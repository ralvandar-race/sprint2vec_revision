import sys

class RepoConfig():

    def __init__(self, name, domain, userpass, storypoint1):
        self.name = name
        self.domain = domain
        self.userpass = userpass
        self.storypoint1 = storypoint1

def createRepo():
    while True:
        try:
            choice = int(input("Enter the number to select the repository\n[1] Apache\n[2] Jenkins\n[3] Jira\n[4] Spring\n[5] Talendforge\n"))
            if choice <= 0 and choice > 5:
                print("Try again!!!")
            else:
                if choice == 1:
                    repo = RepoConfig("apache", "issues.apache.org/jira", "<username>:<password>", "12310293")
                elif choice == 2:
                    repo = RepoConfig("jenkins", "issues.jenkins.io", "<username>:<password>", "10332")
                elif choice == 3:
                    repo = RepoConfig("jira", "jira.atlassian.com", "<username>:<password>", "10571")
                elif choice == 4:
                    repo = RepoConfig("spring", "jira.spring.io", "<username>:<password>", "10142")
                elif choice == 5:
                    repo = RepoConfig("talendforge", "jira.talendforge.org", "<username>:<password>", "10150")
                print("\n================= WELCOME TO {} =================\n".format(repo.name.upper()))
                return repo
        except KeyboardInterrupt:
            print("Interrupted by user")
            sys.exit()
        except Exception:
            print("Only number is valid!!!")


            