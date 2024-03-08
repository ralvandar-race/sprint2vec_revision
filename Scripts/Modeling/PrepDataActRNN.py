import csv
import gzip
import os
import random as rd
import sys
import ast

import _pickle as pkl
import matplotlib.pyplot as plt
import numpy as np

from Utility import Utility


def adjust_length(seqList, length):
    count = 0
    for seq in seqList:
        if len(seq) == 0:
            seq.extend(['<PAD>'] * length)
        elif len(seq) > 0 and len(seq) < length:
            seq.extend(['<PAD>'] * int(length - len(seq)))
        else:
            seqList[count] = seq[:length+1]
        count = count + 1

    return seqList

def tokenize_train(seq_of_act):
    seqList = list()
    noSamples = len(seq_of_act)
    sumL = 0

    # split seq of actions and find max length from avg
    for seq in seq_of_act:
        tok = seq.split()
        sumL = sumL + len(tok)
        tokens = [word for word in tok]
        seqList.append(tokens)
    length = int(sumL/noSamples) + 1
    lengths['train'] = [min(length, len(seq)-1) for seq in seqList]
    
    # fix size for all seq 
    seqList = adjust_length(seqList, length)

    # create dict, convert to seq num, and pad zeros (0s)
    seqDict = {0: '<PAD>', 1: '<UNK>', 2: '<SOS>', 3: '<EOS>'}
    for seq in seqList:
        countS = 0
        for s in seq:
            if s in seqDict.values():
                seq[countS] = list(seqDict.keys())[list(seqDict.values()).index(s)]
            else:
                newInd = len(list(seqDict.keys()))
                seqDict[newInd] = s
                seq[countS] = newInd

            countS = countS + 1

    return length, seqDict, seqList

def tokenize(seq_of_act, length, seq_dict):
    seqList = list()
    
    for seq in seq_of_act:
        tok = seq.split()
        tokens = [word for word in tok]
        seqList.append(tokens)
    ls = [min(length, len(seq)-1) for seq in seqList]

    seqList = adjust_length(seqList, length)

    for seq in seqList:
        countS = 0
        for s in seq:
            if s in seq_dict.values():
                seq[countS] = list(seq_dict.keys())[list(seq_dict.values()).index(s)]
            else:
                # unknown token <UNK>: 1
                seq[countS] = 1
            countS = countS + 1

    return seqList, ls

def prepare_seq(seq_list, lengths):
    no_samples = len(seq_list)

    # create input, next input (output), and mask
    x_en = np.zeros((no_samples, length)).astype('int64') # encoder input
    x_de = np.zeros((no_samples, length)).astype('int64') # decoder input
    y = np.zeros((no_samples, length)).astype('int64') # decoder output
    mask = np.zeros((no_samples, length)).astype('int64') # mask
    for i, s in enumerate(seq_list):
        l = lengths[i]
        if l < 1: 
            continue
        mask[i, :l] = 1
        x_en[i, :l] = s[:l]
        # start of sequence <SOS>: 2
        x_de[i, 0] = 2
        x_de[i, 1:l] = s[:l-1]
        # end of sequence <EOS>: 3
        y[i, :l] = s[1 :l+1]
        y[i, l-1] = 3

    return x_en, x_de, y, mask


try:
    repo = sys.argv[1]
except:
    print("No argument")             
    sys.exit()

# read data
print("Reading data...")
(sprint_train_df, sprint_valid_df, sprint_test_df,
issue_train_df, issue_valid_df, issue_test_df, 
developer_train_df, developer_valid_df, developer_test_df) = Utility.read_prep_dataset(repo)

lengths = {
    'train': list(),
    'valid': list(),
    'test': list()
}

length, seq_dict, train_seq = tokenize_train(developer_train_df['seq_action'].tolist())

print("SeqLength: ", length)
print("train_seq[1]: ", train_seq[1])

valid_seq, lengths['valid'] = tokenize(developer_valid_df['seq_action'].tolist(), length, seq_dict)
print("valid_seq[1]: ", valid_seq[1])

test_seq, lengths['test'] = tokenize(developer_test_df['seq_action'].tolist(), length, seq_dict)
print("test_seq[1]: ", test_seq[1])

x_en_train, x_de_train, y_train, mask_train = prepare_seq(train_seq, lengths['train'])
x_en_valid, x_de_valid, y_valid, mask_valid = prepare_seq(valid_seq, lengths['valid'])
x_en_test, x_de_test, y_test, mask_test = prepare_seq(test_seq, lengths['test'])

# dump data
print("dump data ...")
Utility.dump_prep_dev_act(
    length, seq_dict, \
    x_en_train, x_de_train, y_train, mask_train,\
         x_en_valid, x_de_valid, y_valid, mask_valid, \
            x_en_test, x_de_test, y_test, mask_test, \
                repo)

print("\nlength of x_en_train[1]: ", len(x_en_train[1]))
print("x_en_train[1]: ", x_en_train[1])
print("length of x_de_train[1]: ", len(x_de_train[1]))
print("x_de_train[1]: ", x_de_train[1])
print("length of y_train[1]: ", len(y_train[1]))
print("y_train[1]: ", y_train[1])
print("length of mask_train[1]: ", len(mask_train[1]))
print("mask_train[1]: ", mask_train[1])

print("\nlength of x_en_valid[1]: ", len(x_en_valid[1]))
print("x_en_valid[1]: ", x_en_valid[1])
print("length of x_de_valid[1]: ", len(x_de_valid[1]))
print("x_de_valid[1]: ", x_de_valid[1])
print("length of y_valid[1]: ", len(y_valid[1]))
print("y_valid[1]: ", y_valid[1])
print("length of mask_valid[1]: ", len(mask_valid[1]))
print("mask_valid[1]: ", mask_valid[1])

print("\nlength of x_en_test[1]: ", len(x_en_test[1]))
print("x_en_test[1]: ", x_en_test[1])
print("length of x_de_test[1]: ", len(x_de_test[1]))
print("x_de_test[1]: ", x_de_test[1])
print("length of y_test[1]: ", len(y_test[1]))
print("y_test[1]: ", y_test[1])
print("length of mask_test[1]: ", len(mask_test[1]))
print("mask_test[1]: ", mask_test[1])


print("end for {}".format(repo))