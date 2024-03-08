import sys
import json
import time
import pymysql
import os
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo


"""
# for normal issue
CREATE TABLE `issue_changelog` (
  `idIssueChangeLog` int(11) NOT NULL AUTO_INCREMENT,
  `issue_key` varchar(45) NOT NULL,
  `LogId` varchar(100) DEFAULT NULL,
  `AuthorDisplayName` varchar(100) DEFAULT NULL,
  `AuthorEmail` varchar(100) DEFAULT NULL,
  `CreatedDate` datetime DEFAULT NULL,
  `Field` text,
  `FieldType` text,
  `From` longtext,
  `FromString` longtext,
  `To` longtext,
  `ToString` longtext,
  PRIMARY KEY (`idIssueChangeLog`),
  KEY `key` (`issue_key`),
  KEY `id` (`LogId`),
  KEY `date` (`CreatedDate`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

# for teammember issue
CREATE TABLE `teammember_issue_changelog` (
  `idIssueChangeLog` int(11) NOT NULL AUTO_INCREMENT,
  `issue_key` varchar(45) NOT NULL,
  `LogId` varchar(100) DEFAULT NULL,
  `AuthorDisplayName` varchar(100) DEFAULT NULL,
  `AuthorEmail` varchar(100) DEFAULT NULL,
  `CreatedDate` datetime DEFAULT NULL,
  `Field` text,
  `FieldType` text,
  `From` longtext,
  `FromString` longtext,
  `To` longtext,
  `ToString` longtext,
  PRIMARY KEY (`idIssueChangeLog`),
  KEY `key` (`issue_key`),
  KEY `id` (`LogId`),
  KEY `date` (`CreatedDate`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
"""


def main(choice, issueTable, changelogTable):
    print("Collect Issue changelog...")

    # retrieve only issueKey(s) that don't appear in sprint_issue table
    selectIssueKey = "SELECT DISTINCT issue_key FROM " + issueTable + " WHERE issue_key NOT IN (SELECT issue_key FROM " + changelogTable + ") AND exist_in_website = 1"
    cursor.execute(selectIssueKey)
    result = cursor.fetchall()

    #------------- START Extract issue changelog to issue_changelog table -------------#
    print("Extracting issue changelog to {}...".format(changelogTable))
    countAll = 0
    count = 0
    for row in result:
        countAll += 1
        issueKey = row['issue_key']
        noError = 1
        insertSQLList = list()
        print("IssueKey: {}".format(issueKey))
        json_data = Utility.loadIssueChangLogJSON(issueKey, repo.name, db.folder)

        # in case that the issue doesn't exist in website, skip it
        try:    
            changeLog = json_data['changelog']
        except Exception as e:
            print("The issue [{}] doesn't exist in Website".format(issueKey))
            continue

        # collect changelog for only issues that have `histories` (changelog)
        if changeLog['histories']:
            histories = changeLog['histories']
            for history in histories:
                items = history['items']
                logID = history['id']
                try:
                    author = history['author']
                    try:
                        authorDisplayName = author['displayName']
                    except:
                        authorDisplayName = None
                    # some repo doesn't have emailAddress field
                    try:
                        authorEmail = author['emailAddress']
                    except:
                        authorEmail = None
                except:
                    authorDisplayName = None
                    authorEmail = None
                createdDate = datetime.datetime.strptime(
                    history['created'].split('.')[0] + "Z", 
                    "%Y-%m-%dT%H:%M:%SZ"
                )
                for item in items:
                    try:
                        field = item['field']
                        fieldType = item['fieldtype']
                        try:
                            fr0m = checkNull(item['from'])
                        except:
                            fr0m = None
                        try:
                            fromString = checkNull(item['fromString'])
                        except:
                            fromString = None
                        try:
                            to = checkNull(item['to'])
                        except:
                            to = None
                        try:
                            toString = checkNull(item['toString'])
                        except:
                            toString = None

                        insertChangeLog = "INSERT INTO " + changelogTable + "(`issue_key`, `LogId`, `AuthorDisplayName`, `AuthorEmail`, `CreatedDate`, `Field`, `FieldType`, `From`, `FromString`, `To`, `ToString`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        inputPara = (
                            issueKey,
                            logID,
                            authorDisplayName,
                            authorEmail,
                            createdDate,
                            field,
                            fieldType,
                            fr0m,
                            fromString,
                            to,
                            toString
                        )

                        sql = (insertChangeLog, inputPara)
                        insertSQLList.append(sql)

                    except Exception as e:
                        noError = 0
                        print("ERROR: {}".format(e))
                        break

        # if the issue has no error, let insert all of its changelogs
        if noError == 1:
            count += 1
            for insert, para in insertSQLList:
                print("Inserted successfully into DB\n")
                cursor.execute(insert, para)
                connection.commit()

    time.sleep(0.001)
    #------------- END Extract issue changelog to issue_changelog table -------------#

    print("\nDone for issue changelog in {}! \n".format(repo.name.upper()))
    print("Number of issue needed to be collected: {}".format(countAll))
    print("Number of collected issue: {}".format(count))


def checkNull(item):
    """
    if item is NULL or "" or None, convert to None
    """
    if item == None or item == "" or not item:
        return None
    return item


if __name__ == '__main__':
    repo = Repo.createRepo()
    db = DB.createDB(repo)

    choice = int(input("Please choose the choice\n[1]Normal Issue\n[2]Issue from activity stream\n:"))
    # normal issue
    if choice == 1:
        issueTable = "sprint_issue"
        changelogTable = "issue_changelog"
    # issue from activity stream
    else:
        issueTable = "sprint_teammember_issue_new"
        changelogTable = "teammember_issue_changelog"

    connection = pymysql.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        passwd=db.pwd,
        database=db.repo.name,
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = connection.cursor()   
    
    main(choice, issueTable, changelogTable)

    cursor.close()
    connection.close()
    print("DB Connection is closed")