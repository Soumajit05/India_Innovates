# Phase 1 Implementation Guide - India_Innovates

## Overview

This document describes the Phase 1 enhancements that transform the India_Innovates project from a prototype into a production-ready Global Ontology Engine.

**Implementation Date:** March 2026  
**Components Added:** 6 major modules  
**Dependencies Added:** 15 new packages

---

## New Modules

### 1. **Persistent Storage Layer** (`database.py`)

**Purpose:** Replace in-memory storage with PostgreSQL + Neo4j for production reliability.

**Components:**
- `NodeRecord`: Stores entities with properties, credibility, domains
- `EdgeRecord`: Stores relationships with provenance and decay rates 
- `DocumentRecord`: Tracks ingested sources with metadata
- `ProvenanceRecord`: Audit trail for all graph operations
- `EmbeddingRecord`: Stores vector embeddings for semantic search
- `DatabaseManager`: Connection pooling singleton

**Usage in main.py:**
```python
from app.database import db_manager, DocumentRecord

# Initialize on startup
db_manager.initialize()

# Store ingested document
session = db_manager.get_session()
doc = DocumentRecord(
    id="gdelt_12345",
    title="India China border...",
    source="GDELT",
    domain="GEOPOLITICS",
    credibility_score=0.75
)
session.add(doc)
session.commit()
```

**Environment Variables:**
```
DATABASE_URL=postgresql://user:password@localhost/india_innovates
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

### 2. **Vector Embeddings** (`embeddings.py`)

**Purpose:** Enable semantic similarity search and entity linking.

**Components:**
- `EmbeddingService`: Generates embeddings via Sentence-BERT
- Batch processing for efficiency
- Semantic search implementation

**Usage:**
```python
from app.embeddings import embedding_service

# Embed single text
embedding = embedding_service.embed_text("India China border tension")

# Semantic search in corpus
corpus = ["GDP growth slowing", "Stock market crash", "Political crisis"]
results = embedding_service.semantic_search(
    query="Economic downturn",
    corpus=corpus,
    top_k=2
)
# Returns: [(1, 0.89), (0, 0.76)]  # indices and scores
```

**Available Models:**
- `sentence-transformers/all-MiniLM-L6-v2` (fast, 384d) — **DEFAULT**
- `sentence-transformers/all-mpnet-base-v2` (accurate, 768d)
- `sentence-transformers/multi-qa-mpnet-base-dot-v1` (specialized)

---

### 3. **Entity Linking** (`entity_linking.py`)

**Purpose:** Resolve extracted entities to canonical Wikidata identifiers.

**Components:**
- `WikidataEntityLinker`: Search and fetch entity info
- `EntityAliasRegistry`: Coreference resolution

**Usage:**
```python
from app.entity_linking import WikidataEntityLinker, EntityAliasRegistry

# Link entity to Wikidata
entity_info = WikidataEntityLinker.link_entity("India", entity_type="COUNTRY")
# Returns: {
#   "id": "Q668",
#   "label": "India",
#   "description": "sovereign state in South Asia",
#   "instance_of": "Q3624078",  # sovereign state
#   "population": 1407563842,
#   "coordinate": (20.5937, 78.9629)
# }

# Resolve aliases
canonical = EntityAliasRegistry.resolve_alias("USA")
# Returns: "United States"

# Register new alias
EntityAliasRegistry.register_alias("India", "Bharat")
```

---

### 4. **JWT Authentication** (`auth_jwt.py`)

**Purpose:** Replace simple API key auth with industry-standard JWT tokens.

**Components:**
- `JWTAuthenticator`: Token generation/validation
- `TokenPayload`: Claims model
- FastAPI dependencies for route protection

**Usage:**
```python
from app.auth_jwt import JWTAuthenticator, get_current_user, require_permission
from fastapi import FastAPI, Depends

app = FastAPI()

# Generate token (on login)
token = JWTAuthenticator.create_access_token(
    subject="user@example.com",
    scopes=["read", "write"]
)

# Protected route
@app.get("/dashboard")
async def get_dashboard(current_user = Depends(get_current_user)):
    return {"user": current_user.subject}

# Permission-restricted route
@app.post("/scenarios")
async def create_scenario(
    current_user = Depends(require_permission("write"))
):
    return {"owner": current_user.subject}
```

**Token Generation (curl):**
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user@email.com", "password": "pass"}'
```

**Token Usage (API calls):**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/dashboard
```

---

### 5. **Enhanced Twitter Integration** (`ingestion/twitter_v2.py`)

**Purpose:** Real Twitter API v2 integration replacing stub implementation.

**Components:**
- `TwitterDataCollector`: Search and collection
- `TwitterStreamListener`: Real-time streaming (future)
- Multi-domain keyword organization

**Usage:**
```python
from app.ingestion.twitter_v2 import twitter_collector

# Search tweets
tweets = twitter_collector.search_tweets(
    query="India LAC China",
    max_results=100,
    hours_back=24
)

# Multi-domain collection
all_tweets = twitter_collector.collect_multi_domain_tweets(
    hours_back=24,
    max_per_domain=50
)
# Returns: {"geopolitics": [...], "economics": [...], ...}

# Extract entities from tweets
entities = twitter_collector.extract_entities_from_tweets(tweets)
# Returns: {"people": [...], "organizations": [...], ...}
```

**Configuration:**
```
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

---

### 6. **Temporal Trend Analysis** (`reasoning/temporal.py`)

**Purpose:** Detect patterns, anomalies, and forecast trends in graph metrics.

**Components:**
- `TemporalTrendAnalyzer`: Trend detection, anomaly detection, forecasting
- `GraphMetricsTimeSeries`: Time-series storage and analysis

**Usage:**
```python
from app.reasoning.temporal import TemporalTrendAnalyzer, graph_metrics_ts
from datetime import datetime, timedelta

# Record metrics over time
for i in range(30):
    date = datetime.utcnow() - timedelta(days=30-i)
    value = 100 + (i * 2) + (i % 3)  # Increasing trend with noise
    graph_metrics_ts.record_metric("edges_per_day", value, date)

# Trend analysis
analyzer = TemporalTrendAnalyzer(window_size=7)
values = [(d, v) for d, v in ...]  # [(timestamp, value), ...]
trend = analyzer.compute_trend(values)

# Returns:
{
    "trend": "increasing",
    "velocity": 2.1,  # slope
    "strength": 0.87,  # R-squared
    "recent_avg": 162,
    "historical_avg": 130,
    "volatility": 2.3
}

# Anomaly detection (Z-score)
anomalies = analyzer.detect_anomalies(values, z_threshold=2.5)

# Forecasting
forecast = analyzer.forecast(values, days_ahead=7, method="linear")
# Returns: [
#   {
#     "date": "2026-04-03",
#     "forecast": 170.5,
#     "ci_lower": 165.2,
#     "ci_upper": 175.8,
#     "confidence": 0.95
#   },
#   ...
# ]
```

---

### 7. **Multi-Source Consensus** (`reasoning/consensus.py`)

**Purpose:** Reconcile conflicting information across sources using weighted voting.

**Components:**
- `MultiSourceConsensus`: Truth reconciliation engine
- `ConfidenceAggregator`: Confidence score aggregation

**Usage:**
```python
from app.reasoning.consensus import consensus_engine, ConfidenceAggregator

# Register claims from multiple sources
consensus_engine.register_claim(
    claim_id="gdelt_001",
    source="GDELT",
    claim_type="entity_property",
    subject="India GDP",
    predicate="growth_rate_2025",
    value="6.5%"
)

consensus_engine.register_claim(
    claim_id="imf_001",
    source="IMF",
    claim_type="entity_property",
    subject="India GDP",
    predicate="growth_rate_2025", value="6.2%"
)

# Reconcile via weighted voting
consensus = consensus_engine.reconcile_claims(
    subject="India GDP",
    predicate="growth_rate_2025"
)
# Returns:
{
    "value": "6.5%",
    "confidence": 0.86,  # IMF(0.93) vs GDELT(0.75) weighted vote
    "sources": ["GDELT"],
    "agreement_ratio": 0.5,  # 50% sources agree
    "consensus_type": "weak",
    "alternative_values": [
        {"value": "6.2%", "score": 0.93, "sources": ["IMF"]}
    ]
}

# Detect contradictions
contradictions = consensus_engine.detect_contradictions(threshold=0.3)

# Audit trail
provenance = consensus_engine.get_provenance_trail(
    subject="India GDP",
    predicate="growth_rate_2025"
)
```

---

## Integration with Existing Components

### Updated Ingestion Pipeline

Replace the old Twitter stub in `ingestion/scheduler.py`:

```python
# OLD (still in scheduler.py currently)
# from app.ingestion.twitter import ingest_twitter

# NEW
from app.ingestion.twitter_v2 import twitter_collector
from app.database import db_manager, DocumentRecord, ProvenanceRecord
from app.entity_linking import WikidataEntityLinker
from app.reasoning.consensus import consensus_engine

async def ingest_twitter_v2():
    """Enhanced Twitter ingestion with persistence and consensus."""
    tweets = twitter_collector.collect_multi_domain_tweets(
        hours_back=24,
        max_per_domain=50
    )
    
    session = db_manager.get_session()
    
    for domain, tweet_list in tweets.items():
        for tweet in tweet_list:
            # Store document
            doc = DocumentRecord(
                id=f"twitter_{tweet['id']}",
                title=tweet['text'][:200],
                url=tweet.get('url'),
                source="TWITTER",
                content=tweet['text'],
                domain=domain,
                credibility_score=0.45  # Twitter low credibility
            )
            session.add(doc)
            
            # Link mentions to Wikidata
            for person_mention in twitter_collector.extract_entities_from_tweets([tweet])["people"]:
                # Resolve to canonical entity...
>>> 
    session.commit()
```

### Dashboard Integration

Update `api/dashboard.py` to use trend analysis:

```python
from app.reasoning.temporal import graph_metrics_ts

async def get_dashboard_overview():
    """Enhanced dashboard with trends."""
    # Original logic...
    
    # Add trend data
    geopolitics_trend = graph_metrics_ts.get_metrics_summary("edges_per_domain.GEOPOLITICS", days=7)
    
    return {
        **original_response,
        "trends": {
            "geopolitics": geopolitics_trend,
            "economics": graph_metrics_ts.get_metrics_summary("edges_per_domain.ECONOMICS"),
            ...
        }
    }
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment

```bash
cp .env.template .env

# Edit .env with your configuration:
# - DATABASE_URL
# - NEO4J_* settings
# - TWITTER_BEARER_TOKEN
# - JWT_SECRET_KEY
# - etc.
```

### 3. Initialize Databases

```bash
# PostgreSQL
createdb india_innovates

# Run migrations (or let SQLAlchemy auto-create):
python -c "from app.database import db_manager; db_manager.initialize()"
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

---

## Security Checklist

- [ ] Change `JWT_SECRET_KEY` to random 32+ char string in production
- [ ] Store sensitive env vars in secrets manager (AWS Secrets, HashiCorp Vault)
- [ ] Enable database SSL connections
- [ ] Use HTTPS only in production
- [ ] Implement rate limiting on auth endpoints
- [ ] Add request signing for inter-service communication
- [ ] Rotate API keys regularly
- [ ] Audit log all data access

---

## Performance Tuning

### Embeddings
- Use `all-MiniLM-L6-v2` for speed (default)
- Cache embeddings to avoid recomputation
- Batch process large text collections

### Database
- Add indexes on frequently queried columns (source, timestamp, domain)
- Partition `documents` and `provenance` tables by date
- Archive old records to separate storage

### Twitter Ingestion
- Respect API rate limits (450 requests/15 min)
- Use streaming API for real-time (WIP)
- Deduplicate tweets by ID before storage

---

## Next Steps (Phase 2)

1. **Frontend Integration:**
   - Add JWT login UI
   - Query builder with semantic search
   - Real-time graph updates via WebSockets

2. **Advanced Reasoning:**
   - Bayesian graphical models
   - Causal inference with backdoor criterion
   - Anomaly alerting system

3. **External Integrations:**
   - Wikidata live linking
   - News API aggregation
   - Government data source connectors

---

## Troubleshooting

**TwitterError: 401 Unauthorized**
- Verify bearer token in .env
- Check Twitter API app permissions

**DatabaseConnectionError**
- Ensure PostgreSQL is running: `sudo systemctl start postgresql`
- Verify connection string format
- Check firewall rules

**EmbeddingError: sentence-transformers not installed**
- Run: `pip install sentence-transformers`
- First-time load will download model (~400MB)

**Neo4j connection failed**
- System will fallback to in-memory (non-persistent)
- Install Neo4j: browse https://neo4j.com/download/

---

**Documentation Version:** 1.0  
**Last Updated:** March 27, 2026
