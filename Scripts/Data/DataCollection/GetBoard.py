import base64
import json
import os
import sys
import time
from datetime import datetime

import pymysql
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo


def main():

    collectBoard()
    getSprintList()
    getSprint()


def collectBoard():
    """
    Collect the board ID from the repository
    """
    print("Collect Board ID...")

    json_data = Utility.loadRapidBoardJSON(repo.name, db.folder)   # Modified

    try:
        select = "SELECT board_id FROM board"
        cursor.execute(select)
        result = cursor.fetchall()
        exist = False

        countBoard = 0
        for board in json_data['views']:
            currentBoardID = str(board['id'])
            for row in result:
                if currentBoardID == row['board_id']:
                    exist = True
            if exist == False:
                # print("{} {} {} {}".format(board['id'], board['name'], board['type'],board['self']))
                insertBoardID = "INSERT INTO board(id, board_id, collectedTime) VALUES(%s, %s, %s);"
                inputPara = (
                    countBoard,
                    currentBoardID, 
                    datetime.now() 
                )
                print("\r\n\r\nRecord '{}' [{}] inserted successfully into DB".format(countBoard,board['id']))
                cursor.execute(insertBoardID, inputPara)
                connection.commit()
                countBoard += 1

            else:
                print("Record '{}' is already in DB".format(board['id']))
                exist = False
    except pymysql.Error as e:
        print("ERROR: {}".format(e))
    finally:
        print("\r\n----------------------STORE BOARD ID ON DB COMPLETED----------------------\r\n")


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
    # userpass = "username:password"
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
    # print(json_data)

    return json_data


def writeFile(data, type, folder, repo, boardID="", sprintID=""):
    if type == "board":
        path = "<file_path>".format(folder, repo, boardID)
    elif type == "sprintGreen":
        path = "<file_path>".format(folder, repo, boardID, sprintID)
    # try:
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("Write '{}' success!!".format(json_file.name))
    # except:
        # print("Write error!!")
        # sys.exit(1)


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
