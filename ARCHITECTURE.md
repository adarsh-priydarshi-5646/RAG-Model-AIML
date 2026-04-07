# RAG System - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [API Integration](#api-integration)

---

## System Overview

यह एक **Retrieval-Augmented Generation (RAG)** system है जो documents से intelligent answers generate करता है।

### Key Features:
- Document ingestion और processing
- Vector-based semantic search
- AI-powered answer generation
- Web और CLI interfaces
- Production-ready deployment

---

## Architecture Diagram

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        A[Web Interface<br/>Streamlit] 
        B[CLI Interface<br/>Terminal]
    end
    
    subgraph "RAG Pipeline"
        C[RAG Pipeline<br/>Orchestrator]
        D[Retriever<br/>Semantic Search]
        E[Generator<br/>LLM Response]
    end
    
    subgraph "Data Layer"
        F[Vector Database<br/>FAISS]
        G[Documents<br/>data/raw/]
    end
    
    subgraph "External Services"
        H[Groq API<br/>Llama 3.3 70B]
        I[Web Search<br/>DuckDuckGo/Google]
    end
    
    subgraph "Ingestion Pipeline"
        J[Document Loader]
        K[Text Splitter]
        L[Embeddings<br/>MockEmbeddings]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    D --> F
    E --> H
    E --> I
    G --> J
    J --> K
    K --> L
    L --> F
    
    style A fill:#2196F3,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#4CAF50,color:#fff
    style D fill:#4CAF50,color:#fff
    style E fill:#4CAF50,color:#fff
    style F fill:#FF9800,color:#fff
    style G fill:#FF9800,color:#fff
    style H fill:#9C27B0,color:#fff
    style I fill:#9C27B0,color:#fff
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Web/CLI Interface
    participant Pipeline as RAG Pipeline
    participant Retriever
    participant VectorDB as FAISS Vector DB
    participant Generator
    participant LLM as Groq LLM
    participant WebSearch as Web Search API
    
    User->>UI: Ask Question
    UI->>Pipeline: Forward Query
    Pipeline->>Retriever: Retrieve Documents
    Retriever->>VectorDB: Similarity Search
    VectorDB-->>Retriever: Top-K Documents
    Retriever-->>Pipeline: Retrieved Docs
    Pipeline->>Generator: Generate Answer
    Generator->>LLM: Query + Context
    LLM-->>Generator: Initial Response
    
    alt Answer Found in Documents
        Generator-->>Pipeline: Return Answer
    else Answer Not Found
        Generator->>WebSearch: Search Query
        WebSearch-->>Generator: Search Results
        Generator->>LLM: Query + Docs + Web Results
        LLM-->>Generator: Enhanced Answer
        Generator-->>Pipeline: Return Answer with Sources
    end
    
    Pipeline-->>UI: Final Answer
    UI-->>User: Display Answer
```

### Ingestion Flow

```mermaid
flowchart LR
    A[Raw Documents<br/>.txt files] --> B[Document Loader<br/>TextLoader]
    B --> C[Text Splitter<br/>CharacterTextSplitter]
    C --> D{Chunking Strategy}
    D -->|chunk_size: 1000| E[Document Chunks]
    D -->|overlap: 200| E
    E --> F[Mock Embeddings<br/>1536 dimensions]
    F --> G[FAISS Index<br/>Creation]
    G --> H[Save to Disk<br/>index.faiss + index.pkl]
    
    style A fill:#FFC107,color:#000
    style H fill:#4CAF50,color:#fff
```

### Component Interaction

```mermaid
graph LR
    subgraph "Configuration"
        Config[config.py<br/>Environment Variables]
    end
    
    subgraph "Core RAG"
        Pipeline[pipeline.py<br/>Orchestration]
        Retriever[retriever.py<br/>Search]
        Generator[generator.py<br/>LLM]
        Ingestion[ingestion.py<br/>Processing]
    end
    
    subgraph "Utilities"
        WebSearch[web_search.py<br/>External Search]
        Helpers[helpers.py<br/>Utilities]
    end
    
    Config --> Pipeline
    Config --> Retriever
    Config --> Generator
    Config --> Ingestion
    
    Pipeline --> Retriever
    Pipeline --> Generator
    Generator --> WebSearch
    
    style Config fill:#607D8B,color:#fff
    style Pipeline fill:#4CAF50,color:#fff
    style Retriever fill:#2196F3,color:#fff
    style Generator fill:#FF5722,color:#fff
    style Ingestion fill:#9C27B0,color:#fff
```

---

## Component Details

### 1. Configuration Layer (`app/config.py`)

```
┌─────────────────────────────────┐
│      Configuration              │
├─────────────────────────────────┤
│ • Load .env variables           │
│ • API key validation            │
│ • Path configurations           │
│ • Environment setup             │
└─────────────────────────────────┘
```

**Responsibilities:**
- Environment variables loading
- API key management
- Path configurations (DATA_PATH, VECTOR_DB_PATH)
- Validation checks

**Key Variables:**
```python
OPENAI_API_KEY    # Groq API key
DATA_PATH         # data/raw/
VECTOR_DB_PATH    # vectorstore/db/
```

---

### 2. Ingestion Module (`rag/ingestion.py`)

```
┌──────────────────────────────────────────────┐
│           INGESTION PIPELINE                 │
├──────────────────────────────────────────────┤
│                                              │
│  1. Load Documents                           │
│     ├─ Read .txt files                       │
│     └─ TextLoader (LangChain)                │
│                                              │
│  2. Split Documents                          │
│     ├─ CharacterTextSplitter                 │
│     ├─ chunk_size: 500                       │
│     └─ chunk_overlap: 50                     │
│                                              │
│  3. Create Embeddings                        │
│     ├─ MockEmbeddings (1536 dim)             │
│     └─ Consistent seed for reproducibility   │
│                                              │
│  4. Build Vector Database                    │
│     ├─ FAISS index creation                  │
│     └─ Save to disk (index.faiss, index.pkl) │
│                                              │
└──────────────────────────────────────────────┘
```

**Process Flow:**
```
Documents → Load → Split → Embed → FAISS → Save
```

**Key Functions:**
- `load_documents(path)` - Load all .txt files
- `split_documents(docs)` - Chunk documents
- `create_vector_db(docs, path)` - Create FAISS index
- `run_ingestion()` - Complete pipeline

---

### 3. Retrieval Module (`rag/retriever.py`)

```
┌──────────────────────────────────────┐
│        RETRIEVAL SYSTEM              │
├──────────────────────────────────────┤
│                                      │
│  Query (text)                        │
│      ↓                               │
│  Embed Query                         │
│      ↓                               │
│  FAISS Similarity Search             │
│      ↓                               │
│  Top-K Documents (k=3)               │
│      ↓                               │
│  Return Relevant Chunks              │
│                                      │
└──────────────────────────────────────┘
```

**Key Functions:**
- `load_db(path)` - Load FAISS index
- `retrieve(query, k=3)` - Get top-k similar documents

**Similarity Search:**
- Uses cosine similarity
- Returns top 3 most relevant chunks
- Includes metadata and content

---

### 4. Generation Module (`rag/generator.py`)

```
┌────────────────────────────────────────────┐
│         ANSWER GENERATION                  │
├────────────────────────────────────────────┤
│                                            │
│  Input: Query + Retrieved Documents        │
│      ↓                                     │
│  Build Context                             │
│      ↓                                     │
│  Create Prompt                             │
│      ├─ System: "Answer from context"     │
│      └─ User: Context + Question          │
│      ↓                                     │
│  Send to Groq API                          │
│      ├─ Model: llama-3.3-70b-versatile    │
│      └─ Base URL: api.groq.com            │
│      ↓                                     │
│  Parse Response                            │
│      ↓                                     │
│  Return Answer                             │
│                                            │
└────────────────────────────────────────────┘
```

**Prompt Template:**
```
Answer ONLY from the context.
If not found, say 'I don't know'.

Context: {retrieved_documents}
Question: {user_query}
```

---

### 5. RAG Pipeline (`rag/pipeline.py`)

```
┌─────────────────────────────────────────┐
│         RAG PIPELINE                    │
├─────────────────────────────────────────┤
│                                         │
│  User Query                             │
│      ↓                                  │
│  ┌─────────────────┐                   │
│  │   RETRIEVE      │                   │
│  │  (retriever.py) │                   │
│  └────────┬────────┘                   │
│           │                             │
│           ▼                             │
│  Retrieved Documents                    │
│           │                             │
│           ▼                             │
│  ┌─────────────────┐                   │
│  │   GENERATE      │                   │
│  │  (generator.py) │                   │
│  └────────┬────────┘                   │
│           │                             │
│           ▼                             │
│  Final Answer                           │
│                                         │
└─────────────────────────────────────────┘
```

**Function:**
```python
def rag_pipeline(query):
    docs = retrieve(query)        # Step 1: Retrieve
    response = generate_answer(query, docs)  # Step 2: Generate
    return response
```

---

## Data Flow

### Complete Request Flow

```mermaid
flowchart TD
    Start([User Submits Query]) --> Input[Query Input]
    Input --> Validate{Valid Query?}
    Validate -->|No| Error1[Return Error]
    Validate -->|Yes| RAG[RAG Pipeline Entry]
    
    RAG --> Retrieve[Retrieval Phase]
    Retrieve --> LoadDB[Load FAISS Index]
    LoadDB --> Embed[Embed Query]
    Embed --> Search[Similarity Search]
    Search --> TopK[Get Top-5 Chunks]
    
    TopK --> Generate[Generation Phase]
    Generate --> BuildContext[Build Context from Chunks]
    BuildContext --> CreatePrompt[Create LLM Prompt]
    CreatePrompt --> CallLLM[Call Groq API]
    CallLLM --> Response[Receive Response]
    
    Response --> Check{Answer<br/>Found?}
    Check -->|Yes| Return[Return Answer]
    Check -->|No| WebSearch[Perform Web Search]
    WebSearch --> WebResults{Results<br/>Found?}
    WebResults -->|Yes| EnhancePrompt[Enhance Prompt with Web Data]
    WebResults -->|No| NoAnswer[Return 'No Answer Found']
    EnhancePrompt --> CallLLM2[Call Groq API Again]
    CallLLM2 --> FinalAnswer[Return Enhanced Answer]
    
    Return --> Display[Display to User]
    FinalAnswer --> Display
    NoAnswer --> Display
    Error1 --> Display
    Display --> End([End])
    
    style Start fill:#4CAF50,color:#fff
    style End fill:#F44336,color:#fff
    style RAG fill:#2196F3,color:#fff
    style Generate fill:#FF9800,color:#fff
    style WebSearch fill:#9C27B0,color:#fff
```

### Retrieval Process

```mermaid
graph TD
    A[User Query] --> B[Query Preprocessing]
    B --> C[Generate Query Embedding<br/>MockEmbeddings]
    C --> D[Load FAISS Index]
    D --> E[Cosine Similarity Search]
    E --> F{Results<br/>Found?}
    F -->|Yes| G[Sort by Relevance Score]
    F -->|No| H[Relaxed Search<br/>Increase K]
    H --> G
    G --> I[Return Top-K Documents]
    I --> J[Document Chunks with Metadata]
    
    style A fill:#4CAF50,color:#fff
    style C fill:#2196F3,color:#fff
    style E fill:#FF9800,color:#fff
    style J fill:#9C27B0,color:#fff
```

### Generation Process with Web Search

```mermaid
stateDiagram-v2
    [*] --> CheckDocuments
    CheckDocuments --> GenerateFromDocs: Documents Available
    CheckDocuments --> WebSearch: No Documents
    
    GenerateFromDocs --> EvaluateAnswer
    EvaluateAnswer --> ReturnAnswer: Answer Found
    EvaluateAnswer --> WebSearch: Answer Insufficient
    
    WebSearch --> SearchDuckDuckGo
    SearchDuckDuckGo --> ParseResults
    ParseResults --> CombineContext
    CombineContext --> GenerateEnhanced
    GenerateEnhanced --> ReturnEnhancedAnswer
    
    ReturnAnswer --> [*]
    ReturnEnhancedAnswer --> [*]
    
    note right of WebSearch
        Fallback mechanism when
        documents don't contain answer
    end note
    
    note right of GenerateEnhanced
        Combines document context
        with web search results
    end note
```

---

## Technology Stack

### Core Technologies

```
┌─────────────────────────────────────────────┐
│           TECHNOLOGY STACK                  │
├─────────────────────────────────────────────┤
│                                             │
│  Language:                                  │
│    • Python 3.10                            │
│                                             │
│  Frameworks:                                │
│    • LangChain (Document processing)        │
│    • Streamlit (Web UI)                     │
│                                             │
│  Vector Database:                           │
│    • FAISS (Facebook AI Similarity Search)  │
│                                             │
│  LLM Provider:                              │
│    • Groq (Fast inference)                  │
│    • Model: Llama 3.3 70B Versatile         │
│                                             │
│  Libraries:                                 │
│    • langchain-community                    │
│    • langchain-text-splitters               │
│    • openai (SDK)                           │
│    • numpy                                  │
│    • python-dotenv                          │
│                                             │
│  Deployment:                                │
│    • Docker                                 │
│    • Streamlit Cloud                        │
│    • Render / Railway                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## API Integration

### Groq API Integration

```
┌──────────────────────────────────────────────┐
│          GROQ API INTEGRATION                │
├──────────────────────────────────────────────┤
│                                              │
│  Configuration:                              │
│    • Base URL: https://api.groq.com/openai/v1│
│    • Authentication: Bearer token            │
│    • SDK: OpenAI-compatible                  │
│                                              │
│  Model Details:                              │
│    • Name: llama-3.3-70b-versatile          │
│    • Context: 128K tokens                    │
│    • Speed: ~800 tokens/sec                  │
│    • Cost: FREE tier available               │
│                                              │
│  Request Format:                             │
│    {                                         │
│      "model": "llama-3.3-70b-versatile",    │
│      "messages": [                           │
│        {"role": "system", "content": "..."},│
│        {"role": "user", "content": "..."}   │
│      ]                                       │
│    }                                         │
│                                              │
│  Response Format:                            │
│    {                                         │
│      "choices": [{                           │
│        "message": {                          │
│          "content": "answer text"            │
│        }                                     │
│      }]                                      │
│    }                                         │
│                                              │
└──────────────────────────────────────────────┘
```

---

## System Metrics

### Performance Characteristics

```
┌─────────────────────────────────────────┐
│        PERFORMANCE METRICS              │
├─────────────────────────────────────────┤
│                                         │
│  Ingestion:                             │
│    • Speed: ~100 docs/sec               │
│    • Chunk size: 500 chars              │
│    • Overlap: 50 chars                  │
│                                         │
│  Retrieval:                             │
│    • Latency: <100ms                    │
│    • Top-K: 3 documents                 │
│    • Accuracy: High (semantic)          │
│                                         │
│  Generation:                            │
│    • Latency: 1-3 seconds               │
│    • Token speed: ~800 tok/sec          │
│    • Context window: 128K tokens        │
│                                         │
│  Storage:                               │
│    • Vector DB: ~20KB per 1000 chunks   │
│    • Embeddings: 1536 dimensions        │
│                                         │
└─────────────────────────────────────────┘
```

---

## Security Architecture

```
┌────────────────────────────────────────┐
│       SECURITY MEASURES                │
├────────────────────────────────────────┤
│                                        │
│  1. API Key Management                 │
│     • Stored in .env (not in code)    │
│     • Loaded via python-dotenv         │
│     • Never committed to git           │
│                                        │
│  2. Input Validation                   │
│     • Query sanitization               │
│     • Length limits                    │
│                                        │
│  3. Output Safety                      │
│     • Context-only answers             │
│     • No code execution                │
│                                        │
│  4. Deployment                         │
│     • Environment variables            │
│     • HTTPS only                       │
│     • Rate limiting (API level)        │
│                                        │
└────────────────────────────────────────┘
```

---

## Directory Structure

```
RAG-AIML/
│
├── app/                      # Application layer
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   └── main.py              # CLI interface
│
├── rag/                      # Core RAG modules
│   ├── __init__.py
│   ├── ingestion.py         # Document processing
│   ├── retriever.py         # Semantic search
│   ├── generator.py         # Answer generation
│   └── pipeline.py          # RAG orchestration
│
├── data/                     # Data storage
│   ├── raw/                 # Input documents
│   └── processed/           # Processed data (if any)
│
├── vectorstore/              # Vector database
│   └── db/
│       ├── index.faiss      # FAISS index
│       └── index.pkl        # Metadata
│
├── app_web.py               # Streamlit web interface
├── ingest.py                # Ingestion script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── .env                     # Environment variables
└── .gitignore              # Git ignore rules
```

---

## Deployment Architecture

### Production Deployment

```mermaid
graph TB
    subgraph "Client Layer"
        Users[Users/Browsers]
    end
    
    subgraph "CDN & Security"
        CDN[Streamlit Cloud CDN<br/>HTTPS/SSL]
    end
    
    subgraph "Application Layer"
        App[Streamlit App<br/>app_web.py]
        Config[Configuration<br/>.env secrets]
    end
    
    subgraph "RAG Components"
        Pipeline[RAG Pipeline]
        Retriever[Retriever]
        Generator[Generator]
    end
    
    subgraph "Data Storage"
        VectorDB[(FAISS Vector DB<br/>index.faiss)]
        Docs[(Documents<br/>data/raw/)]
    end
    
    subgraph "External APIs"
        Groq[Groq API<br/>Llama 3.3 70B]
        WebAPI[Web Search API<br/>DuckDuckGo/Google]
    end
    
    Users --> CDN
    CDN --> App
    App --> Config
    App --> Pipeline
    Pipeline --> Retriever
    Pipeline --> Generator
    Retriever --> VectorDB
    Generator --> Groq
    Generator --> WebAPI
    VectorDB -.->|Ingestion| Docs
    
    style Users fill:#4CAF50,color:#fff
    style CDN fill:#2196F3,color:#fff
    style App fill:#FF9800,color:#fff
    style Groq fill:#9C27B0,color:#fff
    style WebAPI fill:#9C27B0,color:#fff
    style VectorDB fill:#607D8B,color:#fff
```

### Deployment Options

```mermaid
mindmap
  root((Deployment<br/>Options))
    Streamlit Cloud
      Free Tier
      Auto Deploy
      SSL Included
      Community Support
    Render
      Free Tier
      Auto Sleep
      Custom Domain
      GitHub Integration
    Hugging Face Spaces
      Free Hosting
      ML Community
      Easy Sharing
      No Sleep
    Railway
      Paid 5/month
      Always Running
      Fast Deploy
      Good Performance
    Docker VPS
      Full Control
      Self Hosted
      Custom Config
      Manual Setup
```

### CI/CD Pipeline

```mermaid
gitGraph
    commit id: "Initial Setup"
    commit id: "Add RAG Core"
    branch development
    checkout development
    commit id: "Feature: Web Search"
    commit id: "Feature: Better UI"
    checkout main
    merge development tag: "v1.0"
    commit id: "Deploy to Streamlit"
    branch hotfix
    checkout hotfix
    commit id: "Fix: Dependencies"
    checkout main
    merge hotfix tag: "v1.0.1"
    commit id: "Auto Deploy"
```

---

## Troubleshooting Guide

### Common Issues & Solutions

```
Issue: Vector DB not found
Solution: Run python ingest.py

Issue: API key error
Solution: Check .env file and API key validity

Issue: Slow responses
Solution: Check Groq API rate limits

Issue: Import errors
Solution: pip install -r requirements.txt

Issue: OpenMP error (macOS)
Solution: export KMP_DUPLICATE_LIB_OK=TRUE
```

---

## Future Enhancements

1. **Multi-format Support**: PDF, DOCX, HTML
2. **Advanced Embeddings**: OpenAI, Cohere embeddings
3. **Caching**: Redis for faster responses
4. **Analytics**: Usage tracking and metrics
5. **Multi-language**: Support for Hindi, etc.
6. **Authentication**: User management
7. **File Upload**: Dynamic document upload
8. **Conversation Memory**: Chat history

---

## Support & Maintenance

- **Logs**: Check application logs for errors
- **Monitoring**: Track API usage and costs
- **Updates**: Keep dependencies updated
- **Backups**: Regular vector DB backups

---

**Last Updated**: April 2026
**Version**: 1.0.0
