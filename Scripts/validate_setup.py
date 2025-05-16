import os
import pandas as pd
import sys
from pathlib import Path

class Sprint2VecValidator:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.required_dirs = [
            'Dataset/existing',
            'Dataset/sprint2vec',
            'Scripts/Data/DataCollection',
            'Scripts/Data/DataExtraction',
            'Scripts/Data/Modeling',
            'Models',
            'Results'
        ]
        
    def validate_directory_structure(self):
        """Validate required directories exist"""
        print("\n🔍 Checking Directory Structure...")
        missing_dirs = []
        for dir_path in self.required_dirs:
            full_path = self.base_path / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
                print(f"❌ Missing: {dir_path}")
            else:
                print(f"✅ Found: {dir_path}")
        return len(missing_dirs) == 0

    def validate_dataset_files(self):
        """Validate required dataset files"""
        print("\n🔍 Checking Dataset Files...")
        repos = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
        splits = ['train', 'test', 'valid']
        missing_files = []
        
        for repo in repos:
            for split in splits:
                file_path = self.base_path / 'Dataset/existing' / f'{repo}_existing_{split}.csv.gz'
                if not file_path.exists():
                    missing_files.append(f'{repo}_{split}')
                    print(f"❌ Missing: {file_path.name}")
                else:
                    print(f"✅ Found: {file_path.name}")
        return len(missing_files) == 0

    def validate_scripts(self):
        """Validate required Python scripts"""
        print("\n🔍 Checking Scripts...")
        required_scripts = [
            'Scripts/Data/DataCollection/GetBoard.py',
            'Scripts/Data/DataCollection/GetRapidBoard.py',
            'Scripts/Data/Modeling/LoadData.py',
            'Scripts/Data/Modeling/PreprocessData.py'
        ]
        missing_scripts = []
        for script in required_scripts:
            script_path = self.base_path / script
            if not script_path.exists():
                missing_scripts.append(script)
                print(f"❌ Missing: {script}")
            else:
                print(f"✅ Found: {script}")
        return len(missing_scripts) == 0

if __name__ == "__main__":
    validator = Sprint2VecValidator("D:/REVA/Capstone1/sprint2vec_revision")
    
    # Run validations
    structure_valid = validator.validate_directory_structure()
    data_valid = validator.validate_dataset_files()
    scripts_valid = validator.validate_scripts()
    
    # Summary
    print("\n📊 Validation Summary:")
    print(f"Directory Structure: {'✅ Valid' if structure_valid else '❌ Invalid'}")
    print(f"Dataset Files: {'✅ Valid' if data_valid else '❌ Invalid'}")
    print(f"Scripts: {'✅ Valid' if scripts_valid else '❌ Invalid'}")