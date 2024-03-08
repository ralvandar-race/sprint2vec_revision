import sys
import os
import requests
import json
import base64
import pymysql
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo
import Utility.DBConfig as DB


def collectRapidBoard():
    print("Collect Rapid Board...")
    url = "https://{}/rest/greenhopper/1.0/rapidviews/list/".format(repo.domain)

    json_data = createRequest(url)

    writeFile(json_data, repo.name, db.folder)


def createRequest(url): 
    # userpass = "username:password"
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
    except requests.exceptions.RequestException as e:  
        print("ERROR: {}".format(e))

    json_data = json.loads(response.text)

    return json_data


def writeFile(data, repo, folder):
    path = "<file_path>".format(folder, repo)
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

    collectRapidBoard()

    cursor.close()
    connection.close()
    print("DB Connection is closed")