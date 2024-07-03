import pymysql
import sys
import os
import requests
import json
import time
from datetime import datetime
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.JSONUtility as Utility
import Utility.DBConfig as DB
import Utility.RepoConfig as Repo

def getIssueFromSprint():
    """
    Collect Issues from Sprint
    """
    print("Collect Issues from Sprint...")
    
    select = "SELECT board_id, sprint_id FROM sprint_feature"
    cursor.execute(select)
    result = cursor.fetchall()

    countIssue = 0
    for row in result:
        boardID = str(row['board_id'])
        sprintID = str(row['sprint_id'])
        sprint = Utility.loadSprintJSON(boardID, sprintID, repo.name, db.folder)
        try:
            contents = sprint['contents']
        except Exception as e:
            print("ERROR: {} [boardID: {}, sprintID: {}]".format(e, boardID, sprintID))
            continue

        # collect the completed issues during the sprint
        completedIssueList = contents['completedIssues']
        for issue in completedIssueList:
            issueKey = issue['key']
            # collectAll(issueKey, db.folder)    # add
            try:
                insertIssue = "INSERT INTO sprint_issue(id, board_id, sprint_id, issue_key, state, addedDuringSprint, exist_in_website, collectedTime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
                inputPara = (
                    str(countIssue),
                    boardID,
                    sprintID,
                    issueKey,
                    "Completed",
                    False,
                    0,
                    datetime.now()
                ) 
                cursor.execute(insertIssue, inputPara)
                connection.commit()
                print("\r\nRecord '{}' [{}] inserted successfully into DB".format(countIssue, issue['key']))
                
                countIssue += 1
            except pymysql.Error as e:
                print("ERROR: {}".format(e))

        # collect the incompleted issues during the sprint
        incompletedIssueList = contents['issuesNotCompletedInCurrentSprint']
        for issue in incompletedIssueList:
            issueKey = issue['key']
            collectAll(issueKey, db.folder) 
            try:
                insertIssue = "INSERT INTO sprint_issue(id, board_id, sprint_id, issue_key, state, addedDuringSprint, exist_in_website, collectedTime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
                inputPara = (
                    str(countIssue),
                    boardID,
                    sprintID,
                    issueKey,
                    "Incompleted in current sprint",
                    False,
                    0,
                    datetime.now()
                ) 
                cursor.execute(insertIssue, inputPara)
                connection.commit()
                print("\r\nRecord '{}' [{}] inserted successfully into DB".format(countIssue, issue['key']))
                
                countIssue += 1
            except pymysql.Error as e:
                print("ERROR: {}".format(e))

        # collect the punted issues during the sprint
        puntedIssueList = contents['puntedIssues']
        for issue in puntedIssueList:
            issueKey = issue['key']
            collectAll(issueKey, db.folder)
            try:
                insertIssue = "INSERT INTO sprint_issue(id, board_id, sprint_id, issue_key, state, addedDuringSprint, exist_in_website, collectedTime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
                inputPara = (
                    str(countIssue),
                    boardID,
                    sprintID,
                    issueKey,
                    "Punted",
                    False,
                    0,
                    datetime.now()
                ) 
                cursor.execute(insertIssue, inputPara)
                connection.commit()
                print("\r\nRecord '{}' [{}] inserted successfully into DB".format(countIssue, issue['key']))
                
                countIssue += 1
            except pymysql.Error as e:
                print("ERROR: {}".format(e))

        # collect the completed issues in another sprint
        CompletedInAnotherIssueList = contents['issuesCompletedInAnotherSprint']
        for issue in CompletedInAnotherIssueList:
            issueKey = issue['key']
            collectAll(issueKey)
            try:
                insertIssue = "INSERT INTO sprint_issue(id, board_id, sprint_id, issue_key, state, addedDuringSprint, exist_in_website, collectedTime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
                inputPara = (
                    str(countIssue),
                    boardID,
                    sprintID,
                    issueKey,
                    "Completed in another sprint",
                    False,
                    0, 
                    datetime.now()
                ) 
                cursor.execute(insertIssue, inputPara)
                connection.commit()
                print("\r\nRecord '{}' [{}] inserted successfully into DB".format(countIssue, issue['key']))
                
                countIssue += 1
            except pymysql.Error as e:
                print("ERROR: {}".format(e))

        # collect the added issues during the sprint
        addedIssueList  = contents['issueKeysAddedDuringSprint']
        for issue in addedIssueList:
            try:
                updateIssue = "UPDATE sprint_issue Set addedDuringSprint = True WHERE board_id = %s and sprint_id = %s and issue_key = %s"
                inputPara = (
                    boardID,
                    sprintID,
                    issue
                )
                cursor.execute(updateIssue, inputPara)
                connection.commit()
                print("\r\nRecord '{}' [{}] updated successfully into DB".format(countIssue, issue))
                
            except pymysql.Error as e:
                print("ERROR: {}".format(e))
    
    print("\nTotal Issues from Sprints in {}: {}".format(repo.name.upper() ,countIssue))

def createRequest(url):
    """
    This method is called for creating request and receive the response back from server
    """
    apiToken = "<api_token>"

    headers = { 
        "Accept": "application/json", 
        "Bearer": apiToken,
    } 
    
    try:
        response = requests.request( 
            "GET", 
            url, 
            headers=headers 
        ) 
    except requests.exceptions.RequestException as e:  
        print("ERROR: {}".format(e))
        # sys.exit(1)

    json_data = json.loads(response.text)

    return json_data

def collectAll(issueKey, folder):
    collectDetail(issueKey, folder)
    time.sleep(0.001)
    collectComment(issueKey, folder)
    time.sleep(0.001)
    collectChangeLog(issueKey, folder)
    time.sleep(0.001)

def collectDetail(issueKey, folder):
    url = "https://{}/rest/api/2/issue/{}".format(repo.domain, issueKey)
    json_data = createRequest(url)
    writeFile(json_data, "detail", issueKey, folder, repo.name)

def collectComment(issueKey, folder):
    url = "https://{}/rest/api/2/issue/{}/comment".format(repo.domain, issueKey)
    json_data = createRequest(url)
    writeFile(json_data, "comment", issueKey, folder, repo.name)

def collectChangeLog(issueKey, folder):
    url = "https://{}/rest/api/2/issue/{}?expand=changelog".format(repo.domain, issueKey)
    json_data = createRequest(url)
    writeFile(json_data, "changeLog", issueKey, folder, repo.name)

def writeFile(data, type, issueKey, folder, repo):
    if type == "detail":
        path = "<directoty_path>".format(folder, repo, issueKey)
    elif type == "comment":
        path = "<directoty_path>".format(folder, repo, issueKey)
    elif type == "changeLog":
        path = "<directoty_path>".format(folder, repo, issueKey)

    try:
        with open(path, 'w') as json_file:
            json.dump(data, json_file)
        print("Write '{}' success!!".format(json_file.name))
    except:
        print("Write error!!")
        sys.exit(1)


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
    
    getIssueFromSprint()

    cursor.close()
    connection.close()
    print("DB Connection is closed")
