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
feature = 'no_auto'

for repo in repo_list:
    for task in task_list:
        best_model_name = json.load(open("<best_model_config_json>".format(task)))[repo]
        best_model = load_model("<best_model_path>".format(repo, task, best_model_name), custom_objects=ak.CUSTOM_OBJECTS)
        train_df = pd.read_csv("<train_data>".format(task, repo, "_".join(best_model_name.split("_")[:-1])))
        train_df = train_df.drop(['productivity', 'quality_impact'], axis=1)
        print(train_df.shape)
        cols = train_df.columns.tolist()
        manual_cols = [c for c in cols if not c.startswith('i_text_') and not c.startswith('d_rnn_feats_')]
        auto_cols = [c for c in cols if c.startswith('i_text_') or c.startswith('d_rnn_feats_')]

        shap_values = np.load("<shap_values>".format(repo, task), allow_pickle=True)
        result_df = pd.DataFrame(shap_values, columns = cols)

        ####### with direction #######
        vals = result_df.values.mean(0)
        shap_df = pd.DataFrame(list(zip(cols, vals)),
                                        columns=['col_name','feat_imp'])

        shap_df['direction'] = '+'
        shap_df.loc[shap_df['feat_imp'] < 0, 'direction'] = '-'
        shap_df['feat_imp'] = shap_df['feat_imp'].abs()
        shap_df = shap_df.sort_values(by='feat_imp', ascending=False)

        # drop auto col_name
        shap_df = shap_df[~shap_df.col_name.isin(auto_cols)]

        # normalize shap values to 1 for max
        shap_df['norm_feat_imp'] = (1.0 / shap_df['feat_imp'].max()) * shap_df['feat_imp']

        # reordering the columns
        shap_df = shap_df[['col_name', 'feat_imp', 'norm_feat_imp', 'direction']]

        # dump to csv
        shap_df.to_csv('<shap_values_with_direction>'.format(repo, task, feature), index=False)

        pros_df = shap_df[shap_df['direction'] == '+']
        cons_df = shap_df[shap_df['direction'] == '-']

        # dump top 5 pros and cons to csv
        pros_df[['col_name', 'norm_feat_imp']].head(5).to_csv('shap_feat_imp_df/{}_{}_{}_pos.csv'.format(repo, task, feature), index=False)
        cons_df[['col_name', 'norm_feat_imp']].head(5).to_csv('shap_feat_imp_df/{}_{}_{}_neg.csv'.format(repo, task, feature), index=False)

        ####### without direction #######
        vals = np.abs(result_df.values).mean(0)
        shap_df = pd.DataFrame(list(zip(cols, vals)), columns=['col_name','feat_imp'])
        shap_df = shap_df[~shap_df.col_name.isin(auto_cols)].sort_values(by='feat_imp', ascending=False)

        # normalize shap values to max = 1
        shap_df['norm_feat_imp'] = (1.0 / shap_df['feat_imp'].max()) * shap_df['feat_imp']

        # dump to csv
        shap_df.to_csv('<shap_values_without_direction>'.format(repo, task, feature), index=False)

        print("Done for {} in {}".format(task, repo))