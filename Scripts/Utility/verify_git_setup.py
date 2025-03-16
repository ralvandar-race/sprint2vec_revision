import subprocess
import sys

def verify_git_setup():
    """Verify git repository setup"""
    try:
        # Check if git is initialized
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      check=True, 
                      capture_output=True)
    except subprocess.CalledProcessError:
        print("Initializing git repository...")
        subprocess.run(['git', 'init'], check=True)
    
    # Check remote
    result = subprocess.run(['git', 'remote', '-v'], 
                          capture_output=True, 
                          text=True)
    
    if 'origin' not in result.stdout:
        print("Adding remote origin...")
        subprocess.run([
            'git', 'remote', 'add', 'origin',
            'https://github.com/ralvandar-race/sprint2vec_revision.git'
        ], check=True)
    
    print("Git setup verified successfully")

if __name__ == "__main__":
    verify_git_setup()