# API Keys Setup Guide

## 📋 Overview

This guide walks you through obtaining API keys for:
1. **OpenAI API** (for DALL-E 3 image generation) - ✅ **REQUIRED**
2. **SerpAPI** (for video/web search) - ⭐ **RECOMMENDED**
3. **YouTube Data API** (alternative for video search) - Optional
4. **Google Custom Search API** (alternative for web search) - Optional

---

## 1. 🔑 OpenAI API Key (REQUIRED for DALL-E 3)

### Why You Need It:
- DALL-E 3 image generation
- Already using for ChatGPT/GPT-4
- **You likely already have this!**

### Steps:

1. **Check if you already have it:**
   ```bash
   # Check your .env file
   grep OPENAI_API_KEY .env
   ```

2. **If you don't have it, get one:**
   - Go to: https://platform.openai.com/api-keys
   - Sign in (or create account)
   - Click **"Create new secret key"**
   - Copy the key (starts with `sk-...`)
   - ⚠️ **Save it immediately** - you can't see it again!

3. **Add to your `.env` file:**
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

4. **Verify it works:**
   ```bash
   # Test the key
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

### Cost:
- DALL-E 3: $0.04/image (standard), $0.08/image (HD)
- DALL-E 2: $0.02/image
- Free tier: $5 credit when you sign up

---

## 2. 🔍 SerpAPI Key (RECOMMENDED for Search)

### Why You Need It:
- Search YouTube videos
- Search web resources
- One API for everything
- Easiest to implement

### Steps:

1. **Sign up for SerpAPI:**
   - Go to: https://serpapi.com/users/sign_up
   - Create account (free trial available)

2. **Get your API key:**
   - After signup, go to: https://serpapi.com/dashboard
   - Your API key is displayed on the dashboard
   - Copy it (looks like: `abc123def456...`)

3. **Add to your `.env` file:**
   ```bash
   SERPAPI_KEY=your_serpapi_key_here
   ```

4. **Install the package:**
   ```bash
   pip install google-search-results
   ```

5. **Test it:**
   ```python
   from serpapi import GoogleSearch
   
   params = {
       "q": "basketball fundamentals",
       "api_key": "your_key",
       "engine": "youtube"
   }
   
   search = GoogleSearch(params)
   results = search.get_dict()
   print(results)
   ```

### Cost:
- **Free Trial:** 100 searches
- **Starter:** $50/month (5,000 searches)
- **Business:** $250/month (50,000 searches)

### Free Trial:
- ✅ 100 free searches when you sign up
- ✅ Perfect for testing

---

## 3. 📺 YouTube Data API Key (Alternative for Video Search)

### Why You Might Want It:
- Free alternative to SerpAPI
- YouTube-only (no web search)
- Good for development/testing

### Steps:

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Sign in with Google account

2. **Create a new project (or select existing):**
   - Click project dropdown → "New Project"
   - Name it (e.g., "Faraday-AI")
   - Click "Create"

3. **Enable YouTube Data API v3:**
   - Go to: https://console.cloud.google.com/apis/library/youtube.googleapis.com
   - Click **"Enable"**

4. **Create API Key:**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click **"Create Credentials"** → **"API Key"**
   - Copy the key (looks like: `AIzaSy...`)

5. **Restrict the key (recommended):**
   - Click on the key to edit
   - Under "API restrictions", select "Restrict key"
   - Choose "YouTube Data API v3"
   - Click "Save"

6. **Add to your `.env` file:**
   ```bash
   YOUTUBE_API_KEY=AIzaSy_your_key_here
   ```

### Cost:
- ✅ **FREE:** 10,000 units per day
- ✅ No credit card required
- ✅ Perfect for development

### Quota:
- 10,000 units/day (1 search = 100 units)
- = ~100 searches per day (free)

---

## 4. 🌐 Google Custom Search API Key (Alternative for Web Search)

### Why You Might Want It:
- Free alternative to SerpAPI
- Web search only (no YouTube)
- Good for light usage

### Steps:

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Use same project as YouTube API (or create new)

2. **Enable Custom Search API:**
   - Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
   - Click **"Enable"**

3. **Create API Key:**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click **"Create Credentials"** → **"API Key"**
   - Copy the key

4. **Create Search Engine:**
   - Go to: https://programmablesearchengine.google.com/controlpanel/create
   - Click **"Add"** to create new search engine
   - Name it (e.g., "Faraday-AI Search")
   - Under "Sites to search", enter: `*` (to search entire web)
   - Click **"Create"**
   - Copy the **Search Engine ID** (looks like: `012345678901234567890:abc...`)

5. **Add to your `.env` file:**
   ```bash
   GOOGLE_SEARCH_API_KEY=AIzaSy_your_key_here
   GOOGLE_SEARCH_ENGINE_ID=012345678901234567890:abc...
   ```

### Cost:
- ✅ **FREE:** 100 queries per day
- ⚠️ **Paid:** $5 per 1,000 queries after free tier

### Quota:
- 100 searches/day (free)
- Limited for production use

---

## 📝 Quick Setup Checklist

### Minimum Required:
- [ ] ✅ **OpenAI API Key** (for DALL-E 3) - **REQUIRED**

### Recommended:
- [ ] ⭐ **SerpAPI Key** (for video/web search) - **RECOMMENDED**

### Optional Alternatives:
- [ ] 📺 **YouTube Data API Key** (free, YouTube only)
- [ ] 🌐 **Google Custom Search API Key** (free, web only, limited)

---

## 🚀 Quick Start (Recommended Setup)

### Step 1: Get OpenAI Key (if you don't have it)
```bash
# Check if you have it
grep OPENAI_API_KEY .env

# If not, add it:
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Step 2: Get SerpAPI Key (Recommended)
1. Sign up: https://serpapi.com/users/sign_up
2. Get key from dashboard
3. Add to `.env`:
   ```bash
   echo "SERPAPI_KEY=your_key_here" >> .env
   ```
4. Install package:
   ```bash
   pip install google-search-results
   ```

### Step 3: Upgrade OpenAI Package
```bash
pip install --upgrade openai
```

### Step 4: Test Everything
```bash
# Test OpenAI
python -c "from openai import OpenAI; print('OpenAI OK')"

# Test SerpAPI (if installed)
python -c "from serpapi import GoogleSearch; print('SerpAPI OK')"
```

---

## 💰 Cost Summary

| Service | Free Tier | Paid Tier | Best For |
|---------|-----------|-----------|----------|
| **OpenAI** | $5 credit | Pay per use | Required |
| **SerpAPI** | 100 searches | $50/month | Production |
| **YouTube API** | 10K/day | Free | Development |
| **Google Search** | 100/day | $5/1K | Light usage |

---

## 🔒 Security Best Practices

1. **Never commit `.env` to git:**
   ```bash
   # Make sure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production:**
   - Render: Add in Environment Variables section
   - Docker: Use `-e` flag or `.env` file
   - Local: Use `.env` file

3. **Restrict API keys:**
   - Google APIs: Restrict to specific APIs
   - OpenAI: Use organization settings
   - SerpAPI: Monitor usage in dashboard

---

## ❓ Troubleshooting

### "OpenAI API key not found"
- Check `.env` file exists
- Verify key starts with `sk-`
- Check for typos/spaces

### "SerpAPI not installed"
```bash
pip install google-search-results
```

### "YouTube API quota exceeded"
- Free tier: 10K units/day
- Wait 24 hours or upgrade
- Or use SerpAPI instead

### "Google Search API quota exceeded"
- Free tier: 100 queries/day
- Wait 24 hours or upgrade
- Or use SerpAPI instead

---

## 📞 Support Links

- **OpenAI:** https://platform.openai.com/docs
- **SerpAPI:** https://serpapi.com/dashboard
- **YouTube API:** https://developers.google.com/youtube/v3
- **Google Search:** https://developers.google.com/custom-search

---

## ✅ Next Steps After Getting Keys

1. Add keys to `.env` file
2. Install packages: `pip install --upgrade openai google-search-results`
3. Test the integrations
4. Deploy to Render (add keys to Environment Variables)

