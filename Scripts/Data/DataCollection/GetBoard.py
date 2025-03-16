import base64
import json
import os
import sys
import time
from datetime import datetime

import pymysql
import requests

# Update the path handling for Utility modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
utility_dir = os.path.join(os.path.dirname(current_dir), 'Utility')
sys.path.insert(0, utility_dir)

# Update imports to use the functions directly
from DBConfig import createDB
from RepoConfig import createRepo
import JSONUtility as Utility


def main():

    collectBoard()
    getSprintList()
    getSprint()


def collectBoard():
    """Collect record IDs from existing dataset"""
    print("Collecting Record IDs from existing data...")

    try:
        json_data = Utility.loadRapidBoardJSON(repo.name, db.folder)
        
        # Check existing board_ids
        select = "SELECT board_id FROM board"
        cursor.execute(select)
        existing_ids = {row['board_id'] for row in cursor.fetchall()}
        
        countBoard = 0
        for record in json_data['views']:
            currentID = record['id']
            
            if currentID not in existing_ids:
                insertBoardID = "INSERT INTO board(board_id, collectedTime) VALUES(%s, %s);"
                inputPara = (
                    currentID, 
                    datetime.now()
                )
                print(f"\nInserting Record ID: {currentID}")
                cursor.execute(insertBoardID, inputPara)
                connection.commit()
                countBoard += 1
            else:
                print(f"Record ID {currentID} already exists in DB")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print(f"\n----------------------RECORD ID COLLECTION COMPLETED ({countBoard} records)----------------------\n")


def getSprintList(): 
    """
    Collect the list of sprints from the board
    """
    print("Collect Board Detail...")
    select = "SELECT board_id FROM board"
    cursor.execute(select)
    result = cursor.fetchall()

    countBoard = 0
    for row in result:
        boardID = row['board_id']
        url = "https://{}/rest/greenhopper/1.0/sprintquery/{}?includeHistoricSprints=true&includeFutureSprints=true".format(repo.domain, boardID)
        json_data = createRequest(url)
        writeFile(json_data, "board", db.folder, repo.name, boardID)
        countBoard += 1
    
    print("Total Board: {}".format(countBoard))


def getSprint():
    """
    Collect the sprint details from the board
    """
    print("Collect Sprints from Board...")
    select = "SELECT board_id FROM board"
    cursor.execute(select)
    result = cursor.fetchall()

    countSprint = 0
    for row in result:
        boardID = row['board_id']
        board = Utility.loadBoardJSON(boardID, repo.name, db.folder)
        if not board['sprints'] is None:
            for sprint in board['sprints']:
                currentSprintID = str(sprint['id'])
                url = "https://{}/rest/greenhopper/latest/rapid/charts/sprintreport?rapidViewId={}&sprintId={}".format(repo.domain, boardID, currentSprintID)
                print(url)
                json_data = createRequest(url)
                time.sleep(2)
                try:
                    writeFile(json_data, "sprintGreen", db.folder, repo.name, boardID, currentSprintID)

                    insertSprint = "INSERT INTO sprint(id, board_id, sprint_id, collectedTime) VALUES(%s, %s, %s, %s)"
                    inputPara = (
                        countSprint,
                        boardID,
                        currentSprintID,
                        datetime.now()
                    )
                    
                    cursor.execute(insertSprint, inputPara)
                    connection.commit()
                    print("Record Sprint '{}' in Board {} inserted successfully into DB\r\n".format(currentSprintID, boardID))
                    
                    countSprint += 1
                except pymysql.Error as e:
                    print("ERROR: {}".format(e))

    print("Total Sprint: {}".format(countSprint))
    

def createRequest(url):
    """
    Send a request to the given URL
    <url>: The URL to send the request to
    """
    userpass = repo.userpass
    encoded = str(base64.b64encode(bytearray(userpass, "utf-8")))
    basicAuth = "Basic " + encoded[2:len(encoded)-1]

    headers = {
        "Accept": "application/json",
        "Authorization": basicAuth
    }
    try:
        response = requests.request(
            "GET",
            url,
            headers = headers
        )
    except requests.exceptions.RequestException as e:  
        print("ERROR: {}".format(e))

    json_data = json.loads(response.text)
    return json_data


def writeFile(data, type, folder, repo, boardID="", sprintID=""):
    if type == "board":
        path = "{}/{}/board_{}.json".format(folder, repo, boardID)
    elif type == "sprintGreen":
        path = "{}/{}/sprint_{}_{}.json".format(folder, repo, boardID, sprintID)
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("Write '{}' success!!".format(json_file.name))


if __name__ == '__main__':
    repo = createRepo(
        "apache"
    )
    
    db = createDB(
        repo=repo,
        host="localhost",
        port=3306,
        user="root",
        pwd="capstone",
        folder="D:/REVA/Capstone1/sprint2vec_revision/Dataset/existing"  # Updated path
    )

    try:
        connection = pymysql.connect(
            host=db.host,
            port=db.port,
            user=db.user,
            passwd=db.pwd,
            database="sprint2vec",
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        print("Database connection established successfully")

        main()

    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
    
    finally:
        if 'connection' in locals() and connection.open:
            cursor.close()
            connection.close()
            print("DB Connection is closed")
