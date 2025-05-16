import mysql.connector
import pandas as pd
from pathlib import Path

class SprintVecDatabase:
    def __init__(self):
        self.conn_params = {
            'database': 'sprint2vec',
            'user': 'root',
            'password': 'capstone',  # Change as per your MySQL setup
            'host': 'localhost',
            'port': '3306'
        }
        
    def create_database(self):
        """Create database if not exists"""
        conn = mysql.connector.connect(
            host=self.conn_params['host'],
            user=self.conn_params['user'],
            password=self.conn_params['password']
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.conn_params['database']}")
        conn.close()
        
    def create_tables(self):
        """Create required tables based on paper schema"""
        commands = [
            """
            CREATE TABLE IF NOT EXISTS sprints (
                sprint_id INT AUTO_INCREMENT PRIMARY KEY,
                repository VARCHAR(50),
                plan_duration INT,
                no_issue INT,
                no_teammember INT,
                productivity FLOAT,
                quality_impact FLOAT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS issues (
                issue_id INT AUTO_INCREMENT PRIMARY KEY,
                sprint_id INT,
                description TEXT,
                no_components INT,
                fog_index FLOAT,
                no_comments INT,
                no_changes INT,
                FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS developer_activities (
                activity_id INT AUTO_INCREMENT PRIMARY KEY,
                sprint_id INT,
                developer_id VARCHAR(100),
                activity_type VARCHAR(50),
                timestamp DATETIME,
                FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id)
            )
            """
        ]
        
        conn = None
        try:
            conn = mysql.connector.connect(**self.conn_params)
            cur = conn.cursor()
            for command in commands:
                cur.execute(command)
            conn.commit()
            print("Tables created successfully")
        except mysql.connector.Error as error:
            print(f"Error: {error}")
        finally:
            if conn is not None:
                conn.close()

    def load_dataset(self, repository):
        """Load dataset into database"""
        base_path = Path("D:/REVA/Capstone1/sprint2vec_revision/Dataset/existing")
        splits = ['train', 'test', 'valid']
        
        for split in splits:
            file_path = base_path / f"{repository}_existing_{split}.csv.gz"
            if file_path.exists():
                df = pd.read_csv(file_path, compression='gzip')
                self._insert_sprint_data(df, repository)
                print(f"Loaded {split} data for {repository}")

    def _insert_sprint_data(self, df, repository):
        """Insert sprint data into database"""
        conn = None
        try:
            conn = mysql.connector.connect(**self.conn_params)
            cur = conn.cursor()
            
            for _, row in df.iterrows():
                cur.execute(
                    """
                    INSERT INTO sprints 
                    (repository, plan_duration, no_issue, no_teammember, 
                     productivity, quality_impact)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (repository, row['plan_duration'], row['no_issue'],
                     row['no_teammember'], row['productivity'], row['quality_impact'])
                )
            
            conn.commit()
        except mysql.connector.Error as error:
            print(f"Error: {error}")
        finally:
            if conn is not None:
                conn.close()

    def verify_data(self):
        """Verify loaded data in database"""
        conn = None
        try:
            conn = mysql.connector.connect(**self.conn_params)
            cur = conn.cursor()
            
            # Check counts per repository
            cur.execute("""
                SELECT repository, 
                       COUNT(*) as sprint_count,
                       AVG(productivity) as avg_productivity,
                       AVG(quality_impact) as avg_quality
                FROM sprints 
                GROUP BY repository
            """)
            
            print("\nData Summary:")
            print("Repository | Sprints | Avg Productivity | Avg Quality")
            print("-" * 50)
            for (repo, count, prod, qual) in cur:
                print(f"{repo:10} | {count:7} | {prod:14.3f} | {qual:10.3f}")
                
        except mysql.connector.Error as error:
            print(f"Error: {error}")
        finally:
            if conn is not None:
                conn.close()

if __name__ == "__main__":
    # Initialize database
    db = SprintVecDatabase()
    
    # Create database and tables
    db.create_database()
    db.create_tables()
    
    # Load data for each repository
    repositories = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
    for repo in repositories:
        print(f"\nProcessing {repo}...")
        db.load_dataset(repo)