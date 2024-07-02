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
    db = DBConfig("<host>", "<port>", "<user>", "<password>", repo, "<data_folder>")
    return db


            