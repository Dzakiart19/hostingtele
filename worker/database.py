from sqlalchemy import create_engine, Column, BigInteger, Text, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid

from config import settings

# Database engine
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ProjectStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class User(Base):
    __tablename__ = "users"
    
    telegram_id = Column(BigInteger, primary_key=True)
    first_name = Column(Text, nullable=False)
    username = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    name = Column(Text, nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    last_error_log = Column(Text)
    container_id = Column(Text)
    zip_storage_path = Column(Text)
    encrypted_bot_token = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    owner = relationship("User", back_populates="projects")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()