import os, sys

repo = [    
    'apache',
    'jira', 
    'jenkins',
    'spring', 
    'talendforge'
]

pooling = [
    'mean',
    'max',
    'min'
]

for rep in repo:
    for pool in pooling:
        print("Running {} {}".format(rep, pool))
        os.system('python PrepTabularFeatures.py {} {}'.format(rep, pool))