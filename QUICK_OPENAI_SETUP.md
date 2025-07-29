# 🚀 Quick OpenAI Setup Guide

## Step 1: Get API Key
1. Go to https://platform.openai.com/api-keys
2. Sign in/create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

## Step 2: Set API Key
**Windows:**
```cmd
setx OPENAI_API_KEY "sk-your-actual-key-here"
```

**Or edit .env file:**
```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Step 3: Restart Terminal
Close and reopen your terminal/PowerShell

## Step 4: Test Setup
```bash
python verify_openai_setup.py
```

## Step 5: Start Application
```bash
python run.py
```

## ✅ Expected Results
- API key detected ✅
- OpenAI test passes ✅  
- Method shows "openai_chatgpt" ✅
- Much better AI suggestions! 🎉

## 💰 Cost
- GPT-4o-mini: ~$0.15 per 1M tokens
- Typical usage: $0.01-0.10 per day
- Very affordable for document editing

## 🆘 Troubleshooting
- **"API key not found"**: Restart terminal after setting key
- **"Invalid API key"**: Check the key is correct and starts with `sk-`
- **"Fallback mode"**: API key not loaded properly, restart app
- **"Connection failed"**: Make sure app is running (`python run.py`)
