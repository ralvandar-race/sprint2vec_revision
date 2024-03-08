import os, sys
SEED = 0
os.environ['PYTHONHASHSEED'] = str(SEED)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import gzip
import json
import random
import joblib
import _pickle as pkl
import pandas as pd
import numpy as np
import tensorflow as tf
import autokeras as ak
from tensorflow import keras
import keras_tuner as kt
from Utility import Utility, Scaler, Classifier
import warnings

from akregressor import ak_model, init_callbacks

warnings.filterwarnings("ignore", category=UserWarning)

def set_seeds(SEED):
    random.seed(SEED)
    tf.random.set_seed(SEED)
    np.random.seed(SEED)
    keras.utils.set_random_seed(SEED)
    tf.config.experimental.enable_op_determinism()
    os.environ['PYTHONHASHSEED'] = str(SEED)

try:
    repo = sys.argv[1]
    approach_name = sys.argv[2]
    task = sys.argv[3]
except:
    print("No argument")
    sys.exit()

approach = approach_name.split('_')[0]
tuning_objective = "val_mae"


# read data
print("Reading data...")
if approach in ['sprintdev', 'sprint2vecnotext', 'sprint2vec']:
    with open('Act Models/best_config.json', 'r') as f:
        best_act_config = json.load(f)[repo]
    approach_name = "{}_{}_{}_{}".format("_".join(approach_name.split('_')[:-1]), best_act_config['rnn'], best_act_config['dim'], approach_name.split('_')[-1])
train_df, valid_df, test_df = Utility.read_prep_final_dataset(repo, approach_name)
approach_name_clf = "{}_ak".format(approach_name)

# separate x and y
X_train = train_df.drop(['productivity', 'quality_impact'], axis=1)
X_valid = valid_df.drop(['productivity', 'quality_impact'], axis=1)
X_test = test_df.drop(['productivity', 'quality_impact'], axis=1)
y_train = train_df[task]
y_valid = valid_df[task]
y_test = test_df[task]

# ak model
set_seeds(SEED)
input_node, output_node = ak_model()
early_stopping, model_checkpoint, lr_scheduler, tensorboard = init_callbacks(repo, approach, approach_name_clf, task)
objective = kt.Objective(tuning_objective, direction="min")

clf = ak.AutoModel(
    inputs=input_node, 
    outputs=output_node, 
    directory='Regressors/{}/{}/{}'.format(repo, approach, approach_name_clf),
    project_name='{}'.format(task),
    objective=tuning_objective,
    tuner='bayesian',
    seed=SEED,
    max_trials=50,
    max_consecutive_failed_trials=10
)

history = clf.fit(
    X_train.values,
    y_train,
    validation_data=(X_valid.values, y_valid),  
    epochs=200,
    callbacks=[early_stopping, model_checkpoint, tensorboard],
)

# save model
print("Saving model...")
best_model = clf.export_model()
best_model.save('Regressors/{}/{}/{}/{}/best'.format(repo, approach, approach_name_clf, task))

data_dict = {
    'train': {'X': X_train.values, 'y': y_train},
    'valid': {'X': X_valid.values, 'y': y_valid},
    'test': {'X': X_test.values, 'y': y_test}
}

# predict
print("Predicting...")
for data_set in data_dict.keys():
    y_pred = best_model.predict(data_dict[data_set]['X'])
    y_pred = y_pred.reshape(y_pred.shape[0])
    Utility.dump_predictions(data_dict[data_set]['y'].values, y_pred, approach_name_clf, task, data_set, repo)
    Utility.evaluate_performance(data_dict[data_set]['y'].values, y_pred, approach_name_clf, task, data_set, repo)

print("Done\n")