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
├── Results
│   ├── Evaluation Results
│   │   ├── apache
│   │   ├── jenkins
│   │   ├── jira
│   │   ├── spring
│   │   └── talendforge
│   ├── Raw Errors
│   │   ├── apache
│   │   ├── jenkins
│   │   ├── jira
│   │   ├── spring
│   │   └── talendforge
│   ├── Predictions
│   │   ├── apache
│   │   ├── jenkins
│   │   ├── jira
│   │   ├── spring
│   │   └── talendforge
│   ├── Productivity.pdf
│   └── Quality.pdf
├── Scripts
│   ├── Data
│   │   ├── DataCollection
│   │   └── DataExtraction
│   │       ├── DeveloperFurtherInfo
│   │       ├── IssueFurtherInfo
│   │       ├── SprintFurtherInfo
│   │       └── MainInfo
│   ├── act_requirements.txt
│   ├── ak_requirements.txt
│   └── text_requirements.txt
├── Sprint2Vec_Config.xlsx
├── model_training_diagram.png
└── readme.md
```

## Contents
- **Dataset**: Contains datasets used in the study, divided into folders based on features utilized:
    - `existing`: Existing approach
    - `sprint2vec`: Our approach
    - `onlysprint`: ALT 1
    - `onlytabular`: ALT 2
    - `sprintissue`: ALT 3
    - `sprintdev`: ALT 4
    - `sprint2vecnotext`: ALT 5
    
    Each subfolder (except `existing` and `onlysprint`) contains:
    - `productivity`: Data for productivity regression task
    - `quality_impact`: Data for quality impact regression task

- **Models**: Contains trained models for different approaches across projects, organized into subfolders:
    - `DevModels`: Developer activity models
    - `TextModels`: Text models
    - `Regressors`: Regression models
    
    Dependency files:
    - `act_requirements.txt`
    - `ak_requirements.txt`
    - `text_requirements.txt`

- **Evaluation Results**: Includes summary files (`Productivity.pdf` and `Quality.pdf`) with experimental results like MAE, percentage improvement, Wilcoxon p-value, and A12 effect size for various approaches across projects. Also contains:
    - `Evaluation Results`: Raw evaluation results (MAE)
    - `Raw Errors`: Error files for raw and absolute errors during evaluation
    - `Predictions`: Raw prediction files during evaluation

- **Scripts**: Contains two subfolders:
    - `Data`: Scripts for data collection and extraction
    - `Modeling`: Scripts for data preprocessing, model training, and evaluation

Additional Files:
- `Sprint2Vec_Config.xlsx`: Best configuration of `sprint2vec` for each case of project and task
- `model_training_diagram.png`: Diagram of the sprint2vec training process

## Getting Started
- **Create Virtual Environments and Install Required Packages:**

    Create vitual environments and install the required packages seperately using the following command:
    ```bash
    pip install -r Scripts/act_requirements.txt
    pip install -r Scripts/ak_requirements.txt
    pip install -r Scripts/text_requirements.txt
    ```
    > Note that the `act_requirements.txt` is for the developer activity models, `ak_requirements.txt` is for the regression models, and `text_requirements.txt` is for the text models.

- **Setup JIRA APIs, SQL Database, and Workspace:**

    Before proceeding, make sure to set up the required steps (e.g., registering for the JIRA accound and getting an access token) for JIRA APIs and a SQL database to suit your requirements. Additionally, ensure you have a suitable workspace configured for your project pipeline.

- **Data Collection and Extraction:**

    Customize the scripts within the Data folder to include your access token for the APIs, database credentials, and workspace specifications. These modifications are necessary to collect and extract data accurately and store it in the database.

    The scripts are segregated into two subfolders:

    - `DataCollection`: Contains scripts for data collection.
    - `DataExtraction`: Contains scripts for data extraction.

    Once customized, execute the scripts to initiate the data collection and extraction processes. For example, you can run the following command to collect the list of boards available in the specified project:
    ```bash
    python DataCollection/GetRapidBoard.py
    ```
    and the following command to extract the attributes of the boards:
    ```bash
    python DataExtraction/MainInfo/ExtractBoardAttribute.py
    ```
    > Note that the data collection and extraction process may take a significant amount of time, depending on the size of the project.

- **Model Training and Evaluation:**

    This process consists of three main components: data preprocessing, feature construction, and modeling. Below are the key scripts involved:

    - **Data Preprocessing**: Scripts like `LoadData.py`, `PreprocessData.py`, and `SplitData.py` are utilized. Some scripts may require customization based on your database and workspace configurations.

    - **Feature Construction**: Scripts such as `PrepSprint2Vec.py` are involved in constructing features.

    - **Modeling**: Scripts like `ActLSTM.py`, `TrainActRNN.py`, and `akregressor.py` are used for modeling. 
    
    Once customized, execute the scripts in the Modeling folder to preprocess the data, train the models, and evaluate them. This is primarily done by running the `run_*.py` files. For example, you can run the following command to load, preprocess, and split the data:
    ```bash
    python Modeling/run_data.py
    ```

*These steps will help you set up your environment and execute the necessary processes to work with the provided data and models.*

## Authors
- Morakot Choetkiertikul
- Peerachai Banyongrakkul
- Chaiyong Ragkhitwetsagul
- Suppawong Tuarob
- Hoa Khanh Dam
- Thanwadee Sunetnanta

## Acknowledgment
This work was financially supported by the Office of the Permanent Secretary, Ministry of Higher Education, Science, Research and Innovation (Grant No. RGNS 64-164).

## Citation
If you use the code, data or models in this repository, please cite the following paper:
```
```