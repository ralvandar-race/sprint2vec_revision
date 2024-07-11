import pandas as pd
import numpy as np
import gzip
import re
import sys
import json
import joblib
# import pickle5 as pkl
import _pickle as pkl
import string
import nltk
nltk.download('stopwords')
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from Utility import Utility

try:
    repo = sys.argv[1]
except:
    print("No argument")
    sys.exit()

text_type = "tfidf"

punctuations = string.punctuation + string.digits + "’" + "”"
stop_words = set(nltk.corpus.stopwords.words('english'))
alphabet_string = string.ascii_lowercase
alphabet_list = list(alphabet_string)
tokenizer = nltk.tokenize.ToktokTokenizer()

def strip_list_noempty(lst):
    new_list = (item.strip() if hasattr(item, 'strip') else item for item in lst)
    return [item for item in new_list if item != '']

def clean_punctuation(text): 
    """
    Remove punctuation from text
    
    Args:
    text: string
    """
    tokens = tokenizer.tokenize(text)
    punctuation_filtered = []
    regex = re.compile('[%s]' % re.escape(punctuations))
    for token in tokens:
        punctuation_filtered.append(regex.sub(' ', token))
    filtered_list = strip_list_noempty(punctuation_filtered)
    return ' '.join(map(str, filtered_list))

def clean_text(text):
    # lower
    text = text.lower()
    # Remove HTML tags
    text = re.sub('<.*?>', ' ', text)  
    # Remove URLs
    text = re.sub(r'http\S+', 'url', text)  
    # remove files and subtitute with word 'file'
    text = re.sub(r'file\s*\S+', 'file', text)
    # remove code
    html_code_pattern = re.compile(r'<code>.*?</code>', re.DOTALL)
    other_code_pattern = re.compile(r'{code}.*?{code}', re.DOTALL)
    markdown_code_pattern = re.compile(r'```.*?```', re.DOTALL)
    text = re.sub(html_code_pattern, 'code', text)
    text = re.sub(markdown_code_pattern, 'code', text)
    text = re.sub(other_code_pattern, 'code', text)
    # remove hashes
    hash_pattern = re.compile(r'\b(?:[a-fA-F0-9]{7,})\b')
    text = re.sub(hash_pattern, '', text)
    # remove special jira format
    text = re.sub(r'\[[\w\s]+-\d+\]', '', text)
    # remove control characters (newline, carriage return, tab)
    text = re.sub(re.compile('[\n\r\t]'), ' ', text)
    # remove '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    text = clean_punctuation(text)
    # replace any sequence of 2 or more spaces with a single space
    text = re.sub(re.compile('\s{2,}'), ' ', text).strip()
    # remove stop words and remove single character
    text = ' '.join([token for token in tokenizer.tokenize(text) if token not in stop_words and token not in alphabet_list])
    return text


# read data
print("Reading data...")
sprint_train_df, sprint_valid_df, sprint_test_df, \
issue_train_df, issue_valid_df, issue_test_df, \
developer_train_df, developer_valid_df, developer_test_df = Utility.read_prep_dataset(repo)

# clean text
for df in [issue_train_df, issue_valid_df, issue_test_df]:
    df['text'] = df['text'].apply(lambda x: clean_text(x))

# find optimal min_df
start_min_df = 1
end_min_df = int(issue_train_df[issue_train_df['text'] != ''].shape[0] * 0.1)
num_empty_train = issue_train_df[issue_train_df['text'] == ''].shape[0]

while start_min_df < end_min_df:
    mid_min_df = (start_min_df + end_min_df) // 2
    bow = CountVectorizer(max_features=None, lowercase=True, min_df=mid_min_df)
    bow.fit(issue_train_df['text'])
    issue_train_bow = bow.transform(issue_train_df['text'])
    num_empty_bow_train = len(np.where(~issue_train_bow.toarray().any(axis=1))[0])
    
    if num_empty_bow_train <= num_empty_train:
        start_min_df = mid_min_df + 1
    else:
        end_min_df = mid_min_df

result_min_df = start_min_df - 1
final_tfidf = TfidfVectorizer(max_features=None, lowercase=True, min_df=result_min_df)
final_tfidf.fit(issue_train_df['text'])
issue_train_tfidf = final_tfidf.transform(issue_train_df['text'])
issue_valid_tfidf = final_tfidf.transform(issue_valid_df['text'])
issue_test_tfidf = final_tfidf.transform(issue_test_df['text'])
issue_train_df['text'] = issue_train_tfidf.toarray().tolist()
issue_valid_df['text'] = issue_valid_tfidf.toarray().tolist()
issue_test_df['text'] = issue_test_tfidf.toarray().tolist()

print("Optimal min_df:", result_min_df)
print("Max Features:", len(final_tfidf.vocabulary_))

vocab = final_tfidf.vocabulary_
train_word_list = final_tfidf.get_feature_names()
word_count_dict = {word: int(count) for word, count in zip(train_word_list, issue_train_tfidf.toarray().sum(axis=0))}
vocab_word_count_dict = {vocab[word]: {'word': word, 'count': count} for word, count in word_count_dict.items()}

# dump vocab and tfidf
Utility.dump_vocab_and_vectorizer(vocab_word_count_dict, final_tfidf, text_type, repo)

# save data
Utility.dump_prep_text_dataset(
    (sprint_train_df, sprint_valid_df, sprint_test_df,
    issue_train_df, issue_valid_df, issue_test_df, 
    developer_train_df, developer_valid_df, developer_test_df),
    repo, text_type)
             
print("TFIDF Done for {}".format(repo))