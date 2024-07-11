import sys

class DBConfig():

    def __init__(self, host, port, user, pwd, repo, folder):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.repo = repo
        self.folder = folder

def createDB(repo):
    """
    Create a new DBConfig object with the given repository name
    <host>: The host of the database
    <port>: The port of the database
    <user>: The user used to connect to the database
    <password>: The password associated with the user
    <data_folder>: The folder where the data is stored

    :param repo: The name of the repository
    :return: The DBConfig object
    """
    db = DBConfig("<host>", "<port>", "<user>", "<password>", repo, "<data_folder>")
    return db


            