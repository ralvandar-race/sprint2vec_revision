import logging
import torch
from pathlib import Path

def verify_training():
    results_path = Path("Results")
    if not results_path.exists():
        results_path.mkdir(parents=True)
        
    logging.info("Verifying training outputs...")
    
    # Check saved models
    models_path = Path("Models")
    for repo in ['apache', 'jenkins', 'jira', 'spring', 'talendforge']:
        model_file = models_path / f"{repo}_model.pt"
        if model_file.exists():
            state_dict = torch.load(model_file)
            logging.info(f"{repo} model parameters: {len(state_dict.keys())}")