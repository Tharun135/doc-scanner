# 🔑 Quick Gemini AI Setup

## Step 1: Get API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key (starts with "AIza...")

## Step 2: Add to .env File
Edit the `.env` file in this folder and replace:
```
GOOGLE_API_KEY=your_google_api_key_here
```

With your actual key:
```
GOOGLE_API_KEY=AIzaSyC-YourActualKeyHere
```

## Step 3: Test It
Run this command:
```
python test_gemini_integration.py
```

Should show "SUCCESS: Using real Gemini AI!"

## That's It! 🎉
Your AI suggestions will now be powered by Google Gemini instead of fallback rules.
