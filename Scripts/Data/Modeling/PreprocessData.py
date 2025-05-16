import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler

def preprocess_data(df):
    """
    Preprocess sprint data
    Args:
        df: Input DataFrame
    Returns:
        DataFrame: Preprocessed data
    """
    # Numeric columns to scale
    numeric_cols = [
        'plan_duration', 'no_issue', 'no_teammember',
        'productivity', 'quality_impact'
    ]
    
    # Create scaler
    scaler = StandardScaler()
    
    # Scale numeric features
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    
    return df

def main(repo_name):
    """Main preprocessing pipeline"""
    # Load data
    base_path = Path("D:/REVA/Capstone1/sprint2vec_revision/Dataset/existing")
    
    for split in ['train', 'test', 'valid']:
        input_file = base_path / f"{repo_name}_existing_{split}.csv.gz"
        print(f"\nProcessing {split} data...")
        
        # Load and preprocess
        df = pd.read_csv(input_file, compression='gzip')
        df_processed = preprocess_data(df)
        
        # Save processed data
        output_file = base_path / f"{repo_name}_processed_{split}.csv.gz"
        df_processed.to_csv(output_file, compression='gzip', index=False)
        print(f"Saved processed data to: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python PreprocessData.py <repository_name>")
        sys.exit(1)
        
    main(sys.argv[1].lower())