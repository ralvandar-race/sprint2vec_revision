import os, sys

# ignore UserWarnings
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

repo = [    
    'apache',
    'jira', 
    'jenkins',
    'spring', 
    'talendforge',
]

for rep in repo:
    print("\nRunning {}".format(rep))
    os.system('python LoadData.py {}'.format(rep))
    os.system('python SplitData.py {}'.format(rep))
    os.system('python PreprocessData.py {}'.format(rep))