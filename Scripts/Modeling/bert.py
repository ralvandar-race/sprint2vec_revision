import sys
import pandas as pd
import numpy as np
import re
import json
import gzip
import _pickle as pkl
import tensorflow as tf
from transformers import BertTokenizer, TFBertModel

import nltk
from sklearn.feature_extraction.text import CountVectorizer

import stokenizer
import seBERTPreprocessor

from Utility import Utility

try:
    repo = sys.argv[1]
    bert_type = sys.argv[2]
except:
    print("No argument")
    sys.exit()

MAX_LENGTH = 512
OUTPUT_DIM = 768
from_pt = True
config_path = None
do_lower_case = True

if bert_type == "bertuncased":
    tokenizer_name = "bert-base-uncased"
    pretrain_name = "bert-base-uncased"
    from_pt = False
    preprocessor = seBERTPreprocessor.preprocess_sebert
elif bert_type == "bertoverflow":
    tokenizer_name = "Text Models/BERTOverflow"
    pretrain_name = "Text Models/BERTOverflow/pytorch_model.bin"
    config_path = "Text Models/BERTOverflow/config.json"
    do_lower_case = False
    preprocessor = stokenizer.preprocess
if bert_type == "sebert":
    OUTPUT_DIM = 1024
    tokenizer_name = "Text Models/seBERT"
    pretrain_name = "Text Models/seBERT/pytorch_model.bin"
    config_path = "Text Models/seBERT/config.json"
    preprocessor = seBERTPreprocessor.preprocess_sebert


print("loading bert...")
tokenizer = BertTokenizer.from_pretrained(tokenizer_name, do_lower_case=do_lower_case)
bert_embedder = TFBertModel.from_pretrained(pretrain_name, from_pt=from_pt, config=config_path)

def bert_embedding(row):
    """
    Get the embedding of the text using last hidden state
    """
    outputs = bert_embedder(row['text']['input_ids'], row['text']['attention_mask'])
    last_hidden_state = outputs.last_hidden_state
    avg_pool = tf.reduce_mean(last_hidden_state, 1)
    return avg_pool[0].numpy()

# read data
print("Reading data...")
sprint_train_df, sprint_valid_df, sprint_test_df, \
issue_train_df, issue_valid_df, issue_test_df, \
developer_train_df, developer_valid_df, developer_test_df = Utility.read_prep_dataset(repo)

# preprocess text and find text fixed length
print("Preprocessing and Finding text length...")
issue_train_df['text'] = issue_train_df['text'].apply(lambda x: preprocessor(x))
issue_valid_df['text'] = issue_valid_df['text'].apply(lambda x: preprocessor(x))
issue_test_df['text'] = issue_test_df['text'].apply(lambda x: preprocessor(x))
temp_train_df = issue_train_df['text'].apply(lambda x: tokenizer.encode_plus(x, max_length=MAX_LENGTH, padding='max_length', truncation=True, add_special_tokens=False, return_tensors='tf'))
nonzero_count = list()
unk_count = list()
for text in temp_train_df.values:
    nonzero_count.append(np.count_nonzero(text['input_ids'].numpy()[0]))
    unk_count.append(np.count_nonzero(text['input_ids'].numpy()[0] == 1))
nonzero_ratio = [x / MAX_LENGTH for x in nonzero_count]
nonzero_mean = np.mean(nonzero_ratio)
ADJUSTED_LENGTH = round(nonzero_mean*MAX_LENGTH)
print("adjusted length: ", ADJUSTED_LENGTH)
print("[UNK] count: ", sum(unk_count))

print("Tokenize and Embedding...")
for df in [issue_train_df, issue_valid_df, issue_test_df]:
    df['text'] = df['text'].apply(lambda x: tokenizer.encode_plus(x, max_length=ADJUSTED_LENGTH, padding='max_length', truncation=True, add_special_tokens=False, return_tensors='tf'))
    df['text'] = df.apply(lambda row: bert_embedding(row) if row['text']['input_ids'].shape[1] > 0 else np.zeros((OUTPUT_DIM,)), axis=1)

# save vocab
print("saving vocab and adjusted length...")
vocab = tokenizer.get_vocab()
Utility.dump_adj_length_unk_count_and_vocab(ADJUSTED_LENGTH, sum(unk_count), vocab, bert_type, repo)

print("dumping...")
Utility.dump_prep_text_dataset(
    (sprint_train_df, sprint_valid_df, sprint_test_df,
    issue_train_df, issue_valid_df, issue_test_df, 
    developer_train_df, developer_valid_df, developer_test_df),
    repo, bert_type)

print("Done for {} embedding: {}".format(bert_type, repo))