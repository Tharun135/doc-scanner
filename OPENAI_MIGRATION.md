# 🚀 OpenAI ChatGPT Integration

This version of doc-scanner now uses **OpenAI's ChatGPT** instead of local Ollama for superior AI suggestions.

## ⚡ Quick Setup

### 1. Get OpenAI API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy your API key

### 2. Set Environment Variable

**Windows (PowerShell):**
```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your_api_key_here"
```

**Or use .env file:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env file and add your API key
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Setup
```bash
python setup_ai.py
```

### 5. Start Application
```bash
python run.py
```

## 🎯 Benefits of OpenAI Integration

### **Advantages:**
- **Superior Quality**: ChatGPT provides more accurate and contextual suggestions
- **No Local Setup**: No need to install or manage local AI models
- **Always Updated**: Access to latest OpenAI improvements
- **Reliable**: Cloud-based service with high availability
- **Faster**: No local compute requirements

### **Cost:**
- **GPT-4o-mini**: ~$0.15 per 1M tokens (very affordable)
- **Typical Usage**: $0.01-0.10 per day for normal document editing
- **Cost Control**: Smart caching and efficient prompts minimize usage

## 🔧 Configuration

### Model Selection
Edit `ai_config.json` to change models:
```json
{
  "ai_settings": {
    "default_model": "gpt-4o-mini",  // Recommended: cost-effective
    "temperature": 0.1,              // Low for consistency
    "max_tokens": 150                // Concise responses
  }
}
```

### Available Models
- **gpt-4o-mini**: Best value, excellent quality
- **gpt-3.5-turbo**: Fast and affordable
- **gpt-4o**: Highest quality, more expensive

## 🛠️ Migration from Ollama

The system automatically falls back to smart rule-based suggestions if OpenAI is unavailable, ensuring continued functionality.

**Previous Ollama users:**
1. Remove Ollama if no longer needed: `ollama uninstall`
2. Set up OpenAI API key as shown above
3. Restart the application

## 🆘 Troubleshooting

### Common Issues:

**"OpenAI API key not found"**
- Ensure environment variable is set correctly
- Restart terminal/application after setting variable
- Check `.env` file if using one

**"API connection failed"**
- Verify your API key is valid
- Check internet connection
- Ensure you have OpenAI API credits

**"Import openai could not be resolved"**
- Run: `pip install openai`
- Check Python environment

### Fallback Mode
If OpenAI fails, the system automatically uses smart rule-based suggestions to ensure continued functionality.

## 📊 Monitoring

- Visit `/performance_dashboard` for AI usage metrics
- Monitor API costs in your OpenAI dashboard
- Provide feedback to improve suggestion quality

## 🔐 Security

- API keys are only stored in environment variables
- No data is permanently stored by OpenAI (per their API policy)
- All communication is encrypted (HTTPS)
