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

print("\nExtract no_issue_sdate ...")
cmd = 'python NoIssue.py {} {} {} {} {}'.format(db.host, db.port, db.user, db.pwd, db.repo.name)
print('cmd: ', cmd)
os.system(cmd)

print("\nExtract no_teammember_sdate ...")
cmd = 'python NoTeammember.py {} {} {} {} {}'.format(db.host, db.port, db.user, db.pwd, db.repo.name)
print('cmd: ', cmd)
os.system(cmd)

print("\nExtract no_completed_issue ...")
cmd = 'python NoCompletedIssue.py {} {} {} {} {}'.format(db.host, db.port, db.user, db.pwd, db.repo.name)
print('cmd: ', cmd)
os.system(cmd)

print("\nFINISH")
