import os, sys
import random
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

from Utility import Utility

SEED = 0

def set_seeds(SEED):
    random.seed(SEED)
    np.random.seed(SEED)
    os.environ['PYTHONHASHSEED'] = str(SEED)

try:
    repo = sys.argv[1]
    task = sys.argv[2]
    approach = sys.argv[3]
except:
    print("No argument")
    sys.exit()

def average_with_random_nosie_model(train, test):
    prediction = np.mean(train)
    sd = np.std(train)
    set_seeds(SEED)
    noise = np.random.normal(0, sd, len(test))
    predicted = [prediction + noise[i] for i in range(len(test))]
    return predicted

def random_model(train, test):
    set_seeds(SEED)
    possible_values = list(train)
    predicted = [random.choice(possible_values) for i in range(len(test))]
    return predicted

def linear_regression_model(x, y):
    model = LinearRegression()
    model.fit(x, y)
    return model

baseline_dict = {
    'averagenoise': average_with_random_nosie_model,
    'random': random_model,
    'linear': linear_regression_model
}


# read data
print("Reading data...")
train_df, valid_df, test_df = Utility.read_prep_final_dataset(repo, "onlysprint")

x_train = train_df.drop(['productivity', 'quality_impact'], axis=1)
x_valid = valid_df.drop(['productivity', 'quality_impact'], axis=1)
x_test = test_df.drop(['productivity', 'quality_impact'], axis=1)

y_train = train_df[task].values.tolist()
y_valid = valid_df[task].values.tolist()
y_test = test_df[task].values.tolist()

if approach == 'linear':
    linear_model = baseline_dict[approach](x_train, y_train)
    print("Saving model...")
    joblib.dump(linear_model, 'Regressors/{}/{}/{}_best.joblib'.format(repo, approach, task))


data_dict = {
    'train': {'x': x_train, 'y': y_train},
    'valid': {'x': x_valid, 'y': y_valid},
    'test': {'x': x_test, 'y': y_test}
}

for data_set in data_dict.keys():
    if approach == 'linear':
        y_pred = linear_model.predict(data_dict[data_set]['x'])
    else:
        y_pred = baseline_dict[approach](data_dict["train"]['y'], data_dict[data_set]['y'])
    Utility.dump_predictions(data_dict[data_set]['y'], y_pred, approach, task, data_set, repo)
    Utility.evaluate_performance(data_dict[data_set]['y'], y_pred, approach, task, data_set, repo)