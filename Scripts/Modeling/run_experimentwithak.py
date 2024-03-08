import os, sys
import time
import json

folders = [
    'Regressors',
    'Error',
    'Scalers',
    'Results',
    'Prediction',
    'Prediction Prob'
]

approaches = [
    'existing',
    'onlysprint',
    'onlytabular',
    'sprintissue',
    'sprintdev',
    'sprint2vecnotext',
    'sprint2vec'
]

repo = [    
    'apache',
    'jira', 
    'jenkins',
    'spring', 
    'talendforge',
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

texts = [
    'bow',
    'tfidf',
    'sow2v',
    'bertuncased',
    'bertoverflow',
    'sebert',
]

acts = [
    'full',
    'last'
]

pools = [
    'mean',
    'max',
    'min'
]


# approaches = [
#     'existing',
#     'onlysprint'
# ] + [
#     'onlytabular_{}'.format(pool)
#     for pool in pools
# ] 
# + [
#     'sprintissue_{}_{}'.format(text, pool)
#     for text in texts
#     for pool in pools
# ] + [
#     'sprintdev_{}_{}'.format(act, pool)
#     for act in acts
#     for pool in pools
# ] + [
#     'sprint2vecnotext_{}_{}'.format(act, pool)
#     for act in acts
#     for pool in pools
# ] 

# approaches = [
#     'sprint2vec_{}_{}_{}'.format(text, act, pool)
#     for text in texts
#     for act in acts
#     for pool in pools #"maxabs", "minabs", "sum"
# ]

tasks = [
    'productivity',
    'quality_impact' 
]

start_time = time.time()
for rep in repo:
    for app in approaches:
        for task in tasks:
            print("Running {} {} {}".format(rep, app, task))
            os.system('python ExperimentWithAk.py {} {} {}'.format(rep, app, task))
            print("Total time: {:.2f} seconds".format(time.time() - start_time))
            print("========================================")