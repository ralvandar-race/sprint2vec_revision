import pandas as pd
import json
import sys
import stat_test

# disable future warnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

try:
    task = sys.argv[1]
except:
    print("No argument")
    sys.exit()

print("task: {}".format(task))

repo = [    
    'apache',
    'jira', 
    'jenkins',
    'spring', 
    'talendforge'
]

texts = [
    'bow',
    'tfidf',
    'sow2v',
    'bertuncased',
    'bertoverflow',
    'sebert',
]

acts = [
    'full',
    'last'
]

pools = [
    'mean',
    'max',
    'min'
]

approaches = [
    'averagenoise',
    'random',
    'linear',
    'existing',
    'onlysprint'
] + [
    'onlytabular_{}'.format(pool)
    for pool in pools
] + [
    'sprintissue_{}_{}'.format(text, pool)
    for text in texts
    for pool in pools
] + [
    'sprintdev_{}_{}'.format(act, pool)
    for act in acts
    for pool in pools
] + [
    'sprint2vecnotext_{}_{}'.format(act, pool)
    for act in acts
    for pool in pools
] + [
    'sprint2vec_{}_{}_{}'.format(text, act, pool)
    for text in texts
    for act in acts
    for pool in pools 
]

def get_results(data_set, task):
    count = 0
    # read results
    for rep in repo:
        for approach in approaches:
            # print("clf: {}".format(clf))
            if approach.split('_')[0] in ['sprintdev', 'sprint2vecnotext', 'sprint2vec']:
                with open('Act Models/best_config.json', 'r') as f:
                    best_act_config = json.load(f)[rep]
                approach = "{}_{}_{}_{}".format("_".join(approach.split('_')[:-1]), best_act_config['rnn'], best_act_config['dim'], approach.split('_')[-1])
            if approach not in ['averagenoise', 'random', 'linear']:
                approach = "{}_ak".format(approach)
            if count == 0:
                result_path = 'Results/{}/{}/{}_{}_{}_{}.csv'.format(rep, approach.split('_')[0], approach, task, data_set, rep)
                df = pd.read_csv(result_path)   
                df.insert(0, 'repo', rep)
                df.insert(1, 'approach', approach.split('_')[0])
                df.insert(2, 'full_approach', approach)
            else:
                result_path = 'Results/{}/{}/{}_{}_{}_{}.csv'.format(rep, approach.split('_')[0], approach, task, data_set, rep)
                df = df.append(pd.read_csv(result_path), ignore_index=True)
                df.loc[count, 'repo'] = rep
                df.loc[count, 'approach'] = approach.split('_')[0]
                df.loc[count, 'full_approach'] = approach
            count += 1
    return df

print("Getting valid results...")
valid_df = get_results('valid', task)
# print(valid_df.head())

min_val_df = valid_df[['repo', 'approach', 'full_approach', 'mae']].groupby(['repo', 'approach'], sort=False).agg({'mae': 'min'}).reset_index()
min_val_df = min_val_df.merge(valid_df[['repo', 'approach', 'full_approach', 'mae']], on=['repo', 'approach', 'mae'], how='left')
min_val_df = min_val_df.drop_duplicates(subset=['repo', 'approach'], keep='first')

print("Getting test results...")
test_df = get_results('test', task)

min_val_df = min_val_df.rename(columns={'mae': 'valid_mae'})
test_df = test_df.rename(columns={'mae': 'test_mae'})
best_df = min_val_df.merge(test_df[['repo', 'approach', 'full_approach', 'test_mae']], on=['repo', 'approach', 'full_approach'], how='left')
best_df = best_df[['repo', 'approach', 'full_approach', 'valid_mae', 'test_mae']]
best_df = best_df.drop(columns=['valid_mae'])
best_df = best_df.rename(columns={'test_mae': 'mae'})

# percentage improvement
print("Calculating percentage improvement...")
best_df['% imp'] = float('nan')
for rep in repo:
    best_df.loc[best_df['repo'] == rep, '% imp'] = best_df.loc[best_df['repo'] == rep, 'mae'].apply(lambda x: (best_df.loc[(best_df['repo'] == rep) & (best_df['approach'] == 'sprint2vec'), 'mae'].values[0] - x) / best_df.loc[(best_df['repo'] == rep) & (best_df['approach'] == 'sprint2vec'), 'mae'].values[0] * 100 * -1)
best_df['imp?'] = best_df['% imp'].apply(lambda x: 'Yes' if x > 0 else 'No')

# stat test
print("Running statistical test...")
best_df['wilcoxon (abs)'] = float('nan')
best_df['sig. code (abs)'] = ''
best_df['sig? (abs)'] = ''
best_df['A12 (abs)'] = float('nan')

data_set = 'test'
sprint2vec_best_dict = {}
for rep in repo:
    sprint2vec_full_approach = best_df.loc[(best_df['repo'] == rep) & (best_df['approach'] == 'sprint2vec'), 'full_approach'].values[0]
    sprint2vec_best_dict[rep] = sprint2vec_full_approach
    with open('Error/{}/{}/{}_{}_{}_{}_abs.txt'.format(rep, 'sprint2vec', sprint2vec_full_approach, task, data_set, rep), 'r') as f:
        sprint2vec_abs = f.read().splitlines()
        sprint2vec_abs = [float(i) for i in sprint2vec_abs]
    other_full_approaches = best_df.loc[(best_df['repo'] == rep) & (best_df['approach'] != 'sprint2vec'), 'full_approach'].values
    for other_full_approach in other_full_approaches:
        with open('Error/{}/{}/{}_{}_{}_{}_abs.txt'.format(rep, other_full_approach.split('_')[0], other_full_approach, task, data_set, rep), 'r') as f:
            other_abs = f.read().splitlines()
            other_abs = [float(i) for i in other_abs]
        wilcoxon_abs = stat_test.wilcoxon_test(sprint2vec_abs, other_abs)
        A12_abs = stat_test.VD_A(other_abs, sprint2vec_abs) # error lower is better so we swap the order
        best_df.loc[(best_df['repo'] == rep) & (best_df['full_approach'] == other_full_approach), 'wilcoxon (abs)'] = wilcoxon_abs[0] if wilcoxon_abs[0] >= 0.001 else '<0.001'
        best_df.loc[(best_df['repo'] == rep) & (best_df['full_approach'] == other_full_approach), 'sig. code (abs)'] = wilcoxon_abs[1]
        best_df.loc[(best_df['repo'] == rep) & (best_df['full_approach'] == other_full_approach), 'sig? (abs)'] = wilcoxon_abs[2]
        best_df.loc[(best_df['repo'] == rep) & (best_df['full_approach'] == other_full_approach), 'A12 (abs)'] = A12_abs[0]
        
best_df = best_df.round(3)
# save sprint2vec best
print("Saving sprint2vec best...")
with open('Results/sprint2vec_{}_best.json'.format(task), 'w') as f:
    json.dump(sprint2vec_best_dict, f, indent=4)
print("Saving final report...")
best_df.to_csv('Results/{}_final_results.csv'.format(task), index=False)