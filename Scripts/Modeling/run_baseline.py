import os, sys

repo = [    
    'apache',
    'jira',
    'jenkins',
    'spring',
    'talendforge'
]

folders = [
    'Regressors',
    'Error',
    'Scalers',
    'Results',
    'Prediction',
    'Prediction Prob'
]

approaches = [
    'averagenoise',
    'random',
    'linear'
]

for f in folders:
    if not os.path.exists(f):
        os.makedirs(f)
    for r in repo:
        if not os.path.exists('{}/{}'.format(f, r)):
            os.makedirs('{}/{}'.format(f, r))
        for app in approaches:
            if not os.path.exists('{}/{}/{}'.format(f, r, app)):
                os.makedirs('{}/{}/{}'.format(f, r, app))

task = [
    'productivity',
    'quality_impact'
]

for rep in repo:
    for t in task:
        for b in approaches:
            print("Running {} {} {}".format(rep, t, b))
            os.system('python baseline.py {} {} {}'.format(rep, t, b))