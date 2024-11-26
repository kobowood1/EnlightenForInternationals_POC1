import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
Session = sessionmaker(bind=engine)

# Create base class for declarative models
Base = declarative_base()

class ComparisonHistory(Base):
    __tablename__ = 'comparison_history'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    syllabus1_name = Column(String(255))
    syllabus2_name = Column(String(255))
    similarity_score = Column(Float)
    comparison_data = Column(JSON)
    recommendations = Column(JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'syllabus1_name': self.syllabus1_name,
            'syllabus2_name': self.syllabus2_name,
            'similarity_score': self.similarity_score,
            'comparison_data': self.comparison_data,
            'recommendations': self.recommendations
        }

# Create tables
Base.metadata.create_all(engine)

def get_session():
    """Get a new database session."""
    return Session()

def save_comparison(syllabus1_name, syllabus2_name, similarity_score, comparison_data, recommendations):
    """Save a comparison to the database."""
    session = get_session()
    try:
        history = ComparisonHistory(
            syllabus1_name=syllabus1_name,
            syllabus2_name=syllabus2_name,
            similarity_score=similarity_score,
            comparison_data=comparison_data,
            recommendations=recommendations
        )
        session.add(history)
        session.commit()
        return history.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_comparison_history(limit=10):
    """Get recent comparison history."""
    session = get_session()
    try:
        history = session.query(ComparisonHistory)\
            .order_by(ComparisonHistory.timestamp.desc())\
            .limit(limit)\
            .all()
        return [h.to_dict() for h in history]
    finally:
        session.close()
