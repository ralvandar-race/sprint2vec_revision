import shap
import autokeras as ak
import json
import numpy as np
from tensorflow.keras.models import load_model
import pandas as pd
import matplotlib.pyplot as plt

repo_list = [
    "apache", 
    "jenkins", 
    "jira", 
    "spring", 
    "talendforge"
]
task_list = [
    "productivity", 
    "quality_impact"
]
feature_list = [
    "all",
    "no_auto",
    "no_manual"
]

shap.initjs()

for repo in repo_list:
    for task in task_list:
        for feature in feature_list:
            # Load the best model
            best_model_name = json.load(open("<best_model_config_json>".format(task)))[repo]
            best_model = load_model("<best_model_path>".format(repo, task, best_model_name), custom_objects=ak.CUSTOM_OBJECTS)
            train_df = pd.read_csv("<train_data>".format(task, repo, "_".join(best_model_name.split("_")[:-1])))
            train_df = train_df.drop(['productivity', 'quality_impact'], axis=1)
            print(train_df.shape)
            cols = train_df.columns.tolist()
            
            # Get lists of different types of features
            manual_cols = [c for c in cols if not c.startswith('i_text_') and not c.startswith('d_rnn_feats_')]
            auto_cols = [c for c in cols if c.startswith('i_text_') or c.startswith('d_rnn_feats_')]
            manual_index = [cols.index(c) for c in manual_cols]
            auto_index = [cols.index(c) for c in auto_cols]
            
            # Select the features to use
            if feature == "no_auto":
                current_cols = manual_cols
                current_index = manual_index
            elif feature == "no_manual":
                current_cols = auto_cols
                current_index = auto_index
            else:
                current_cols = cols
                current_index = list(range(len(cols)))
            # print(current_cols)
            X_train = train_df.values
            
            # Create a summary of the training data
            X_train_summary = shap.kmeans(X_train, 10)

            # Load the test data
            test_df = pd.read_csv("<test_data>".format(task, repo, "_".join(best_model_name.split("_")[:-1])))
            test_df = test_df.drop(['productivity', 'quality_impact'], axis=1)
            print(test_df.shape)
            X_test = test_df.values

            try:
                shap_values = np.load("<shap_values>".format(repo, task), allow_pickle=True)
            except:
                # Create the SHAP values
                kernel_explainer = shap.KernelExplainer(best_model.predict, X_train_summary)
                shap_values = kernel_explainer.shap_values(X_test)[0]

                # Save the SHAP values
                np.save("<shap_values>".format(repo, task), shap_values)

            print("shap_values shape: {}".format(shap_values.shape))