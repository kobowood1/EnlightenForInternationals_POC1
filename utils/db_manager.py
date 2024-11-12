import os
import psycopg2
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ['PGDATABASE'],
            user=os.environ['PGUSER'],
            password=os.environ['PGPASSWORD'],
            host=os.environ['PGHOST'],
            port=os.environ['PGPORT']
        )
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS comparison_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                syllabus1_name TEXT NOT NULL,
                syllabus2_name TEXT NOT NULL,
                similarity_score FLOAT NOT NULL,
                topics_compared JSONB,
                learning_outcomes JSONB,
                sections_comparison JSONB,
                recommendations JSONB
            );
            """)
            self.conn.commit()

    def save_comparison(self, syllabus1_name, syllabus2_name, similarity_score, 
                       topics_compared, learning_outcomes, sections_comparison, recommendations):
        with self.conn.cursor() as cur:
            cur.execute("""
            INSERT INTO comparison_history 
            (syllabus1_name, syllabus2_name, similarity_score, topics_compared, 
             learning_outcomes, sections_comparison, recommendations)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                syllabus1_name, syllabus2_name, similarity_score,
                json.dumps(topics_compared), json.dumps(learning_outcomes),
                json.dumps(sections_comparison), json.dumps(recommendations)
            ))
            self.conn.commit()

    def get_comparison_history(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT * FROM comparison_history 
            ORDER BY timestamp DESC
            """)
            columns = ['id', 'timestamp', 'syllabus1_name', 'syllabus2_name', 
                      'similarity_score', 'topics_compared', 'learning_outcomes', 
                      'sections_comparison', 'recommendations']
            results = []
            for row in cur.fetchall():
                result = dict(zip(columns, row))
                for key in ['topics_compared', 'learning_outcomes', 'sections_comparison', 'recommendations']:
                    if result[key]:
                        result[key] = json.loads(result[key])
                results.append(result)
            return results
