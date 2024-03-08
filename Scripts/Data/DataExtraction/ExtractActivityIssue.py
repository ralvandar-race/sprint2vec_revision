import xml.etree.ElementTree as ET
import pymysql
import os
import sys
import re
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Utility.RepoConfig as Repo
import Utility.DBConfig as DB

"""
CREATE TABLE `sprint_teammember_issue_new` (
  `board_id` int(11) NOT NULL,
  `sprint_id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `issue_key` varchar(45) NOT NULL,
  `action` varchar(255) NOT NULL,
  `exist_in_website` tinyint(4) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


"""
def main():

    error_list = list()

    select = "SELECT sprint_teammember.board_id, sprint_teammember.sprint_id, sprint_teammember.username FROM sprint_teammember JOIN sprint_feature ON sprint_feature.board_id = sprint_teammember.board_id AND sprint_feature.sprint_id = sprint_teammember.sprint_id WHERE sprint_feature.state = 'CLOSED' AND sprint_teammember.board_id >= '211'"
    cursor.execute(select)
    result = cursor.fetchall()

    for row in result:
        boardID = row['board_id']
        sprintID = row['sprint_id']
        username = row['username']

        xmlFile = "C:/Users/peera/Documents/{}/{}/activityStream/{}_{}_{}.xml".format(db.folder, repo.name, boardID, sprintID, username)
        print("\nuser: {}".format(username))
        print(xmlFile)
        
        # some devs don't exist in website
        try:
            tree = ET.parse(xmlFile)
        except:
            continue
            
        root = tree.getroot()
        # print(root.tag)

        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title")
        
            soup = BeautifulSoup(title.text, 'html.parser')

            try:
                usr = soup.find('a').text
            except:
                continue

            try:
                action = soup.find('a', text=re.compile(usr)).next_sibling.strip()
            # can't extract action from this title
            except:
                continue

            aTags = soup.find_all('a')
            
            # handle normal format
            try:
                issueKey = aTags[len(aTags)-1].find('span').text
            # not normal
            except:
                issueKey = aTags[len(aTags)-1].text
                issueKey = issueKey.split()[0]
                # print(issueKey)
                pass

            check1 = issueKey.split()
            if len(check1) == 1:
                check2 = issueKey.split('-')
                if len(check2) == 2:
                    if check2[1].isdigit():

                        insert = "INSERT INTO sprint_teammember_issue_new(board_id ,sprint_id ,username ,issue_key, action) VALUES(%s, %s, %s, %s, %s)"
                        inputPara = (
                            boardID,
                            sprintID,
                            username,
                            issueKey,
                            action
                        )

                        try:
                            cursor.execute(insert, inputPara)
                            connection.commit()
                        except:
                            error_list.append({'boardID': boardID, 'sprintID': sprintID, 'username': username, 'issueKey': issueKey, 'action': action})
                            continue
                            # print("ERROR: ", issueKey, action)
                            # sys.exit()

                        print("insert {} involving with {} into DB successfully".format(issueKey, username))
    
    print(error_list)


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