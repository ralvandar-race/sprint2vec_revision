import os, sys
SEED = 0
os.environ['PYTHONHASHSEED'] = str(SEED)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import _pickle as pkl
import random
import gzip
import json
import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Model, Sequential, Input, models, initializers, optimizers
import tensorflow.keras.backend as K

import keras_tuner as kt

from Utility import Utility
from ActLSTM import MyLSTM, MyRandomSearch, rnn2feature, perplexity, init_callbacks, save_best_model, load_best_model, save_performance
from ActGRU import MyGRU

import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

def set_seeds(SEED):
    random.seed(SEED)
    tf.random.set_seed(SEED)
    np.random.seed(SEED)
    keras.utils.set_random_seed(SEED)
    tf.config.experimental.enable_op_determinism()
    os.environ['PYTHONHASHSEED'] = str(SEED)

# main
try:
    repo = sys.argv[1]
    rnn_type = sys.argv[2]
    output_dim = int(sys.argv[3])
except:
    print("No argument")             
    sys.exit()

print("read data ...")
length, seq_dict, \
    x_en_train, x_de_train, y_train, mask_train, \
        x_en_valid, x_de_valid, y_valid, mask_valid, \
            x_en_test, x_de_test, y_test, mask_test = Utility.read_prep_dev_act(repo)

dict_size = len(seq_dict)
print('Dict size: ', dict_size)

print("init callbacks ...")
early_stopping, model_checkpoint, lr_scheduler, tensorboard = init_callbacks(repo, output_dim, rnn_type)

print("tuning ...")
if rnn_type == 'lstm':
    rnn = MyLSTM(dict_size, length, int(output_dim))
elif rnn_type == 'gru':
    rnn = MyGRU(dict_size, length, int(output_dim))
set_seeds(SEED)
tuner = MyRandomSearch(
    rnn,
    objective=kt.Objective("val_perplexity", direction="min"),
    directory='Act Models/{}/{}/'.format(repo, output_dim),
    project_name='{}'.format(rnn_type),
    max_trials=30,
    executions_per_trial=1,
    seed=SEED,
    # overwrite=True
)

set_seeds(SEED)
tuner.search(
    x=[x_en_train, x_de_train],
    y=y_train,
    epochs=200,
    validation_data=([x_en_valid, x_de_valid], y_valid),
    callbacks=[early_stopping, model_checkpoint, lr_scheduler, tensorboard]
)

print("save best model ...")
best_model = save_best_model(tuner, repo, output_dim, rnn_type)

print("evaluate and feat2vec ..")
best_model = load_best_model(repo, output_dim, rnn_type)
print(best_model.summary())
train_loss, train_ppl = best_model.evaluate([x_en_train, x_de_train], y_train)
valid_loss, valid_ppl = best_model.evaluate([x_en_valid, x_de_valid], y_valid)
test_loss, test_ppl = best_model.evaluate([x_en_test, x_de_test], y_test)
print('Train loss: {}, Train ppl: {}'.format(train_loss, train_ppl))
print('Valid loss: {}, Valid ppl: {}'.format(valid_loss, valid_ppl))
print('Test loss: {}, Test ppl: {}'.format(test_loss, test_ppl))

# dump performance to csv file
save_performance(repo, output_dim, rnn_type, train_loss, train_ppl, valid_loss, valid_ppl, test_loss, test_ppl)

input_layer = best_model.get_layer(name='encoder_inputs')
try:
    encoder_output_layer = best_model.get_layer(name='encoder_{}_2'.format(rnn_type))
except:
    encoder_output_layer = best_model.get_layer(name='encoder_{}_1'.format(rnn_type))
    
get_layer_output = K.function([input_layer.input],
                                [encoder_output_layer.output])
train_layer_output = get_layer_output([x_en_train])[0][0]
valid_layer_output = get_layer_output([x_en_valid])[0][0]
test_layer_output = get_layer_output([x_en_test])[0][0]

train_full_seq = train_layer_output[0]
train_full_seq_feats = rnn2feature(train_full_seq, mask_train)
train_last_hidden = train_layer_output[1]

valid_full_seq = valid_layer_output[0]
valid_full_seq_feats = rnn2feature(valid_full_seq, mask_valid)
valid_last_hidden = valid_layer_output[1]

test_full_seq = test_layer_output[0]
test_full_seq_feats = rnn2feature(test_full_seq, mask_test)
test_last_hidden = test_layer_output[1]

print("shape: ", train_full_seq_feats.shape, valid_full_seq_feats.shape, test_full_seq_feats.shape)

print("dump data ...")
(sprint_train_df, sprint_valid_df, sprint_test_df,
issue_train_df, issue_valid_df, issue_test_df, 
developer_train_df, developer_valid_df, developer_test_df) = Utility.read_prep_dataset(repo)

# drop seq_action column
developer_train_df.drop(columns=['seq_action'], inplace=True)
developer_valid_df.drop(columns=['seq_action'], inplace=True)
developer_test_df.drop(columns=['seq_action'], inplace=True)

developer_train_df['rnn_feats'] = train_full_seq_feats.tolist()
developer_valid_df['rnn_feats'] = valid_full_seq_feats.tolist()
developer_test_df['rnn_feats'] = test_full_seq_feats.tolist()

Utility.dump_prep_act_dataset(
    (sprint_train_df, sprint_valid_df, sprint_test_df,
    issue_train_df, issue_valid_df, issue_test_df,
    developer_train_df, developer_valid_df, developer_test_df),
    repo, "full", rnn_type, output_dim
)

developer_train_df['rnn_feats'] = train_last_hidden.tolist()
developer_valid_df['rnn_feats'] = valid_last_hidden.tolist()
developer_test_df['rnn_feats'] = test_last_hidden.tolist()

Utility.dump_prep_act_dataset(
    (sprint_train_df, sprint_valid_df, sprint_test_df,
    issue_train_df, issue_valid_df, issue_test_df,
    developer_train_df, developer_valid_df, developer_test_df),
    repo, "last", rnn_type, output_dim
)

print("Done for {} {} {}".format(repo, rnn_type, output_dim))