import subprocess
from pathlib import Path

def run_command(cmd, desc=None):
    """Run command and print status"""
    if desc:
        print(f"\n=== {desc} ===")
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def main():
    repos = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
    base_dir = Path(__file__).parent
    
    for repo in repos:
        print(f"\n\n=== Processing {repo.upper()} ===")
        
        # Data Processing
        run_command(f"python Scripts/Modeling/LoadData.py {repo}", 
                   "Loading Data")
        
        run_command(f"python Scripts/Modeling/PreprocessData.py {repo}", 
                   "Preprocessing")
        
        run_command(f"python Scripts/Modeling/SplitData.py {repo}", 
                   "Splitting Data")
        
        # Feature Construction
        run_command(f"python Scripts/Modeling/bow.py {repo}", 
                   "Generating BOW Features")
        
        run_command(f"python Scripts/Modeling/PrepSprint2vec.py {repo} bow full lstm 16 mean",
                   "Preparing Sprint2Vec Features")
        
        # Model Training
        run_command(f"python Scripts/Modeling/TrainActRNN.py {repo} lstm 32",
                   "Training RNN Model")
        
        # Evaluation
        for task in ['productivity', 'quality_impact']:
            run_command(f"python Scripts/Modeling/ExperimentWithAk.py {repo} {task} sprint2vec_bow_mean",
                       f"Evaluating {task}")

if __name__ == "__main__":
    main()