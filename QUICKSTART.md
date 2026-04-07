# 🚀 Quick Start Guide

## RAG System - 5 Minutes Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/adarsh-priydarshi-5646/RAG-Model-AIML.git
cd RAG-Model-AIML
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup API Key
1. Get free API key: https://console.groq.com/keys
2. Create `.env` file:
```bash
echo "OPENAI_API_KEY=gsk_your_key_here" > .env
```

### Step 4: Ingest Documents
```bash
python ingest.py
```

### Step 5: Run Application
```bash
streamlit run app_web.py
```

Open browser: http://localhost:8501

---

## 🌐 Deploy to Production (FREE)

### Streamlit Cloud
1. Push to GitHub ✅ (Already done!)
2. Visit: https://share.streamlit.io/
3. Click "New app"
4. Select repository: `RAG-Model-AIML`
5. Main file: `app_web.py`
6. Add secret: `OPENAI_API_KEY = gsk_your_key`
7. Click "Deploy"

Your app will be live at: `https://your-app.streamlit.app`

---

## 📚 Documentation

- **README.md** - Overview and basic usage
- **ARCHITECTURE.md** - Complete technical documentation with diagrams
- **This file** - Quick start guide

---

## 🆘 Troubleshooting

**Problem**: Module not found
```bash
pip install -r requirements.txt
```

**Problem**: API key error
```bash
# Check .env file exists and has correct key
cat .env
```

**Problem**: Vector DB not found
```bash
python ingest.py
```

**Problem**: OpenMP error (macOS)
```bash
export KMP_DUPLICATE_LIB_OK=TRUE
```

---

## ✅ What's Included

- ✅ Complete RAG system
- ✅ Web interface (Streamlit)
- ✅ CLI interface
- ✅ Docker support
- ✅ Production-ready
- ✅ Full documentation
- ✅ Architecture diagrams
- ✅ Deployment configs

---

## 🎯 Next Steps

1. Add your own documents to `data/raw/`
2. Run `python ingest.py` again
3. Ask questions about your documents!

---

**Repository**: https://github.com/adarsh-priydarshi-5646/RAG-Model-AIML
