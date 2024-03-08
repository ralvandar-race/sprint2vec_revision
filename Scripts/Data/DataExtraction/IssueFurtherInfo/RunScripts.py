import datetime
import json
import os
import sys
import time
import pymysql
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.RepoConfig as Repo


repo = Repo.createRepo()

print("\nExtract change_priority ...")
cmd = 'python NoChangePrior.py {}'.format(repo.name)
print('cmd: ', cmd)
os.system(cmd)

print("\nExtract no_comment ...")
cmd = 'python NoComment.py {}'.format(repo.name)
print('cmd: ', cmd)
os.system(cmd)

print("\nExtract reopen_status ...")
cmd = 'python ReopenStatus.py {}'.format(repo.name)
print('cmd: ', cmd)
os.system(cmd)

print("\nFINISH")
