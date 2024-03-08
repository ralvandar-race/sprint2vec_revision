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


pooling = [
    'mean',
    'max',
    'min'
]

for rep in repo:
    for text in text_type:
        for pool in pooling:
            print("Running {} {} {}".format(rep, text, pool))
            os.system('python PrepSprintIssue.py {} {} {}'.format(rep, text, pool))