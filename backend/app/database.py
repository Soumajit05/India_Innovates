"""
Database initialization and connection management.
Supports PostgreSQL for relational data + Neo4j for graph persistence.
"""
import os
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from neo4j import GraphDatabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SQLALCHEMY MODELS FOR PostgreSQL
# ============================================================================

Base = declarative_base()


class NodeRecord(Base):
    """Persistent node storage."""
    __tablename__ = "nodes"
    
    id = Column(String(255), primary_key=True)
    label = Column(String(50))  # COUNTRY, ORGANIZATION, etc.
    domain = Column(String(50))  # GEOPOLITICS, ECONOMICS, etc.
    name = Column(String(255))
    properties = Column(JSON)  # Generic storage for node-specific fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    strength = Column(Float, default=1.0)  # Node confidence
    credibility = Column(Float, default=0.75)  # Source credibility


class EdgeRecord(Base):
    """Persistent edge (relationship) storage."""
    __tablename__ = "edges"
    
    id = Column(String(255), primary_key=True)
    source_id = Column(String(255))
    target_id = Column(String(255))
    edge_type = Column(String(50))  # CAUSES, THREATENS, etc.
    strength = Column(Float, default=0.75)  # Confidence
    decay_rate = Column(Float, default=0.1)  # Annual decay
    source = Column(String(100))  # GDELT, RSS, TWITTER, WORLDBANK
    source_url = Column(String(500))
    properties = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentRecord(Base):
    """Ingested document metadata."""
    __tablename__ = "documents"
    
    id = Column(String(255), primary_key=True)
    title = Column(String(500))
    url = Column(String(500), unique=True)
    source = Column(String(100))  # GDELT, RSS, TWITTER, WORLDBANK
    content = Column(Text)
    published_at = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    domain = Column(String(50))
    event_type = Column(String(50))
    extracted_entities = Column(JSON)  # List of entity IDs
    credibility_score = Column(Float, default=0.75)


class ProvenanceRecord(Base):
    """Audit trail for all graph changes."""
    __tablename__ = "provenance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation = Column(String(50))  # CREATE, UPDATE, DELETE
    entity_type = Column(String(50))  # NODE, EDGE
    entity_id = Column(String(255))
    old_value = Column(JSON)
    new_value = Column(JSON)
    source_document = Column(String(255))  # Document ID
    timestamp = Column(DateTime, default=datetime.utcnow)
    reasoning_chain = Column(JSON)  # How decision was made


class EmbeddingRecord(Base):
    """Vector embeddings for semantic search."""
    __tablename__ = "embeddings"
    
    id = Column(String(255), primary_key=True)
    entity_id = Column(String(255))  # Node/Edge ID
    entity_type = Column(String(50))  # NODE, EDGE, DOCUMENT
    embedding = Column(JSON)  # Vector array
    model = Column(String(100))  # Model name (e.g., sentence-transformers/all-MiniLM-L6-v2)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# DATABASE CONNECTION POOL
# ============================================================================

class DatabaseManager:
    """Singleton manager for database connections."""
    
    _instance = None
    _engine = None
    _session_maker = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def initialize(self):
        """Initialize database connection pools."""
        # PostgreSQL connection
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost/india_innovates"
        )
        self._engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            echo=os.getenv("DEBUG", "false").lower() == "true"
        )
        self._session_maker = sessionmaker(bind=self._engine)
        
        # Create all tables
        Base.metadata.create_all(self._engine)
        logger.info("PostgreSQL database initialized")
        
        # Neo4j connection
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            self.neo4j_driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            self.neo4j_driver.verify_connectivity()
            logger.info("Neo4j database connected")
        except Exception as e:
            logger.warning(f"Neo4j connection failed (using in-memory fallback): {e}")
            self.neo4j_driver = None
    
    def get_session(self) -> Session:
        """Get PostgreSQL session."""
        if self._session_maker is None:
            self.initialize()
        return self._session_maker()
    
    def get_neo4j_session(self):
        """Get Neo4j session."""
        if self.neo4j_driver is None:
            return None
        return self.neo4j_driver.session()
    
    def close(self):
        """Close all connections."""
        if self._engine:
            self._engine.dispose()
        if self.neo4j_driver:
            self.neo4j_driver.close()


# Global instance
db_manager = DatabaseManager()
