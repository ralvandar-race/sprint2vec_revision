import os
from pathlib import Path

def process_large_files():
    """Process large files for Git LFS"""
    large_file_extensions = ['.pt', '.pth', '.pkl', '.h5', '.csv']
    project_root = Path('D:/REVA/Capstone1/sprint2vec_revision')
    
    for ext in large_file_extensions:
        large_files = list(project_root.rglob(f'*{ext}'))
        if large_files:
            print(f'Processing {ext} files...')
            for file in large_files:
                rel_path = file.relative_to(project_root)
                print(f'Adding {rel_path} to Git LFS')

if __name__ == '__main__':
    process_large_files()