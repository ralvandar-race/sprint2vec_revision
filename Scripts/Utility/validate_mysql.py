import mysql.connector
from pathlib import Path
import pandas as pd
import logging

class MySQLValidator:
    def __init__(self):
        self.conn_params = {
            'host': 'localhost',
            'user': 'root',
            'password': 'capstone',
            'database': 'sprint2vec'
        }
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def validate_database(self):
        """Validate MySQL database content"""
        try:
            conn = mysql.connector.connect(**self.conn_params)
            cursor = conn.cursor()

            # Check tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'sprint2vec'
            """)
            tables = [t[0] for t in cursor.fetchall()]
            required_tables = ['sprints', 'issues', 'developer_activities']
            
            for table in required_tables:
                if table not in tables:
                    logging.error(f"Missing table: {table}")
                    return False

            # Check data counts per repository
            repositories = ['apache', 'jenkins', 'jira', 'spring', 'talendforge']
            for repo in repositories:
                cursor.execute(f"""
                    SELECT COUNT(*) as sprint_count,
                           AVG(productivity) as avg_productivity,
                           AVG(quality_impact) as avg_quality
                    FROM sprints 
                    WHERE repository = '{repo}'
                """)
                result = cursor.fetchone()
                if result[0] == 0:
                    logging.error(f"No data found for repository: {repo}")
                    return False
                logging.info(f"{repo}: {result[0]} sprints, "
                           f"avg_productivity={result[1]:.3f}, "
                           f"avg_quality={result[2]:.3f}")

            return True

        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    validator = MySQLValidator()
    if validator.validate_database():
        print("\n✅ Database validation successful")
    else:
        print("\n❌ Database validation failed")