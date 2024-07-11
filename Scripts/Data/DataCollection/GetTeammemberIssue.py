import requests 
import json
import pymysql
import time
from datetime import datetime
import sys
import os
import base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.RepoConfig as Repo

def main():
    """
    Main function to collect the issues associated with the team members
    """
    selectKey = "SELECT DISTINCT(issue_key) FROM sprint_teammember_issue_new WHERE issue_key NOT IN (SELECT issue_key FROM collected_key)"
    cursor.execute(selectKey)
    result = cursor.fetchall()

    for row in result:
        currentKey = row['issue_key']
        check = 0
        try:
            print("\n")
            # collect the detail of the issue
            collectDetail(currentKey, db.folder)
            time.sleep(0.001)
            # collect the comments of the issue
            collectComment(currentKey, db.folder)
            time.sleep(0.001)
            # collect the change log of the issue
            collectChangeLog(currentKey, db.folder)
            time.sleep(0.001)
            check = 1
        except Exception as e:
            print("ERROR: {}".format(e))
            check = 0
            time.sleep(1)
        finally:
            if check == 1:
                storeDB(currentKey)
                print("\n")


def storeDB(currentKey):
    """
    Store the issue key into the database
    """
    insertKey = "INSERT INTO collected_key(`issue_key`, `collectedTime`) VALUES(%s, %s)"
    inputPara = (
        currentKey,
        datetime.now()
    )
    cursor.execute(insertKey, inputPara)
    connection.commit()
    print("Inserted {} successfully".format(currentKey))



def createRequest(url):
    """
    Send a request to the given URL
    
    <url>: The URL to send the request to
    """

    # <api_token>: your api token for the repository
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


def collectDetail(issueKey, folder):
    """
    Collect the detail of the issue
    """
    url = "https://{}/rest/api/2/issue/{}".format(repo.domain, issueKey)
    json_data = createRequest(url)
    writeFile(json_data, "detail", issueKey, folder, repo.name)

def collectComment(issueKey, folder):
    """
    Collect the comments of the issue
    """
    url = "https://{}/rest/api/2/issue/{}/comment".format(repo.domain, issueKey)
    json_data = createRequest(url)
    writeFile(json_data, "comment", issueKey, folder, repo.name)

def collectChangeLog(issueKey, folder):
    """
    Collect the change logs of the issue
    """
    url = "https://{}/rest/api/2/issue/{}?expand=changelog".format(repo.domain, issueKey)
    json_data = createRequest(url)
    writeFile(json_data, "changeLog", issueKey, folder, repo.name)

def writeFile(data, type, issueKey, folder, repo):
    if type == "detail":
        path = "<file_path>".format(folder, repo, issueKey)
    elif type == "comment":
        path = "<file_path>".format(folder, repo, issueKey)
    elif type == "changeLog":
        path = "<file_path>".format(folder, repo, issueKey)

    try:
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
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
    main()
    cursor.close()
    connection.close()
    
    print("DB Connection is closed")
    print("----------------- COMPLETED -----------------")