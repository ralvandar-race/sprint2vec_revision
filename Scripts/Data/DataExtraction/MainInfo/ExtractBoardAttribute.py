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

"""
ALTER TABLE `board_feature` 
ADD `canEdit` TINYINT(1) NULL DEFAULT NULL AFTER `type`, 
ADD `sprintSupportEnabled` TINYINT(1) NULL DEFAULT NULL AFTER `canEdit`, 
ADD `filterID` INT(11) NULL DEFAULT NULL AFTER `sprintSupportEnabled`, 
ADD `filterName` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `filterID`, 
ADD `filterQuery` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `filterName`, 
ADD `filterOwnerUsername` VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `filterQuery`, 
ADD `filterOwnerDisplayName` VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `filterOwnerUsername`, 
ADD `filterOwnerRenderedLink` VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `filterOwnerDisplayName`, 
ADD `filterCanEdit` TINYINT(1) NULL DEFAULT NULL AFTER `filterOwnerRenderedLink`, 
ADD `filterIsOrderedByRank` VARCHAR(1) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `filterCanEdit`,
ADD `filterCanBeFixed` TINYINT(1) NULL DEFAULT NULL AFTER `filterIsOrderedByRank`;
"""


def GetBoardDetail():
    """
    Collect the board detail from RapidBoard.json
    """
    print("Collect Board Feature from RapidBoard.json...")
    select = "SELECT `id`, board_id FROM board"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        id = row['id']
        boardID = row['board_id']
        rapidBoard = Utility.loadRapidBoardJSON(repo.name, db.folder)

        rapidViews = rapidBoard['views']
        for board in rapidViews:
            if int(boardID) == board['id']:
                canEdit = board['canEdit']
                sprintSupportEnabled = board['sprintSupportEnabled']
                filterID = board['filter']['id']
                filterName = board['filter']['name']
                filterQuery = board['filter']['query']
                filterOwnerUsername = board['filter']['owner']['userName']
                filterOwnerDisplayName = board['filter']['owner']['displayName']
                try:
                    filterOwnerRenderedLink = board['filter']['owner']['renderedLink']
                except:
                    filterOwnerRenderedLink = None
                try:
                    filterCanEdit = board['filter']['canEdit']
                except:
                    filterCanEdit = None
                try:
                    filterIsOrderedByRank = board['filter']['isOrderedByRank']
                except:
                    filterIsOrderedByRank = None
                try:
                    filterCanBeFixed = board['filter']['canBeFixed']
                except:
                    filterCanBeFixed = None

                updateBoardFeat = "UPDATE board_feature SET canEdit = %s, sprintSupportEnabled = %s, filterID = %s, filterName = %s, filterQuery = %s, filterOwnerUsername = %s, filterOwnerDisplayName = %s, filterOwnerRenderedLink = %s, filterCanEdit = %s, filterIsOrderedByRank = %s, filterCanBeFixed = %s WHERE board_id = %s"
                inputPara = (
                    canEdit,
                    sprintSupportEnabled,
                    filterID,
                    filterName,
                    filterQuery,
                    filterOwnerUsername,
                    filterOwnerDisplayName,
                    filterOwnerRenderedLink,
                    filterCanEdit,
                    filterIsOrderedByRank,
                    filterCanBeFixed,
                    boardID
                )

                cursor.execute(updateBoardFeat, inputPara)
                connection.commit()
                print('id: ', id)
                print('Feature of Board {} has been collected successfully'.format(boardID))
                
                

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
