import mysql.connector
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        database='sprint2vec',
        user='root',
        password='capstone',
        host='localhost',
        port='3306'
    )

def query_to_dataframe(sql):
    """Execute SQL query and return results as DataFrame"""
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()

def analyze_repository_performance():
    """Analyze repository performance metrics"""
    sql = """
    SELECT 
        repository,
        COUNT(*) as sprint_count,
        AVG(productivity) as avg_productivity,
        AVG(quality_impact) as avg_quality,
        STDDEV(productivity) as std_productivity,
        STDDEV(quality_impact) as std_quality
    FROM sprints
    GROUP BY repository
    """
    return query_to_dataframe(sql)

# In Python console or notebook
from Scripts.Data.Database.db_utils import analyze_repository_performance

# Get performance analysis
performance_df = analyze_repository_performance()
print(performance_df)