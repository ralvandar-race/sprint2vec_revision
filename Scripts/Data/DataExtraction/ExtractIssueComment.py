import sys
import json
import pymysql
import os
import datetime
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.DBConfig as DB
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo

"""
# for normal issue
CREATE TABLE `sprint_issue_comment` (
  `board_id` int(11) NOT NULL,
  `sprint_id` int(11) NOT NULL,
  `issue_key` varchar(45) NOT NULL,
  `comment_id` varchar(45) NOT NULL,
  `createddate` datetime DEFAULT NULL,
  `body` mediumtext,
  `author` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`board_id`,`sprint_id`,`issue_key`,`comment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

# for teammember issue
CREATE TABLE `sprint_teammember_issue_comment` (
  `board_id` int(11) NOT NULL,
  `sprint_id` int(11) NOT NULL,
  `issue_key` varchar(45) NOT NULL,
  `comment_id` varchar(45) NOT NULL,
  `createddate` datetime DEFAULT NULL,
  `body` mediumtext,
  `author` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`board_id`, `sprint_id`, `issue_key`, `comment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

def main(choice, issueTable, commentTable):
    print("Collect Issue Comment...")
    
    if choice == 1:
        select = "SELECT board_id, sprint_id, issue_key FROM sprint_issue WHERE NOT EXISTS (SELECT board_id, sprint_id, issue_key FROM sprint_issue_comment WHERE sprint_issue.board_id = sprint_issue_comment.board_id AND sprint_issue.sprint_id = sprint_issue_comment.sprint_id AND sprint_issue.issue_key = sprint_issue_comment.issue_key) AND exist_in_website = 1"
    else:
        select = "SELECT DISTINCT(issue_key), board_id, sprint_id FROM " + issueTable + " WHERE NOT EXISTS (SELECT board_id, sprint_id, issue_key FROM " + commentTable + " WHERE " + issueTable + ".board_id = " + commentTable + ".board_id AND " + issueTable + ".sprint_id = " + commentTable + ".sprint_id AND " + issueTable + ".issue_key = " + commentTable + ".issue_key) AND exist_in_website = 1"
    cursor.execute(select)
    result = cursor.fetchall()

    #------------- START Extract issue comment to sprint_issue_comment table -------------#
    print("Extracting issue comment to {} ...".format(commentTable))
    countAll = 0
    count = 0
    for row in result:
        countAll += 1
        noError = 1
        insertSQLList = list()
        boardID = row['board_id']
        sprintID = row['sprint_id']
        issueKey = row['issue_key']

        print("Extract issue [{}] in sprint [{}] on board [{}]".format(issueKey, sprintID, boardID))
        json_data = Utility.loadIssueCommentJSON(issueKey, repo.name, db.folder)

        # in case that the issue doesn't exist in website, skip it
        try:    
            comments = json_data['comments']
        except Exception as e:
            print("ERROR: {}".format(e))
            continue

        for comment in comments:
            try:
                commentID = comment['id']
                createdDate = datetime.datetime.strptime(
                    comment['created'].split('.')[0] + "Z", 
                    "%Y-%m-%dT%H:%M:%SZ"
                )
                body = comment['body']
                author = comment['author']['name']

                insertChangeLog = "INSERT INTO " + commentTable + "(`board_id`, `sprint_id`, `issue_key`, `comment_id`, `createdDate`, `body`, `author`) VALUES(%s, %s, %s, %s, %s, %s, %s)"
                inputPara = (
                    boardID,
                    sprintID,
                    issueKey,
                    commentID,
                    createdDate,
                    body,
                    author
                )

                sql = (insertChangeLog, inputPara)
                insertSQLList.append(sql)

            except Exception as e:
                noError = 0
                print("ERROR: {}".format(e))
                break

        if noError == 1:
            count += 1
            for insert, para in insertSQLList:
                print("Inserted successfully into DB\n")
                cursor.execute(insert, para)
                connection.commit()
    #------------- END Extract issue comment to sprint_issue_comment table -------------#

    print("Done for issue comment in {}! \n".format(repo.name.upper()))
    print("Number of issue needed to collect comment: {}".format(countAll))
    print("Number of collected issue: {}".format(count))



if __name__ == '__main__':
    repo = Repo.createRepo()
    db = DB.createDB(repo)

    choice = int(input("Please choose the choice\n[1]Normal Issue\n[2]Issue from activity stream\n:"))
    # normal issue
    if choice == 1:
        issueTable = "sprint_issue"
        commentTable = "sprint_issue_comment"
    # issue from activity stream
    else:
        issueTable = "sprint_teammember_issue_new"
        commentTable = "sprint_teammember_issue_comment"

    connection = pymysql.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        passwd=db.pwd,
        database=db.repo.name,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()   
    
    main(choice, issueTable, commentTable)

    cursor.close()
    connection.close()
    print("DB Connection is closed")
