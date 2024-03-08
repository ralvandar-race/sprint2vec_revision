# updated on 12/13/2021 --> (action, type)

import sys
import json
import pymysql
import re
import os
import datetime
import operator
import time
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo


def extractSeqAction():

    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()

    reList = ['to', 'on', 'of', 'between']
    vowels = ['a', 'e', 'i', 'o', 'u']
    special_cases = ['backward', 'backport', 'complet', 'compat']
    mappings = dict()
    count_dict = dict()
   
    addCol = "ALTER TABLE `sprint_teammember_insight` ADD `seq_action` TEXT NOT NULL AFTER `most_prefer_type`;"
    try:
        cursor.execute(addCol)
        connection.commit()
    except:
        pass

    select = "SELECT board_id, sprint_id, username from sprint_teammember_insight"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        actionSeq = ''
        boardID = row['board_id']
        sprintID = row['sprint_id']
        username = row['username']

        select = """
        SELECT stin.board_id, stin.sprint_id, stin.issue_key, stin.action, stifn.type 
        FROM sprint_teammember_issue_new as stin
        JOIN sprint_teammember_issue_feature_insight_new as stifn
        ON stin.board_id = stifn.board_id and stin.sprint_id = stifn.sprint_id and stin.issue_key = stifn.issue_key
        WHERE stin.board_id = %s and stin.sprint_id = %s and stin.username = %s and stin.exist_in_website = 1
        """
        inputPara = (
            boardID,
            sprintID,
            username
        )
        cursor.execute(select, inputPara)
        result2 = cursor.fetchall()
        # reverse actions (past to present)
        for row2 in list(reversed(result2)):
            raw_action = row2['action'].lower()
            raw_action = raw_action.split(' to ')[0]
            raw_action = raw_action.split(" '")[0]
            raw_action = raw_action.split()
            if raw_action[len(raw_action)-1] in reList:
                del raw_action[len(raw_action) - 1]
            raw_action = [re.sub('[^A-Za-z0-9]+', '',word) for word in raw_action if not word.isdigit() and not word == 'the' and not word == 'one']
            raw_action = [lemmatizer.lemmatize(w) for w in raw_action]
            raw_action = ' '.join([stemmer.stem(w) for w in raw_action])
            raw_type = row2['type'].lower()
            if not "{}:{}".format(raw_action, raw_type) in mappings.keys():
                issue_type = [letter for letter in raw_type if letter not in vowels and letter.isalnum()]
                issue_type = ''.join(issue_type)
                action = ''.join([word[0:5] if word in special_cases else word[:3] for word in raw_action.split()])
                action = action + issue_type
                actionSeq = actionSeq + " " + action
                mappings["{}:{}".format(raw_action, raw_type)] = action
                count_dict["{}:{}".format(raw_action, raw_type)] = 1
            else:
                actionSeq = actionSeq + " " + mappings["{}:{}".format(raw_action, raw_type)]
                count_dict["{}:{}".format(raw_action, raw_type)] += 1
            actionSeq = actionSeq.strip()

        update = "UPDATE sprint_teammember_insight si SET si.seq_action = %s WHERE si.board_id = %s and si.sprint_id = %s and si.username = %s"
        inputPara =(
            actionSeq,
            boardID,
            sprintID,
            username
        )
        cursor.execute(update,inputPara)
        connection.commit()
        print("update {} {} {} into DB successfully".format(boardID, sprintID, username))

if __name__ == '__main__':
    try:
        repo = sys.argv[1]
        host = sys.argv[2]
        port = sys.argv[3]
        user = sys.argv[4]
        pwd = sys.argv[5]
    except:
        print("No argument")
        sys.exit()

    connection = pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=pwd,
        db=repo,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()   
    
    extractSeqAction()

    cursor.close()
    connection.close()
    print("DB Connection is closed")