import os, sys

repo = [    
    'apache',
    'jira', 
    'jenkins',
    'spring', 
    'talendforge',
]

for rep in repo:
    print("Running {}".format(rep))
    os.system('python PrepSprintFeatures.py {}'.format(rep))