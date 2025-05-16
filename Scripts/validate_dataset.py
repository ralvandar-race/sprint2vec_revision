import os
import pandas as pd
import numpy as np
from pathlib import Path

def analyze_csv_gz(file_path):
    """Analyze a single CSV.GZ file"""
    try:
        df = pd.read_csv(file_path, compression='gzip')
        return {
            'file': file_path.name,
            'rows': len(df),
            'columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'target_vars': [col for col in df.columns if col in ['productivity', 'quality_impact']],
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
        }
    except Exception as e:
        return {'file': file_path.name, 'error': str(e)}

def validate_dataset():
    """Validate and summarize all dataset files"""
    base_path = Path(r"D:\REVA\Capstone1\sprint2vec_revision\Dataset")
    approaches = ['existing', 'onlysprint', 'onlytab', 'sprintissue', 'sprintdev', 'sprint2vec']
    
    summary = []
    
    for approach in approaches:
        approach_path = base_path / approach
        if not approach_path.exists():
            print(f"Warning: {approach} folder not found")
            continue
            
        print(f"\n=== Analyzing {approach} approach ===")
        for file_path in approach_path.glob('*.csv.gz'):
            result = analyze_csv_gz(file_path)
            summary.append({
                'approach': approach,
                **result
            })
            
            if 'error' in result:
                print(f"Error in {file_path.name}: {result['error']}")
            else:
                print(f"\nFile: {result['file']}")
                print(f"Rows: {result['rows']:,}")
                print(f"Columns: {result['columns']}")
                print(f"Missing Values: {result['missing_values']:,}")
                print(f"Memory Usage: {result['memory_usage']:.2f} MB")
                if result['target_vars']:
                    print(f"Target Variables: {', '.join(result['target_vars'])}")

    return pd.DataFrame(summary)

if __name__ == "__main__":
    print("Starting Dataset Validation...")
    summary_df = validate_dataset()
    
    # Save summary to CSV
    output_path = r"D:\REVA\Capstone1\sprint2vec_revision\Dataset\validation_summary.csv"
    summary_df.to_csv(output_path, index=False)
    print(f"\nSummary saved to: {output_path}")