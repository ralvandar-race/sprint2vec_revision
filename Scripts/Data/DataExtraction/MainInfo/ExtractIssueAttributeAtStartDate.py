import sys
import json
from turtle import up
from matplotlib.pyplot import text
import pymysql
import os
import datetime
import time
import textstat
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Utility.DBConfig as DB
import Utility.JSONUtility as Utility
import Utility.RepoConfig as Repo


def extractIssueFeature(featureTable, insightTable, clTable):
    print("Create table: " + insightTable + " duplicated from " + featureTable + " ...")

    select_max = "SELECT MAX(`no_component`) as maxCom FROM " + featureTable
    try:
        cursor.execute(select_max)
        res = cursor.fetchone()
        max_component = int(res['maxCom'])
    except:
        pass

    try:
        drop_table = "DROP TABLE IF EXISTS " + insightTable
        cursor.execute(drop_table)
        connection.commit()
    except:
        pass
    
    try:
        create_column = "CREATE TABLE %s SELECT board_id, sprint_id, issue_key, summary, description, storypoint, type, priority, no_component, openeddate, "
        for c in range(0, max_component):
            if c == max_component - 1:
                create_column += "component_{} FROM %s".format(c+1)
            else:
                create_column += "component_{}, ".format(c+1)
        input_para = (
            insightTable, 
            featureTable
        )
        cursor.execute(create_column % input_para)
        connection.commit()
        print("Create table: " + insightTable + " ... Done")
    except:
        pass

    try:
        add_lifetime_column = "ALTER TABLE " + insightTable + " ADD COLUMN `lifetime` INT NULL DEFAULT NULL"
        cursor.execute(add_lifetime_column)
        connection.commit()
    except:
        pass

    select_sql = "SELECT iss.*, spr.`start_date` FROM %s iss JOIN %s spr ON iss.`board_id` = spr.`board_id` AND iss.`sprint_id` = spr.`sprint_id`  WHERE `lifetime` IS NULL;"
    input_para = (
        insightTable,
        "sprint_feature"
    )
    cursor.execute(select_sql % input_para)
    result = cursor.fetchall()

    for row in result:
        start_date = row['start_date']
        board_id = row['board_id']
        sprint_id = row['sprint_id']
        issue_key = row['issue_key']
        summary = row['summary']
        description = row['description']
        storypoint = row['storypoint']
        type = row['type']
        priority = row['priority']
        no_component = row['no_component']
        open_date = row['openeddate']
        lifetime = start_date - open_date
        lifetime = int(lifetime.total_seconds() // 3600)
        components = set()
        for c in range(0, no_component):
            components.add(row['component_{}'.format(c+1)])

        print(issue_key)

        cl_dict = {
            "description": description,
            "Story Points": storypoint,
            "summary": summary,
            "type": type,
            "priority": priority,
            "Component": components
        }

        fields = {'Component', 'description', 'Story Points', 'summary', 'type', 'priority'}

        # before
        before_fields = set()
        select_before_cl_sql = """
            SELECT Field, FromString, ToString, CreatedDate 
            FROM `%s` 
            WHERE `issue_key` = '%s'
            AND `CreatedDate` <= '%s'
            AND `Field` IN ('Component', 'description', 'Story Points', 'summary', 'type', 'priority')
            ORDER BY `CreatedDate` ASC"""
        input_para = (
            clTable,
            issue_key,
            start_date
        )
        cursor.execute(select_before_cl_sql % input_para)
        result_cl = cursor.fetchall()
        
        for cl in result_cl:
            field = cl['Field']
            to_string = cl['ToString']

            if field != 'Component':
                before_fields.add(field)
                cl_dict[field] = to_string
            else:
                if not to_string is None:
                    cl_dict[field].add(to_string)

        # after
        after_fields = fields.symmetric_difference(before_fields)
        select_after_cl_sql = """
            SELECT Field, FromString, ToString, CreatedDate
            FROM `%s` 
            WHERE `issue_key` = '%s'
            AND `CreatedDate` > '%s'
            AND `Field` IN ("""
        
        count = 0
        for field in after_fields:
            if count == len(after_fields) - 1:
                select_after_cl_sql += "'%s')" % field
            else:
                select_after_cl_sql += "'%s', " % field
            count += 1

        input_para = (
            clTable,
            issue_key,
            start_date
        )
        cursor.execute(select_after_cl_sql % input_para)
        result_cl = cursor.fetchall()
        
        for cl in result_cl:
            field = cl['Field']
            from_string = cl['FromString']
            to_string = cl['ToString']

            if field != 'Component':
                cl_dict[field] = from_string
            else:
                if not to_string is None:
                    try:
                        cl_dict[field].remove(to_string)
                    except:
                        pass
                    cl_dict[field].add(from_string)

        # print(cl_dict["Component"])
        try:
            cl_dict["Component"].remove(None)
        except:
            pass
        # print(cl_dict["Component"])

        update_sql = "UPDATE " + insightTable + " SET summary = %s, description = %s, storypoint = %s, type = %s, priority = %s, no_component = %s, lifetime = %s"
        # for c in range(0, len(cl_dict['Component'])):
        #     update_sql += ", component_{} = '{}'".format(c+1, list(cl_dict['Component'])[c])
        update_sql += " WHERE board_id = %s AND sprint_id = %s AND issue_key = %s"

        # print(len(cl_dict['Component']))
        input_para = (
            cl_dict['summary'],
            cl_dict['description'],
            cl_dict['Story Points'],
            cl_dict['type'],
            cl_dict['priority'],
            len(cl_dict['Component']),
            lifetime,
        )
        # for c in range(0, len(cl_dict['Component'])):
        #     input_para += (list(cl_dict['Component'])[c],)
        input_para += (board_id, sprint_id, issue_key)
        cursor.execute(update_sql, input_para)
        connection.commit()
        print("Update " + insightTable + " for issue " + issue_key + " ... Done")


    # drop column for component
    for c in range(0, max_component):
        drop_column_sql = "ALTER TABLE " + insightTable + " DROP COLUMN `component_{}`".format(c+1)
        cursor.execute(drop_column_sql)
        connection.commit()
        print("Drop column component_{} ... Done".format(c+1))

    print("Done for {}".format(repo.name.upper()))

def gunning_fog_index(insightTable):
    print("\nGunning Fog Index for {}".format(insightTable))
    try:
        add_column = "ALTER TABLE " + insightTable + " ADD COLUMN `fog_index` FLOAT NULL DEFAULT 0"
        cursor.execute(add_column)
        connection.commit()
        print("Add column fog_index ... Done")
    except:
        print("Column fog_index already exists")

    select = "SELECT board_id, sprint_id, issue_key, description FROM " + insightTable + " WHERE description IS NOT NULL"
    cursor.execute(select)
    result = cursor.fetchall()
    for row in result:
        board_id = row['board_id']
        sprint_id = row['sprint_id']
        issue_key = row['issue_key']
        description = row['description']
        fog = textstat.gunning_fog(description)
        update_sql = "UPDATE " + insightTable + " SET fog_index = %s WHERE board_id = %s AND sprint_id = %s AND issue_key = %s"
        input_para = (fog, board_id, sprint_id, issue_key)
        cursor.execute(update_sql, input_para)
        connection.commit()
        print("Fog index for issue " + issue_key + " is " + str(fog))


def num_comments(insightTable):
    print("\nNumber of Comments for {}".format(insightTable))
    try:
        add_column = "ALTER TABLE " + insightTable + " ADD COLUMN `no_comments` INT NULL DEFAULT 0"
        cursor.execute(add_column)
        connection.commit()
        print("Add column no_comments ... Done")
    except:
        print("Column no_comments already exists")

    select = "SELECT iss.board_id, iss.sprint_id, iss.issue_key, sf.`start_date` FROM " + insightTable + " iss JOIN sprint_feature sf ON iss.board_id = sf.board_id AND iss.sprint_id = sf.sprint_id"
    cursor.execute(select)
    result = cursor.fetchall()
    for row in result:
        board_id = row['board_id']
        sprint_id = row['sprint_id']
        issue_key = row['issue_key']
        start_date = row['start_date']
        select_comment_sql = "SELECT COUNT(*) AS no_comments FROM `sprint_issue_comment` WHERE `board_id` = %s AND `sprint_id` = %s AND `issue_key` = %s AND `createddate` <= %s"
        input_para = (board_id, sprint_id, issue_key, start_date)
        cursor.execute(select_comment_sql, input_para)
        result_comment = cursor.fetchall()
        for row_comment in result_comment:
            no_comments = row_comment['no_comments']
            update_sql = "UPDATE " + insightTable + " SET no_comments = %s WHERE board_id = %s AND sprint_id = %s AND issue_key = %s"
            input_para = (no_comments, board_id, sprint_id, issue_key)
            cursor.execute(update_sql, input_para)
            connection.commit()
            print("Number of comments for issue " + issue_key + " is " + str(no_comments))

def num_change(insightTable, clTable):
    print("\nNumber of Changes for {}".format(insightTable))
    try:
        add_column = "ALTER TABLE " + insightTable + " ADD COLUMN `no_change_description` INT NULL DEFAULT 0,    ADD COLUMN `no_change_priority` INT NULL DEFAULT 0, ADD COLUMN `no_change_fix` INT NULL DEFAULT 0"
        cursor.execute(add_column)
        connection.commit()
        print("Add column no_change_description ... Done")
        print("Add column no_change_priority ... Done")
        print("Add column no_change_fix ... Done")
    except:
        print("Column no_change_description already exists")
        print("Column no_change_priority already exists")
        print("Column no_change_fix already exists")

    select = "SELECT iss.board_id, iss.sprint_id, iss.issue_key, sf.`start_date` FROM " + insightTable + " iss JOIN sprint_feature sf ON iss.board_id = sf.board_id AND iss.sprint_id = sf.sprint_id"
    cursor.execute(select)
    result = cursor.fetchall()
    for row in result:
        board_id = row['board_id']
        sprint_id = row['sprint_id']
        issue_key = row['issue_key']
        start_date = row['start_date']
        select_change_desc = """
        SELECT COUNT(*) AS no_change_description FROM 
        ( SELECT DISTINCT 
        `issue_key`, `LogId`, `AuthorDisplayName`, `AuthorEmail`, `CreatedDate`, `Field`, `FieldType`, `From`, `FromString`, `To`, `ToString` 
        FROM issue_changelog WHERE `issue_key` = %s AND `createddate` <= %s AND `field` = 'description') AS T"""
        select_change_pri = """
        SELECT COUNT(*) AS no_change_priority FROM
        ( SELECT DISTINCT
        `issue_key`, `LogId`, `AuthorDisplayName`, `AuthorEmail`, `CreatedDate`, `Field`, `FieldType`, `From`, `FromString`, `To`, `ToString`
        FROM issue_changelog WHERE `issue_key` = %s AND `createddate` <= %s AND `field` = 'priority') AS T"""
        select_change_fix = """
        SELECT COUNT(*) AS no_change_fix FROM
        ( SELECT DISTINCT
        `issue_key`, `LogId`, `AuthorDisplayName`, `AuthorEmail`, `CreatedDate`, `Field`, `FieldType`, `From`, `FromString`, `To`, `ToString`
        FROM issue_changelog WHERE `issue_key` = %s AND `createddate` <= %s AND `field` = 'Fix Version') AS T"""
        input_para = (issue_key, start_date)
        cursor.execute(select_change_desc, input_para)
        result_desc = cursor.fetchone()
        cursor.execute(select_change_pri, input_para)
        result_pri = cursor.fetchone()
        cursor.execute(select_change_fix, input_para)
        result_fix = cursor.fetchone()
        no_change_description = result_desc['no_change_description']
        no_change_priority = result_pri['no_change_priority']
        no_change_fix = result_fix['no_change_fix']
        update_sql = "UPDATE " + insightTable + " SET no_change_description = %s, no_change_priority = %s, no_change_fix = %s WHERE board_id = %s AND sprint_id = %s AND issue_key = %s"
        input_para = (no_change_description, no_change_priority, no_change_fix, board_id, sprint_id, issue_key)
        cursor.execute(update_sql, input_para)
        connection.commit()


if __name__ == '__main__':
    repo = Repo.createRepo()
    db = DB.createDB(repo)

    choice = int(input("Please choose the choice\n[1]Normal Issue\n[2]Issue from activity stream\n:"))
    # normal issue
    if choice == 1:
        featureTable = "sprint_issue_feature"
        insightTable = "sprint_issue_feature_insight"
        clTable = "issue_changelog"
    # issue from activity stream
    else:
        featureTable = "sprint_teammember_issue_feature_new"
        insightTable = "sprint_teammember_issue_feature_insight_new"
        clTable = "teammember_issue_changelog"

    connection = pymysql.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        passwd=db.pwd,
        database=db.repo.name,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()   
    
    extractIssueFeature(featureTable, insightTable, clTable)

    if choice == 1:
        gunning_fog_index(insightTable)
        num_comments(insightTable)
        num_change(insightTable, clTable)

    cursor.close()
    connection.close()
    print("DB Connection is closed")