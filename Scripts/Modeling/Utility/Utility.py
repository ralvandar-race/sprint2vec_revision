import sys
import csv
import json
import gzip
import joblib
import pandas as pd
import numpy as np
# if python < 3.8: use pickle5 else use _pickle
if sys.version_info[1] < 8:
    import pickle5 as pkl
else:
    import _pickle as pkl
from sklearn.metrics import mean_squared_error, mean_absolute_error

TASKS = ['productivity', 'quality_impact', 'no_complete', 'no_reopen']

# add for regression
def replace_class_with_ratio(repo, sprint_dict):
    """
    Replace the class of productivity and quality impact with the ratio of complete and reopen issues

    :param repo: The name of the repository
    :param sprint_dict: The dictionary containing the sprint data
    :return: The updated sprint dictionary with the ratio of complete and reopen issues prepared for regression
    """
    sprint_full_df = pd.read_csv('Data/{}_sprint.csv'.format(repo))
    sprint_train_df = sprint_full_df[:sprint_dict['train'].shape[0]]
    sprint_valid_df = sprint_full_df[sprint_dict['train'].shape[0]:sprint_dict['train'].shape[0]+sprint_dict['valid'].shape[0]]
    sprint_test_df = sprint_full_df[sprint_dict['train'].shape[0]+sprint_dict['valid'].shape[0]:]
    sprint_dict['train']['productivity'] = sprint_train_df['complete_ratio']
    sprint_dict['train']['quality_impact'] = sprint_train_df['reopen_ratio']
    sprint_dict['valid']['productivity'] = sprint_valid_df['complete_ratio']
    sprint_dict['valid']['quality_impact'] = sprint_valid_df['reopen_ratio']
    sprint_dict['test']['productivity'] = sprint_test_df['complete_ratio']
    sprint_dict['test']['quality_impact'] = sprint_test_df['reopen_ratio']
    return sprint_dict

def read_raw_dataset(repo):
    """
    Read the raw dataset of the given repository

    :param repo: The name of the repository
    :return: The sprint, issue, and developer dataframes
    """
    sprint_df = pd.read_csv('Data/{}_sprint.csv'.format(repo))
    issue_df = pd.read_csv('Data/{}_issue.csv'.format(repo))
    developer_df = pd.read_csv('Data/{}_developer.csv'.format(repo))
    return sprint_df, issue_df, developer_df

def dump_prep_dataset(repo, dataset):
    """
    Dump the preprocessed dataset into a pickle file compressed with gzip
    
    :param repo: The name of the repository
    :param dataset: The preprocessed dataset
    """
    file_name = "Data/Preprocessed/{}.pkl.gz".format(repo)
    with gzip.open(file_name, "wb") as f:
        pkl.dump(dataset, f, -1)

def read_prep_dataset(repo):
    """
    Read the preprocessed dataset from a pickle file compressed with gzip
        
    :param repo: The name of the repository
    :return: The preprocessed dataset
    """
    file_name = "Data/Preprocessed/{}.pkl.gz".format(repo)
    with gzip.open(file_name, "rb") as f:
        return pkl.load(f)

def dump_prep_text_dataset(data_df, repo, text_type):
    """
    Dump the preprocessed text dataset into a pickle file compressed with gzip

    :param data_df: The preprocessed text dataset
    :param repo: The name of the repository
    :param text_type: The type of text data (e.g., bow, tfidf, ..)
    """
    file_name = "Data/Preprocessed_Text/{}_{}.pkl.gz".format(repo, text_type)
    with gzip.open(file_name, "wb") as f:
        pkl.dump(data_df, f, -1)
                
def read_prep_text_dataset(repo, text_type):
    """
    Read the preprocessed text dataset from a pickle file compressed with gzip
    
    :param repo: The name of the repository
    :param text_type: The type of text data (e.g., bow, tfidf, ..)
    :return: The preprocessed text dataset
    """
    file_name = "Data/Preprocessed_Text/{}_{}.pkl.gz".format(repo, text_type)
    with gzip.open(file_name, "rb") as f:
        return pkl.load(f)

def read_prep_act_dataset(repo, act_type, rnn_type, act_dim):
    """
    Read the preprocessed action dataset from a pickle file compressed with gzip

    :param repo: The name of the repository
    :param act_type: The type of action data (e.g., full, last)
    :param rnn_type: The type of RNN model (e.g., lstm, gru)
    :param act_dim: The dimension of the action data
    :return: The preprocessed action dataset
    """
    file_name = "Data/Preprocessed_Act/{}_{}_{}_{}.pkl.gz".format(repo, act_type, rnn_type, act_dim)
    with gzip.open(file_name, "rb") as f:
        return pkl.load(f)

def dump_prep_act_dataset(data_df, repo, act_type, rnn_type, act_dim):
    """
    Dump the preprocessed action dataset into a pickle file compressed with gzip

    :param data_df: The preprocessed action dataset
    :param repo: The name of the repository
    :param act_type: The type of action data (e.g., full, last)
    :param rnn_type: The type of RNN model (e.g., lstm, gru)
    :param act_dim: The dimension of the action data
    """
    file_name = "Data/Preprocessed_Act/{}_{}_{}_{}.pkl.gz".format(repo, act_type, rnn_type, act_dim)
    with gzip.open(file_name, "wb") as f:
        pkl.dump(data_df, f, -1)

def dump_prep_final_dataset(data_df, approach_path):
    """
    Dump the preprocessed final dataset into a csv file compressed with gzip

    final dataset means the dataset that has been gone through the feature extraction process (e.g., sprint2vec, ...), ready to used for modeling

    :param data_df: The preprocessed final dataset
    :param approach_path: The name of the approach
    """
    data_df.to_csv("Data/Preprocessed/{}.csv.gz".format(approach_path), index=False, compression='gzip')

def dump_prep_final_mora_and_shihab_dataset(data_df, approach_path):
    """
    Dump the preprocessed final dataset for Mora (i.e., existing approach for num complete issues) 
    and Shihab approach (i.e., existing approach for num reopened issues) into two csv files compressed with gzip

    :param data_df: The preprocessed final dataset
    :param approach_path: The name of the approach
    """
    data_df[0].to_csv("Data/Preprocessed/sprint_{}.csv.gz".format(approach_path), index=False, compression='gzip')
    data_df[1].to_csv("Data/Preprocessed/issue_{}.csv.gz".format(approach_path), index=False, compression='gzip')
    
def read_prep_final_dataset(repo, approach_name):
    """
    Read the preprocessed final dataset from a csv file compressed with gzip

    final dataset means the dataset that has been gone through the feature extraction process (e.g., sprint2vec, ...), ready to used for modeling
    
    :param repo: The name of the repository
    :param approach_name: The name of the approach
    :return: The preprocessed final dataset of sprint (train, valid, test)
    """
    train_df = pd.read_csv("Data/Preprocessed/{}_{}_train.csv.gz".format(repo, approach_name), compression='gzip')
    valid_df = pd.read_csv("Data/Preprocessed/{}_{}_valid.csv.gz".format(repo, approach_name), compression='gzip')
    test_df = pd.read_csv("Data/Preprocessed/{}_{}_test.csv.gz".format(repo, approach_name), compression='gzip')
    return train_df, valid_df, test_df

def read_prep_final_mora_and_shihab_dataset(repo, approach_name):
    """
    Read the preprocessed final dataset for Mora (i.e., existing approach for num complete issues)
    and Shihab approach (i.e., existing approach for num reopened issues) from two csv files compressed with gzip
    
    :param repo: The name of the repository
    :param approach_name: The name of the approach
    :return: The preprocessed final dataset of sprint (train, valid, test) and issue (train, valid, test)
    """
    sprint_train_df = pd.read_csv("Data/Preprocessed/sprint_{}_{}_train.csv.gz".format(repo, approach_name), compression='gzip')
    sprint_valid_df = pd.read_csv("Data/Preprocessed/sprint_{}_{}_valid.csv.gz".format(repo, approach_name), compression='gzip')
    sprint_test_df = pd.read_csv("Data/Preprocessed/sprint_{}_{}_test.csv.gz".format(repo, approach_name), compression='gzip')
    issue_train_df = pd.read_csv("Data/Preprocessed/issue_{}_{}_train.csv.gz".format(repo, approach_name), compression='gzip')
    issue_valid_df = pd.read_csv("Data/Preprocessed/issue_{}_{}_valid.csv.gz".format(repo, approach_name), compression='gzip')
    issue_test_df = pd.read_csv("Data/Preprocessed/issue_{}_{}_test.csv.gz".format(repo, approach_name), compression='gzip')
    return sprint_train_df, sprint_valid_df, sprint_test_df, issue_train_df, issue_valid_df, issue_test_df

def dump_vocab_and_vectorizer(vocab, vectorizer, text_type, repo):
    """
    Dump the vocabulary and vectorizer into json and joblib files
    
    :param vocab: The vocabulary
    :param vectorizer: The vectorizer
    :param text_type: The type of text data (e.g., bow, tfidf)
    :param repo: The name of the repository
    """
    vocab_path = 'Text Models/{}_{}_vocab.json'.format(repo, text_type)
    with open(vocab_path, 'w') as f:
        json.dump(vocab, f, indent=4)
    vectorizer_path = 'Text Models/{}_{}.joblib'.format(repo, text_type)
    joblib.dump(vectorizer, vectorizer_path)

def dump_adj_length_unk_count_and_vocab(adjusted_length, unk_count, vocab, bert_type, repo):
    """
    Dump the adjusted length, unknown count, and vocabulary into text and json files
    
    :param adjusted_length: The adjusted length
    :param unk_count: The unknown count
    :param vocab: The vocabulary
    :param bert_type: The type of BERT model (e.g., bertoverflow, bertuncased, sebert)
    :param repo: The name of the repository
    """
    with open('Text Models/{}_{}_adjusted_length.txt'.format(repo, bert_type), 'w') as f:
        f.write(str(adjusted_length))
    with open('Text Models/{}_{}_unk_count.txt'.format(repo, bert_type), 'w') as f:
        f.write(str(unk_count))
    with open('Text Models/{}_vocab.json'.format(bert_type), 'w') as f:
        json.dump(vocab, f, indent=4)

def dump_prep_dev_act(length, seq_dict, x_en_train, x_de_train, y_train, mask_train, x_en_valid, x_de_valid, y_valid, mask_valid, x_en_test, x_de_test, y_test, mask_test, repo):
    """
    Dump the preprocessed developer action dataset into text, json, and npz files
    
    :param length: The length of the sequence
    :param seq_dict: The dictionary containing the sequence data
    :param x_en_train: The encoder input of the training set
    :param x_de_train: The decoder input of the training set
    :param y_train: The target of the training set
    :param mask_train: The mask of the training set
    :param x_en_valid: The encoder input of the validation set
    :param x_de_valid: The decoder input of the validation set
    :param y_valid: The target of the validation set
    :param mask_valid: The mask of the validation set
    :param x_en_test: The encoder input of the test set
    :param x_de_test: The decoder input of the test set
    :param y_test: The target of the test set
    :param mask_test: The mask of the test set
    :param repo: The name of the repository
    """
    # save length as text file
    with open('Data/Seq Actions/{}_length.txt'.format(repo), 'w') as f:
        f.write(str(length))
    # save seq_dict as json file
    with open('Data/Seq Actions/{}_seq_dict.json'.format(repo), 'w') as f:
        json.dump(seq_dict, f, indent=4)
    np.savez('Data/Seq Actions/{}_x_en_train.npz'.format(repo), x_en_train)
    np.savez('Data/Seq Actions/{}_x_de_train.npz'.format(repo), x_de_train)
    np.savez('Data/Seq Actions/{}_y_train.npz'.format(repo), y_train)
    np.savez('Data/Seq Actions/{}_mask_train.npz'.format(repo), mask_train)
    np.savez('Data/Seq Actions/{}_x_en_valid.npz'.format(repo), x_en_valid)
    np.savez('Data/Seq Actions/{}_x_de_valid.npz'.format(repo), x_de_valid)
    np.savez('Data/Seq Actions/{}_y_valid.npz'.format(repo), y_valid)
    np.savez('Data/Seq Actions/{}_mask_valid.npz'.format(repo), mask_valid)
    np.savez('Data/Seq Actions/{}_x_en_test.npz'.format(repo), x_en_test)
    np.savez('Data/Seq Actions/{}_x_de_test.npz'.format(repo), x_de_test)
    np.savez('Data/Seq Actions/{}_y_test.npz'.format(repo), y_test)
    np.savez('Data/Seq Actions/{}_mask_test.npz'.format(repo), mask_test)

def read_prep_dev_act(repo):
    """
    Read the preprocessed developer action dataset from text, json, and npz files
    
    :param repo: The name of the repository
    :return: The length, sequence dictionary, encoder input, decoder input, target, and mask of the training, validation, and test sets
    """
    with open('Data/Seq Actions/{}_length.txt'.format(repo), 'r') as f:
        length = int(f.read())
    with open('Data/Seq Actions/{}_seq_dict.json'.format(repo), 'r') as f:
        seq_dict = json.load(f)
    x_en_train = np.load('Data/Seq Actions/{}_x_en_train.npz'.format(repo))['arr_0']
    x_de_train = np.load('Data/Seq Actions/{}_x_de_train.npz'.format(repo))['arr_0']
    y_train = np.load('Data/Seq Actions/{}_y_train.npz'.format(repo))['arr_0']
    mask_train = np.load('Data/Seq Actions/{}_mask_train.npz'.format(repo))['arr_0']
    x_en_valid = np.load('Data/Seq Actions/{}_x_en_valid.npz'.format(repo))['arr_0']
    x_de_valid = np.load('Data/Seq Actions/{}_x_de_valid.npz'.format(repo))['arr_0']
    y_valid = np.load('Data/Seq Actions/{}_y_valid.npz'.format(repo))['arr_0']
    mask_valid = np.load('Data/Seq Actions/{}_mask_valid.npz'.format(repo))['arr_0']
    x_en_test = np.load('Data/Seq Actions/{}_x_en_test.npz'.format(repo))['arr_0']
    x_de_test = np.load('Data/Seq Actions/{}_x_de_test.npz'.format(repo))['arr_0']
    y_test = np.load('Data/Seq Actions/{}_y_test.npz'.format(repo))['arr_0']
    mask_test = np.load('Data/Seq Actions/{}_mask_test.npz'.format(repo))['arr_0']
    return length, seq_dict, x_en_train, x_de_train, y_train, mask_train, x_en_valid, x_de_valid, y_valid, mask_valid, x_en_test, x_de_test, y_test, mask_test

def dump_predictions(true_value, predictions, approach, task, data_set, repo):
    """
    Dump the true value and predictions into a tsv file
    
    :param true_value: The true values
    :param predictions: The predictions
    :param approach: The name of the approach
    :param task: The task (e.g., productivity, quality_impact, no_complete, no_reopen)
    :param data_set: The dataset (e.g., train, valid, test)
    :param repo: The name of the repository
    """
    preds = [true_value, predictions]
    zipped = zip(*preds)
    file_path = "Prediction/{}/{}/{}_{}_{}_{}.csv".format(repo, approach.split('_')[0], approach, task, data_set, repo)
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(zipped)

def dump_prob_predictions(prob, approach, task, data_set, repo):
    """
    Dump the predicted probabilities into a tsv file
    
    :param prob: The predicted probabilities
    :param approach: The name of the approach
    :param task: The task (e.g., productivity, quality_impact, no_complete, no_reopen)
    :param data_set: The dataset (e.g., train, valid, test)
    :param repo: The name of the repository
    """
    zipedPredictedResult = zip(*np.array(prob).T)
    file_path = "Prediction Prob/{}/{}/{}_{}_{}_{}.csv".format(repo, approach.split('_')[0], approach, task, data_set, repo)
    with open(file_path, 'w', newline='') as predicedFile:
        wr = csv.writer(predicedFile, delimiter='\t')
        wr.writerows(zipedPredictedResult)

def evaluate_performance(true_value, predictions, approach, task, data_set, repo):
    """
    Evaluate the performance of the model, including MAE, MSE, and RMSE, based on the true value and predictions
    And, dump the raw and absolute errors into text files, and the evaluation results into a csv file
        
    :param true_value: The true values
    :param predictions: The predictions
    :param approach: The name of the approach
    :param task: The task (e.g., productivity, quality_impact, no_complete, no_reopen)
    :param data_set: The dataset (e.g., train, valid, test)
    :param repo: The name of the repository
    """
    raw_path = 'Error/{}/{}/{}_{}_{}_{}_raw.txt'.format(repo, approach.split('_')[0], approach, task, data_set, repo)
    preds = [true_value, predictions]
    zipped = zip(*preds)
    with open(raw_path, 'w', newline='') as f:
        for line in zipped:
            raw_error = line[0] - line[1]
            f.write(str(raw_error))
            f.write('\n')
    abs_path = 'Error/{}/{}/{}_{}_{}_{}_abs.txt'.format(repo, approach.split('_')[0], approach, task, data_set, repo)
    zipped = zip(*preds)
    with open(abs_path, 'w', newline='') as f:
        for line in zipped:
            abs_error = abs(line[0] - line[1])
            f.write(str(abs_error))
            f.write('\n')
    mae = mean_absolute_error(true_value, predictions)
    mse = mean_squared_error(true_value, predictions)
    rmse = mean_squared_error(true_value, predictions, squared=False)

    result_df = pd.DataFrame({
        'mae': [mae],
        'mse': [mse],
        'rmse': [rmse],
    })

    result_path = 'Results/{}/{}/{}_{}_{}_{}.csv'.format(repo, approach.split('_')[0], approach, task, data_set, repo)
    result_df.to_csv(result_path, index=False)

    print("{} {}:{:.4f}".format(data_set, task, mae))