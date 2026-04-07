# Deployment Guide - Streamlit Cloud

## Quick Deployment Steps

### 1. Prerequisites
- GitHub account
- Groq API key (free from https://console.groq.com/keys)
- Code pushed to GitHub repository

### 2. Deploy to Streamlit Cloud

1. Visit https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Configure:
   - Repository: `adarsh-priydarshi-5646/RAG-Model-AIML`
   - Branch: `main`
   - Main file path: `app_web.py`

5. Click "Advanced settings"
6. Add Secrets (in TOML format):
   ```toml
   OPENAI_API_KEY = "gsk_your_groq_api_key_here"
   ```

7. Click "Deploy"

### 3. Wait for Deployment
- Initial deployment takes 2-5 minutes
- Streamlit will install dependencies automatically
- Your app will be live at: `https://your-app-name.streamlit.app`

## Troubleshooting

### Issue: Dependency conflicts
**Solution**: The requirements.txt is configured for compatibility. If issues persist:
- Check that numpy version is `<2.0.0,>=1.19.3`
- Streamlit Cloud uses Python 3.10+ by default

### Issue: Vector database not found
**Solution**: The app will show a warning. To fix:
1. Ensure `vectorstore/db/` folder is in your repository
2. Or run ingestion on first startup (automatic in setup.sh)

### Issue: API key error
**Solution**: 
1. Verify your Groq API key is valid
2. Check it's added in Streamlit Cloud secrets
3. Format should be: `OPENAI_API_KEY = "gsk_..."`

### Issue: Module import errors
**Solution**: 
- Ensure all files are committed to GitHub
- Check that `app/`, `rag/`, and `data/` folders are present

## Environment Variables

Required in Streamlit Cloud Secrets:
```toml
OPENAI_API_KEY = "gsk_your_groq_api_key_here"
```

Optional (for advanced configuration):
```toml
KMP_DUPLICATE_LIB_OK = "TRUE"  # For macOS OpenMP issues
```

## Post-Deployment

### Testing Your Deployment
1. Visit your app URL
2. Try example questions:
   - "Who created Python?"
   - "What are Python's key features?"
   - "When was Python 3 released?"

### Monitoring
- Check logs in Streamlit Cloud dashboard
- Monitor API usage in Groq console
- Track app performance in Streamlit metrics

### Updating Your App
1. Push changes to GitHub
2. Streamlit Cloud auto-deploys on push
3. Changes appear in 1-2 minutes

## Performance Tips

1. **Vector Database**: Pre-commit the vector database to avoid regeneration
2. **API Limits**: Groq free tier has rate limits - monitor usage
3. **Caching**: Streamlit caches data automatically
4. **Documents**: Keep documents under 10MB total for faster loading

## Custom Domain (Optional)

Streamlit Cloud provides:
- Free subdomain: `your-app.streamlit.app`
- Custom domain support (paid plans)

## Scaling

For production use:
- Consider Streamlit Cloud paid plans for:
  - Custom domains
  - More resources
  - Priority support
  - No sleep mode

## Support

- Streamlit Docs: https://docs.streamlit.io/
- Groq Docs: https://console.groq.com/docs
- GitHub Issues: https://github.com/adarsh-priydarshi-5646/RAG-Model-AIML/issues

## Security Notes

1. Never commit API keys to GitHub
2. Use Streamlit Cloud secrets for sensitive data
3. Keep dependencies updated
4. Monitor API usage regularly

---

**Your app is now live and accessible to anyone with the URL!**
