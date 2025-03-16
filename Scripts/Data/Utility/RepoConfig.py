import sys
import os

class RepoConfig:
    def __init__(self, name):
        self.name = name
        self.data_path = f"D:/REVA/Capstone1/sprint2vec_revision/Dataset/existing/{name}_existing"
    
    @staticmethod
    def createRepo(name):
        valid_repos = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
        if name not in valid_repos:
            raise ValueError(f"Unknown repository: {name}")
        return RepoConfig(name)

def getExistingRepo(name):
    """
    Get configuration for existing repository data
    Args:
        name: Repository name ('apache', 'jenkins', 'jira', 'spring', 'talendforge')
    Returns:
        RepoConfig object
    """
    repo_configs = {
        "apache": ("issues.apache.org/jira", "12310293"),
        "jenkins": ("issues.jenkins.io", "10332"),
        "jira": ("jira.atlassian.com", "10571"),
        "spring": ("jira.spring.io", "10142"),
        "talendforge": ("jira.talendforge.org", "10150")
    }
    
    if name not in repo_configs:
        raise ValueError(f"Unknown repository: {name}")
        
    domain, storypoint1 = repo_configs[name]
    return createRepo(name, domain, "username:password", storypoint1)


