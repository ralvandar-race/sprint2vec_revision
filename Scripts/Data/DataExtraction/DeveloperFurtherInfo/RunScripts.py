import datetime
import json
import os
import sys
import time
import pymysql
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.RepoConfig as Repo
import Utility.DBConfig as DB

repo = Repo.createRepo()
db = DB.createDB(repo)

print("\nExtract no_distinct_action ...")
cmd = 'python NoDistinctAction.py {} {} {} {} {}'.format(repo.name, db.host, db.port, db.user, db.pwd)
print('cmd: ', cmd)
os.system(cmd)

print("\nExtract developer_activeness ...")
cmd = 'python Activeness.py {} {} {} {} {}'.format(repo.name, db.host, db.port, db.user, db.pwd)
print('cmd: ', cmd)
os.system(cmd)

print("\nExtract most_prefer_type ...")
cmd = 'python MostPreTypeDev.py {} {} {} {} {}'.format(repo.name, db.host, db.port, db.user, db.pwd)
print('cmd: ', cmd)
os.system(cmd)

print("\nExtract seq_action ...")
cmd = 'python SeqActionIssueType.py {} {} {} {} {}'.format(repo.name, db.host, db.port, db.user, db.pwd)
print('cmd: ', cmd)
os.system(cmd)

print("\nFINISH")
