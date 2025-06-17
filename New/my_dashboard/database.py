# database.py (หรือวางไว้ตอนต้นใน app.py)
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine("sqlite:///app_data.db", echo=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

class UploadHistory(Base):
    __tablename__ = 'upload_logs'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    filename = Column(String)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# ฟังก์ชันที่ใช้ในแอป
def add_user(username, password):
    if session.query(User).filter_by(username=username).first():
        return False
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return True

def validate_user(username, password):
    return session.query(User).filter_by(username=username, password=password).first()

def log_upload(username, filename):
    log = UploadHistory(username=username, filename=filename)
    session.add(log)
    session.commit()

def get_user_logs(username):
    return session.query(UploadHistory).filter_by(username=username).all()
