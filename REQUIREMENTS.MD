# Podcast Knowledge Chatbot  
## Requirements & Implementation Plan

---

## 1. Objective
Build a chatbot that allows internal teams and external users to query all company podcast content (via transcripts) to quickly find insights, quotes, and episode references by topic, industry, or speaker.

The goal is to turn the podcast library into a searchable knowledge and thought-leadership platform.

---

## 2. Business Value
- Strengthens company thought leadership  
- Saves time for content creation, sales, and marketing  
- Increases engagement with podcasts and community content  
- Improves sales enablement and prospecting  
- Demonstrates industry credibility in meetings and outreach  

---

## 3. Core Use Cases

### 3.1 Marketing & Content
- Generate topic-based summaries from multiple podcasts  
- Extract 5–6 quotes from different speakers on a single topic  
- Identify speakers to tag in LinkedIn posts  
- Create content outlines for blogs and social posts  

### 3.2 Sales Enablement
Allow AEs to:
- Search for podcast content by industry  
- Show prospects relevant episodes from similar businesses  
- Learn about a prospect’s industry through existing content  

### 3.3 Community & Website
- Embed an interactive chatbot on the community page  
- Let users:
  - Search topics  
  - See who has spoken about them  
  - Click through to relevant podcast episodes  

### 3.4 Partnerships & Outreach
- Show podcast prospects which related businesses have already been featured  
- Use during in-person visits to:
  - Show podcasts in the visitor’s industry  
  - Establish credibility and expertise  

---

## 4. Functional Requirements

### 4.1 Data
Ingest all existing podcast transcripts and store:
- Episode title  
- Guest name(s)  
- Industry/category  
- Topic tags  
- Episode link  

### 4.2 Chatbot Capabilities
- Natural language search across all transcripts  
- Topic-based querying (e.g., “restaurants”, “cybersecurity”)  
- Speaker-based querying (e.g., “What has Martha said about X?”)  
- Quote extraction with speaker attribution  
- Episode recommendations with links  
- Industry filtering  

### 4.3 Interfaces
- Internal version for marketing, sales, and leadership  
- Public-facing version for the community page (read-only)  

---

# 5. Technical Architecture & Requirements

## 5.1 API Layer
**Framework:** FastAPI

**Responsibilities:**
- Expose REST endpoints for chatbot queries  
- Handle authentication and rate limiting  
- Route user requests to LangGraph agents  
- Log queries and responses for analytics  
- Serve internal and public UI clients  

---

## 5.2 Agent Orchestration
**Framework:** LangGraph (multi-agent system)

**Agents:**
- **Query Router Agent** – Interprets user intent and routes tasks  
- **Search Agent** – Retrieves relevant transcript chunks via RAG  
- **Quote Agent** – Extracts and formats quotes with attribution  
- **Summary Agent** – Produces topic summaries  
- **Recommendation Agent** – Suggests relevant episodes and speakers  

**State Management:**
- Use LangGraph state to pass context between agents  

---

## 5.3 Agent Tooling
**Framework:** fastMCP

**Purpose:**
- Expose retrieval, filtering, and metadata lookup as MCP tools  
- Provide structured tool calls for:
  - Transcript search  
  - Industry filtering  
  - Speaker lookup  
  - Episode metadata retrieval  

---

## 5.4 Retrieval & Embeddings (RAG)
**Vector / Search Engine:** Typesense

**Responsibilities:**
- Store transcript chunks with metadata  
- Store vector embeddings for semantic search  
- Support hybrid search (keyword + vector)  

**Indexing:**
- Chunk transcripts by topic/paragraph  
- Generate embeddings for each chunk  
- Store metadata (episode, speaker, industry, timestamp, link)  

---

## 5.5 Data Pipeline
1. Collect podcast transcripts  
2. Clean and normalize text  
3. Chunk transcripts  
4. Generate embeddings  
5. Store in Typesense  
6. Sync metadata to MCP tools  

---

## 5.6 Security & Access
- Token-based authentication for internal users  
- Public chatbot with restricted access  
- Rate limiting and logging  
- Optional role-based access (Marketing, Sales, Admin)  

---

## 5.7 Deployment
- Containerized services (Docker)  
- Separate services for:
  - FastAPI backend  
  - LangGraph agent service  
  - Typesense vector store  
- CI/CD for model and index updates  

---

## 6. Success Metrics
- Reduced time to create content and sales materials  
- Increased podcast engagement (clicks, listens)  
- Increased community interaction  
- Increased usage by AEs  
- Positive feedback from prospects and partners  

---

## 7. Open Questions
- Do we already have podcast transcripts?  
- Are transcripts already structured or time-stamped?  
- Do we have episode metadata in a database?  
