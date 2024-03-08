import os, sys

repo = [    
    'apache',
    'jira',
    'jenkins',
    'spring',
    'talendforge'
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
    for act in act_type:
        for rnn in rnn_type:
            for dim in act_dim:
                for pool in pooling:
                    print("Running {} {} {} {} {}".format(rep, act, rnn, dim, pool))
                    os.system('python PrepSprint2VecNoText.py {} {} {} {} {}'.format(rep, act, rnn, dim, pool))
                    # os.system('python Experiment.py {} {} {} {} {}'.format(rep, text, act, dim, pool))