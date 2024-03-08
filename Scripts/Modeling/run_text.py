import os, sys

# ignore future warnings, user warnings
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

text_type = [
    'bow', 
    'tfidf', 
    'sow2v'
]

for rep in repo:
    for text in text_type:
        print("Running {}".format(rep))
        os.system('python {}.py {}'.format(text, rep))

emb_type = [
    'bertuncased',
    'bertoverflow',
    'sebert',
]

for rep in repo:
    for emb in emb_type:
        print("Running {}".format(rep))
        os.system('python bert.py {} {}'.format(rep, emb))
