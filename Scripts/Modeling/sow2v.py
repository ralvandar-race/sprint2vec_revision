import sys
import pandas as pd
import numpy as np
import gzip
import json
import _pickle as pkl

import string
import pandas as pd
import numpy as np

import re
import nltk
from nltk.corpus import stopwords

from gensim.models.keyedvectors import KeyedVectors

from Utility import Utility

try:
    repo = sys.argv[1]
except:
    print("No argument")
    sys.exit()

text_type = "sow2v"
DEFAULT_DIM = 200

print("Loading pretrained word2vec model...")
pretrained_model = "Text Models/SOw2v/SO_vectors_200.bin"
word_vect = KeyedVectors.load_word2vec_format(pretrained_model, binary=True)

stop_words = set(nltk.corpus.stopwords.words('english'))
tokenizer = nltk.tokenize.ToktokTokenizer()

# read data
print("Reading data...")
sprint_train_df, sprint_valid_df, sprint_test_df, \
issue_train_df, issue_valid_df, issue_test_df, \
developer_train_df, developer_valid_df, developer_test_df = Utility.read_prep_dataset(repo)

def preprocess(text):
    # remove code snippets
    text = text.lower()
    text = re.sub(r'[\n\r\t]', ' ', text)
    html_code_pattern = re.compile(r'<code>.*?</code>', re.DOTALL)
    other_code_pattern = re.compile(r'{code}.*?{code}', re.DOTALL)
    markdown_code_pattern = re.compile(r'```.*?```', re.DOTALL)
    text = re.sub(html_code_pattern, ' ', text)
    text = re.sub(markdown_code_pattern, ' ', text)
    text = re.sub(other_code_pattern, ' ', text)

    # remove HTML tags
    html_tag_pattern = re.compile(r'<.*?>')
    text = re.sub(html_tag_pattern, ' ', text)

    pattern = re.compile(r'[^\w\s\+\#\-\\\_\/]', re.UNICODE)
    text = re.sub(pattern, ' ', text)

    # remove stop words
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens if token.strip() not in stop_words]

    text = re.sub(r'\s+', ' ', ' '.join(tokens))
    
    return text

matching_vocab = dict()
unmatching_vocab = dict()
length = dict()

def embed_text(text):
    """
    Embed the text
    
    :param text: the text to be embedded
    """
    tokens = text.split()
    length[len(tokens)] = length.get(len(tokens), 0) + 1
    if text == '':
        return np.zeros(DEFAULT_DIM)
    vectors = []
    for token in tokens:
        try:
            # if token in word_vect:
            vectors.append(word_vect[token])
            if token in matching_vocab:
                matching_vocab[token] += 1
            else:
                matching_vocab[token] = 1
        except:
            # append zero vector if token not in word_vect
            vectors.append(np.zeros(DEFAULT_DIM))
            if token in unmatching_vocab:
                unmatching_vocab[token] += 1
            else:
                unmatching_vocab[token] = 1
    vectors = np.array(vectors)
    vectors = np.mean(vectors, axis=0)
    return vectors

print("Tokenizing and Embedding...")
for df in [issue_train_df, issue_valid_df, issue_test_df]:
    df['text'] = df['text'].apply(lambda x: preprocess(x))
    df['text'] = df['text'].apply(lambda x: embed_text(x))

# dump vocab as json file 
print("Dumping vocab...")
vocab = word_vect.key_to_index
with open('Text Models/{}_vocab.json'.format(text_type), 'w') as f:
    json.dump(vocab, f, indent=4)

length = dict(sorted(length.items(), key=lambda item: item[1], reverse=True))
with open('Text Models/{}_{}_length.json'.format(repo, text_type), 'w') as f:
    json.dump(length, f, indent=4)

print("Dumping dataset...")
Utility.dump_prep_text_dataset(
    (sprint_train_df, sprint_valid_df, sprint_test_df,
    issue_train_df, issue_valid_df, issue_test_df, 
    developer_train_df, developer_valid_df, developer_test_df),
    repo, text_type)

print("Done for {} embedding: {}".format(text_type, repo))