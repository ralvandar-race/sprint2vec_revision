import shap
import autokeras as ak
import json
import numpy as np
from tensorflow.keras.models import load_model
import pandas as pd

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

for repo in repo_list:
    for task in task_list:
        # Load the best model
        best_model_name = json.load(open("<best_model_config_json>".format(task)))[repo]
        best_model = load_model("<best_model_path>".format(repo, task, best_model_name), custom_objects=ak.CUSTOM_OBJECTS)
        train_df = pd.read_csv("<train_data>".format(task, repo, "_".join(best_model_name.split("_")[:-1])))
        train_df = train_df.drop(['productivity', 'quality_impact'], axis=1)
        print(train_df.shape)
        cols = train_df.columns.tolist()

        # Get lists of different types of features
        manual_cols = [c for c in cols if not c.startswith('i_text_') and not c.startswith('d_rnn_feats_')]
        sprint_cols = [c for c in manual_cols if c.startswith('s_')]
        issue_cols = [c for c in manual_cols if c.startswith('i_')]
        dev_cols = [c for c in manual_cols if c.startswith('d_')]
        auto_cols = [c for c in cols if c.startswith('i_text_') or c.startswith('d_rnn_feats_')]
        text_cols = [c for c in auto_cols if c.startswith('i_text_')]
        act_cols = [c for c in auto_cols if c.startswith('d_rnn_feats_')]

        print("All Features: ", len(cols))
        print("Manual Features: ", len(manual_cols))
        print("sprint Features: {} \nissue Features: {} \ndeveloper Features: {}".format(len(sprint_cols), len(issue_cols), len(dev_cols)))
        print("Auto Features: ", len(auto_cols))
        print("Text Features: {} \nActivity Features: {}".format(len(text_cols), len(act_cols)))

        print(sprint_cols)
        print(issue_cols)
        print(dev_cols)
        print(text_cols)
        print(act_cols)

        # Load SHAP values
        shap_values = np.load("<shap_values>".format(repo, task), allow_pickle=True)
        result_df = pd.DataFrame(shap_values, columns = cols)

        # Calculate feature importance by taking the mean of absolute SHAP values
        vals = np.abs(result_df.values).mean(0)
        shap_df = pd.DataFrame(list(zip(cols, vals)), columns=['col_name','feat_imp'])

        # Calculate feature importance for different groups of features
        sprint_vals = shap_df[shap_df['col_name'].isin(sprint_cols)]['feat_imp'].mean()
        issue_vals = shap_df[shap_df['col_name'].isin(issue_cols)]['feat_imp'].mean()
        dev_vals = shap_df[shap_df['col_name'].isin(dev_cols)]['feat_imp'].mean()
        text_vals = shap_df[shap_df['col_name'].isin(text_cols)]['feat_imp'].mean()
        act_vals = shap_df[shap_df['col_name'].isin(act_cols)]['feat_imp'].mean()

        # Save the feature importance values
        group_shap_df = pd.DataFrame(list(zip(['sprint', 'issue', 'developer', 'text', 'activity'], [sprint_vals, issue_vals, dev_vals, text_vals, act_vals])), columns=['col_name','feat_imp'])
        group_shap_df = group_shap_df.sort_values(by='feat_imp', ascending=False)
        group_shap_df['norm_feat_imp'] = (1.0 / group_shap_df['feat_imp'].max()) * group_shap_df['feat_imp']
        group_shap_df = group_shap_df[['col_name', 'feat_imp', 'norm_feat_imp']]
        group_shap_df.to_csv('<shap_group_feat_imp>'.format(repo, task), index=False)