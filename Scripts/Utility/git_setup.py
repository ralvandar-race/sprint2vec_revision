import subprocess
import os

def setup_git_credentials():
    """Configure Git credentials"""
    # Set credential helper
    subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'])
    
    # Store credentials
    git_credentials = os.path.expanduser('~/.git-credentials')
    with open(git_credentials, 'w') as f:
        f.write(f"https://{os.getenv('GITHUB_TOKEN')}:x-oauth-basic@github.com\n")
    
    # Set permissions
    os.chmod(git_credentials, 0o600)

if __name__ == "__main__":
    setup_git_credentials()