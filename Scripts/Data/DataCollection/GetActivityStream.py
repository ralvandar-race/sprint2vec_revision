import base64
import calendar
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import json
import os
import sys
import time

import pymysql
import requests

from lxml import etree
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.RepoConfig as Repo


def main():
    """
    Main function to get the activity stream of the users in the sprint team
    """
    selectUsers = "SELECT board_id, sprint_id, username FROM sprint_teammember ORDER BY board_id ;"
    cursor.execute(selectUsers)
    result = cursor.fetchall()

    for user in result:
        currentBoardID = user['board_id']
        currentSprintID = user['sprint_id']
        username = user['username']
        print("BID: ", currentBoardID, "SID: ", currentSprintID)

        selectStartDate = "SELECT start_date FROM sprint_feature WHERE board_id = %s AND sprint_id = %s"
        inputPara = (
            currentBoardID,
            currentSprintID
        )
        cursor.execute(selectStartDate, inputPara)
        result = cursor.fetchall()

        dateTimeCode = '%Y-%m-%d %H:%M:%S'
        
        # Get the activity stream of the user
        for sprint in result:
            startDate = str(sprint['start_date'])
            utcEpoch = int(calendar.timegm(time.strptime(startDate, dateTimeCode))) * 1000
            try: # Get the activity stream of the user for the last 3 months
                nextMonth = monthsBefore(sprint['start_date'], 3)
                utcEpochBefore = int(calendar.timegm(time.strptime(nextMonth, dateTimeCode))) * 1000
                url = "https://{}/activity?streams=user+IS+{}&streams=update-date+BETWEEN+{}+{}&startAt=0&maxResults=1000".format(repo.domain, username, utcEpochBefore, utcEpoch)
                print(url, currentBoardID, currentSprintID)
                xml_data = createRequest(url)
            except:
                try: # Get the activity stream of the user for the last 2 months
                    nextMonth = monthsBefore(sprint['start_date'], 2)
                    utcEpochBefore = int(calendar.timegm(time.strptime(nextMonth, dateTimeCode))) * 1000
                    url = "https://{}/activity?streams=user+IS+{}&streams=update-date+BETWEEN+{}+{}&startAt=0&maxResults=1000".format(repo.domain, username, utcEpochBefore, utcEpoch)
                    print(url, currentBoardID, currentSprintID)
                    xml_data = createRequest(url)
                except: # Get the activity stream of the user for the last 1 month
                    nextMonth = monthsBefore(sprint['start_date'], 1)
                    utcEpochBefore = int(calendar.timegm(time.strptime(nextMonth, dateTimeCode))) * 1000
                    url = "https://{}/activity?streams=user+IS+{}&streams=update-date+BETWEEN+{}+{}&startAt=0&maxResults=1000".format(repo.domain, username, utcEpochBefore, utcEpoch)
                    print(url, currentBoardID, currentSprintID)

            writeFile(xml_data, db.folder, repo.name, username, currentBoardID, currentSprintID)


def monthsBefore(sourcedate, num_months):
    """
    Get the date of the month before the source date
    """
    print("Original Date: {}".format(sourcedate))
    end_date = sourcedate + relativedelta(months=-num_months)
    months_before = datetime.datetime(end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute, end_date.second)
    print("One Month Before: {}".format(months_before))
    return str(months_before)



def createRequest(url):
    """
    Create a request to get the activity stream of the user
    """

    try:
        response = requests.request(
            "GET",
            url,
        )
    except requests.exceptions.RequestException as e:  
        print("ERROR: {}".format(e))

    # print(response.text)

    return response.text


def writeFile(data, folder, repo, user, boardID, sprintID):
    """
    Write the activity stream of the user to a file
    """
    path = "<file_path>".format(folder, repo, boardID, sprintID, user)

    try:
        with open(path, 'w',  encoding="utf-8") as xmlFile:
            xmlFile.write(data)
        print("Write '{}' success!!\n".format(xmlFile.name))
    except Exception as e:
        print("Write error!!: {}\n".format(e))
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
