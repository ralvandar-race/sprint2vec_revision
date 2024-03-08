# Sprint2Vec: a deep characterization of sprints in iterative software development

This repository contains the code, data, models, and experimental results for the paper "Sprint2Vec: a deep characterization of sprints in iterative software development" submitted to IEEE Transactions on Software Engineering (TSE).

## Abstract

Iterative approaches, like Agile Scrum are commonly adopted to enhance the software development process. However, challenges such as schedule and budget overruns still persist in many software projects. Several approaches employ machine learning techniques, particularly classification, to facilitate decision-making in iterative software development. Existing approaches often concentrate on characterizing a sprint to predict solely productivity. We introduce Sprint2Vec, which leverages three aspects of sprint information -- sprint attributes, issue attributes, and the developers involved in a sprint, to comprehensively characterize it for predicting both productivity and quality outcomes of the sprints. Our approach combines traditional feature extraction techniques with automated deep learning-based unsupervised feature learning techniques. We utilize methods like Long Short-Term Memory (LSTM) to enhance our feature learning process. This enables us to learn features from unstructured data, such as textual descriptions of issues and sequences of developer activities. We conducted an evaluation of our approach on two regression tasks: predicting the deliverability (i.e., the amount of work delivered from a sprint) and quality of a sprint (i.e., the amount of delivered work that requires rework). The evaluation results on five well-known open-source projects (Apache, Atlassian, Jenkins, Spring, and Talendforge) demonstrate our approach's superior performance compared to baseline and alternative approaches.

## Directory Structure
```
.
├── Dataset
│   ├── existing
│   ├── onlysprint
│   ├── onlytabular
│   │   ├── productivity
│   │   └── quality_impact
│   ├── sprint2vec
│   │   ├── productivity
│   │   └── quality_impact
│   ├── sprint2vecnotext
│   │   ├── productivity
│   │   └── quality_impact
│   ├── sprintdev
│   │   ├── productivity
│   │   └── quality_impact
│   └── sprintissue
│       ├── productivity
│       └── quality_impact
├── Errors
│   ├── apache
│   ├── jenkins
│   ├── jira
│   ├── spring
│   └── talendforge
├── Models
│   ├── DevModels
│   │   ├── apache
│   │   ├── jenkins
│   │   ├── jira
│   │   ├── spring
│   │   └── talendforge
│   ├── Regressors
│   │   ├── apache
│   │   │   ├── productivity
│   │   │   └── quality_impact
│   │   ├── jenkins
│   │   │   ├── productivity
│   │   │   └── quality_impact
│   │   ├── jira
│   │   │   ├── productivity
│   │   │   └── quality_impact
│   │   ├── spring
│   │   │   ├── productivity
│   │   │   └── quality_impact
│   │   └── talendforge
│   │       ├── productivity
│   │       └── quality_impact
│   └── TextModels
│       ├── BERTOverflow
│       │   └── readme.txt
│       ├── BERTuncased
│       │   └── readme.txt
│       ├── BoW
│       │   ├── apache
│       │   ├── jenkins
│       │   ├── jira
│       │   ├── spring
│       │   └── talendforge
│       ├── SO_W2V
│       │   └── readme.txt
│       ├── TFIDF
│       │   ├── apache
│       │   ├── jenkins
│       │   ├── jira
│       │   ├── spring
│       │   └── talendforge
│       └── seBERT
│           └── readme.txt
├── Predictions
│   ├── apache
│   ├── jenkins
│   ├── jira
│   ├── spring
│   └── talendforge
├── Results
│   ├── Productivity.pdf
│   ├── Quality.pdf
│   ├── apache
│   ├── jenkins
│   ├── jira
│   ├── spring
│   └── talendforge
├── Scripts
│   ├── Data
│   │   ├── DataCollection
│   │   │   ├── GetActivityStream.py
│   │   │   ├── GetBoard.py
│   │   │   ├── GetBoardDetail.py
│   │   │   ├── GetRapidBoard.py
│   │   │   ├── GetSprintIssue.py
│   │   │   └── GetTeammemberIssue.py
│   │   └── DataExtraction
│   │       ├── DeveloperFurtherInfo
│   │       │   ├── Activeness.py
│   │       │   ├── MostPreTypeDev.py
│   │       │   ├── NoDistinctAction.py
│   │       │   ├── RunScripts.py
│   │       │   └── SeqActionIssueType.py
│   │       ├── ExtractActivityIssue.py
│   │       ├── ExtractBoardFeature.py
│   │       ├── ExtractIssueAttribute.py
│   │       ├── ExtractIssueAttributeAtStartDate.py
│   │       ├── ExtractIssueChangeLog.py
│   │       ├── ExtractIssueComment.py
│   │       ├── ExtractIssueComponent.py
│   │       ├── ExtractNoReopen.py
│   │       ├── ExtractQualitative.py
│   │       ├── ExtractQuantitative.py
│   │       ├── ExtractSprintAssignee.py
│   │       ├── ExtractSprintAttribute.py
│   │       ├── ExtractSprintIssue.py
│   │       ├── IssueFurtherInfo
│   │       │   ├── NoChangePrior.py
│   │       │   ├── NoComment.py
│   │       │   ├── ReopenStatus.py
│   │       │   └── RunScripts.py
│   │       └── SprintFurtherInfo
│   │           ├── NoCompletedIssue.py
│   │           ├── NoIssue.py
│   │           ├── NoTeammember.py
│   │           └── RunScripts.py
│   ├── Modeling
│   │   ├── ActGRU.py
│   │   ├── ActLSTM.py
│   │   ├── ExperimentWithAk.py
│   │   ├── LoadData.py
│   │   ├── PrepDataActRNN.py
│   │   ├── PrepEmbFeatures.py
│   │   ├── PrepExisting.py
│   │   ├── PrepSprint2vec.py
│   │   ├── PrepSprint2vecNoText.py
│   │   ├── PrepSprintDev.py
│   │   ├── PrepSprintFeatures.py
│   │   ├── PrepSprintIssue.py
│   │   ├── PrepTabularFeatures.py
│   │   ├── PreprocessData.py
│   │   ├── SplitData.py
│   │   ├── SummarizeResult.py
│   │   ├── TrainActRNN.py
│   │   ├── akregressor.py
│   │   ├── baseline.py
│   │   ├── bert.py
│   │   ├── bow.py
│   │   ├── run_baseline.py
│   │   ├── run_data.py
│   │   ├── run_experimentwithak.py
│   │   ├── run_prepexisting.py
│   │   ├── run_prepsprint.py
│   │   ├── run_prepsprint2vec.py
│   │   ├── run_prepsprint2vecnotext.py
│   │   ├── run_prepsprintdev.py
│   │   ├── run_prepsprintissue.py
│   │   ├── run_preptabular.py
│   │   ├── run_text.py
│   │   ├── run_trainact.py
│   │   ├── seBERTPreprocessor.py
│   │   ├── sow2v.py
│   │   └── tfidf.py
│   ├── act_requirements.txt
│   ├── ak_requirements.txt
│   └── text_requirements.txt
├── Sprint2Vec_Config.xlsx
├── model_training_diagram.png
└── readme.md
```

## Contents
- `Dataset`: Contains the datasets used in the study. The datasets are divided into different folders based on the features used in the study, which are `existing`, `sprint2vec` (our approach), `onlysprint` (ALT 1), `onlytabular` (ALT 2), , `sprintissue` (ALT 3), `sprintdev` (ALT 4), and `sprint2vecnotext` (ALT 5). Each of these folders (excepy `existing` and `onlysprint`) contains two subfolders, `productivity` and `quality_impact` for the two regression tasks.
- `Errors`: Contains the error files for raw errors and absolute errors generated during the model evaluation.
- `Models`: Contains the trained models for the different approaches across the different projects. The models are divided into three subfolders, `DevModels` (for the developer activity models), `TextModels` (for the text models), and `Regressors` (for the regression models). Moreoever, it contains the dependency files which are `act_requirements.txt`, `ak_requirements.txt`, and `text_requirements.txt`.
- `Predictions`: Contains the raw prediction files generated during the model evaluation.
- `Results`: Contains the summary of the results (i.e., MAE, percentage improvement, Wilcoxon p-value with associated significant code, and A12 effect size) for the different approaches across the different projects for the two regression tasks. Also, it contains the raw results (i.e., MAE).
- `Scripts`: Contains two subfolders, `Data` and `Modeling`. The `Data` folder contains the scripts used for data collection and extraction, while the `Modeling` folder contains the scripts used for data preprocessing, model training, and model evaluation.

* Other from above, the directory includes `Sprint2Vec_Config.xlsx` which is the best configuration of `sprint2vec` for each case, and `model_training_diagram.png` which is the diagram of the model training process.

## Getting Started
- Create vitual environment and install the required packages using the following command:
```
pip install -r Scripts/act_requirements.txt
pip install -r Scripts/ak_requirements.txt
pip install -r Scripts/text_requirements.txt
```
Note that the `act_requirements.txt` is for the developer activity models, `ak_requirements.txt` is for the regression models, and `text_requirements.txt` is for the text models.

- Setup GitHub APIs and SQL database.

- Run the scripts in the `Data` folder to collect and extract the data to store in the database. The scripts are divided into two subfolders, `DataCollection` and `DataExtraction` for data collection and data extraction, respectively.

- Run the scripts in the `Modeling` folder to preprocess the data, train the models, and evaluate the models.

## Authors
- Morakot Choetkiertikul
- Peerachai Banyongrakkul
- Chaiyong Ragkhitwetsagul
- Suppawong Tuarob
- Thanwadee Sunetnanta
- Hoa Khanh Dam
