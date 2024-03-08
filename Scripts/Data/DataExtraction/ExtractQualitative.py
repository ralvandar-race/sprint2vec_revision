import sys
import os
import json
import pymysql
import time
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import operator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.RepoConfig as Repo
import Utility.DBConfig as DB

def main():
    print("Try to add `reopen_ratio` and `qualitative_quality` column ...")
    addColumn = "ALTER TABLE `sprint_feature` ADD `reopen_ratio` FLOAT;"
    try:
        cursor.execute(addColumn)
        connection.commit()
        print("Add columns successfully")
    except:
        print("This repo already has columns")

    time.sleep(3)

    print("\nStart to add value into `reopen_ratio` column ...")
    select = "SELECT board_id, sprint_id, no_reopen, no_issue FROM sprint_feature"
    cursor.execute(select)
    result = cursor.fetchall()
    for row in result:
        try:
            reopenRatio = row['no_reopen']/row['no_issue']
        except:
            reopenRatio = 0.0
        update = "UPDATE sprint_feature SET reopen_ratio = %s WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            reopenRatio,
            row['board_id'],
            row['sprint_id']
        )
        cursor.execute(update, inputPara)
        connection.commit()
       
    print("DONE FOR {}".format(repo.name.upper()))


if __name__ == '__main__':
    repo = Repo.createRepo()
    db = DB.createDB(repo)

    connection = pymysql.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        passwd=db.pwd,
        database=db.repo.name,
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = connection.cursor()   

    main()

    cursor.close()
    connection.close()
    print("DB Connection is closed")