import os
from pathlib import Path
import logging

def scan_project():
    """Scan project directory for model and related files"""
    project_root = Path("D:/REVA/Capstone1/sprint2vec_revision")
    
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Define expected project structure
    expected_dirs = [
        'Scripts/Models',
        'Scripts/Data/Processing',
        'Scripts/Data/Analysis',
        'Results',
        'Models'
    ]
    
    # Create missing directories
    for dir_path in expected_dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
    # Scan for model files
    logging.info("\nScanning for model files...")
    model_files = list(project_root.rglob("*model*.pt"))
    if model_files:
        logging.info("Found model files:")
        for model in model_files:
            logging.info(f"- {model.relative_to(project_root)}")
    else:
        logging.warning("No model files (*.pt) found")
    
    # Scan for Python files
    logging.info("\nScanning for source files...")
    for py_file in project_root.rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class Sprint2Vec' in content:
                logging.info(f"Found model definition in: {py_file.relative_to(project_root)}")

if __name__ == "__main__":
    scan_project()