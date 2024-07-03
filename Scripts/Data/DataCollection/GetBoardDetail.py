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
import Utility.RepoConfig as Repo


def GetBoardDetail():
    """
    Get the board detail of the repository
    """
    print("Collect Board Detail...")
    select = "SELECT board_id FROM board"
    cursor.execute(select)
    result = cursor.fetchall()

    countBoard = 0
    for row in result:
        boardID = row['board_id']
        url = "https://{}/rest/agile/1.0/board/{}".format(repo.domain, boardID)
        # send request to get the board detail
        json_data = createRequest(url)
        # store the board detail into the database
        try:
            insertDetail = "INSERT INTO board_feature(id, board_id, name, url, type, collectedTime) VALUES(%s, %s, %s, %s, %s, %s)"
            inputPara = (
                countBoard,
                boardID,
                json_data['name'],
                json_data['self'],
                json_data['type'],
                datetime.now()
            )
            cursor.execute(insertDetail, inputPara)
            connection.commit()
            print("\r\nRecord '{}' [{}] inserted successfully into DB".format(countBoard, boardID))
            countBoard += 1
        except pymysql.Error as e:
            print("ERROR: {}".format(e))



def createRequest(url):
    userpass = repo.userpass
    encoded = str(base64.b64encode(bytearray(userpass, "utf-8")))
    basicAuth = "Basic " + encoded[2:len(encoded)-1]

    headers = {
        "Accept": "application/json",
        "Authorization": basicAuth,
    }

    try:
        response = requests.request(
            "GET",
            url,
            headers = headers
        )
        print(url)
        time.sleep(1)
    except requests.exceptions.RequestException as e:  
        print("ERROR: {}".format(e))

    # print(response.text)
    json_data = json.loads(response.text)
    return json_data



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

    GetBoardDetail()

    cursor.close()
    connection.close()
    print("DB Connection is closed")
