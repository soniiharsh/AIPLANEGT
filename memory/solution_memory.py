import sqlite3
import json
from datetime import datetime

class SolutionMemory:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                input_type TEXT,
                raw_input TEXT,
                parsed_problem TEXT,
                solution TEXT,
                verification TEXT,
                user_feedback TEXT,
                is_correct BOOLEAN
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store(self, data):
        """Store solution attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO solutions 
            (timestamp, input_type, raw_input, parsed_problem, 
             solution, verification, user_feedback, is_correct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            data.get("input_type"),
            data.get("raw_input"),
            json.dumps(data.get("parsed_problem")),
            json.dumps(data.get("solution")),
            json.dumps(data.get("verification")),
            data.get("user_feedback"),
            data.get("is_correct")
        ))
        
        conn.commit()
        solution_id = cursor.lastrowid
        conn.close()
        
        return solution_id
    
    def retrieve_similar(self, problem_text, limit=3):
        """Find similar solved problems"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple keyword matching (can be improved with embeddings)
        cursor.execute("""
            SELECT * FROM solutions
            WHERE is_correct = 1
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in results]
    
    def _row_to_dict(self, row):
        """Convert DB row to dict"""
        return {
            "id": row[0],
            "timestamp": row[1],
            "parsed_problem": json.loads(row[3]),
            "solution": json.loads(row[4])
        }