import os, sys

repo = [    
    'apache',
    'jira',
    'jenkins',
    'spring',
    'talendforge'
]

text_type = [
    'bow',
    'tfidf',
    'sow2v',
    'bertuncased',
    'bertoverflow',
    'sebert'
]

act_type = [
    'full',
    'last'
]

rnn_type = [
    'lstm',
    'gru'
]

act_dim = [
    '16',
    '32',
    '64'
]

pooling = [
    'mean',
    'max',
    'min'
]

for rep in repo:
    for text in text_type:
        for act in act_type:
            for rnn in rnn_type:
                for dim in act_dim:
                    for pool in pooling:
                        print("Running {} {} {} {} {} {}".format(rep, text, act, rnn, dim, pool))
                        os.system('python PrepSprint2Vec.py {} {} {} {} {} {}'.format(rep, text, act, rnn, dim, pool))
                        # os.system('python Experiment.py {} {} {} {} {}'.format(rep, text, act, dim, pool))