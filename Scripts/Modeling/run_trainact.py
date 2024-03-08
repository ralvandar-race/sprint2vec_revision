import os, sys

repo = [    
    'apache', 
    'jira',  
    'jenkins', 
    'spring', 
    'talendforge',
]

rnn_type = [
    'gru', 
    'lstm', 
]

output_dim = [
    16, 
    32, 
    64
]

for rep in repo:
    print("\nREPO: {}".format(rep))
    os.system('python PrepDataActRNN.py {}'.format(rep))
    for rnn in rnn_type:
        for dim in output_dim:
            print("\nRNN: {}, DIM: {}".format(rnn, dim))
            print("Running TrainActRNN.py {} {} {}".format(rep, rnn, dim))
            os.system('python TrainActRNN.py {} {} {}'.format(rep, rnn, dim))