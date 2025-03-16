from pathlib import Path
import argparse
import logging

class Sprint2VecPipeline:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def process_repository(self, repo_name: str):
        """Process a single repository dataset"""
        logging.info(f"Processing repository: {repo_name}")
        
        # 1. Load existing dataset
        dataset_path = self.base_path / "Dataset" / "existing" / f"{repo_name}_existing_train.csv.gz"
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
            
        # 2. Process features
        
        # 3. Train models
        
        # 4. Evaluate results

def main():
    parser = argparse.ArgumentParser(description='Sprint2Vec Pipeline')
    parser.add_argument('repository', help='Repository name to process')
    args = parser.parse_args()
    
    pipeline = Sprint2VecPipeline("D:/REVA/Capstone1/sprint2vec_revision")
    pipeline.process_repository(args.repository)

if __name__ == "__main__":
    main()