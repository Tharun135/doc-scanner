# 🚀 DocScanner AI - Docker Deployment on Render

This guide will help you deploy your DocScanner AI Flask application to Render using Docker.

## 📋 Prerequisites

1. ✅ **GitHub Repository**: Your code should be pushed to GitHub
2. ✅ **Render Account**: Sign up at [render.com](https://render.com)
3. ✅ **Docker Files**: Already created ✅

## 🐳 Docker Files Overview

Your project now includes these Docker-related files:

- `Dockerfile` - Production-ready Docker configuration
- `.dockerignore` - Excludes unnecessary files from Docker build
- `wsgi.py` - WSGI entry point for Gunicorn
- `requirements.txt` - Updated with Gunicorn
- `render.yaml` - Optional Render configuration
- `.env.production` - Production environment template

## 🛠️ Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
git add .
git commit -m "Add Docker configuration for Render deployment"
git push origin main
```

### 2. Deploy on Render

1. **Go to Render**: Visit [render.com](https://render.com) and log in
2. **Create New Web Service**: Click "New +" → "Web Service"
3. **Connect Repository**: Connect your GitHub account and select your `doc-scanner` repository
4. **Configure Service**:
   - **Name**: `docscanner-ai` (or your preferred name)
   - **Runtime**: Select **Docker**
   - **Branch**: `main` (or your default branch)
   - **Build Command**: Leave empty (Docker handles this)
   - **Start Command**: Leave empty (Docker handles this)

### 3. Set Environment Variables

In the Render dashboard, go to "Environment" and add these variables:

**Required:**
```
FLASK_ENV=production
STABLE_MODE=1
SECRET_KEY=your-super-secret-key-here
```

**Optional (if you use external APIs):**
```
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Build the Docker image
   - Deploy your application
   - Provide a live URL like: `https://docscanner-ai.onrender.com`

## 🔍 Monitoring Your Deployment

### Build Logs
- Watch the build process in the Render dashboard
- Check for any errors during Docker image creation

### Application Logs
- Monitor runtime logs for errors
- Check application startup messages

### Health Check
- Your app includes a health check endpoint at `/`
- Render will automatically restart if health checks fail

## 🔧 Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check that all files are committed to Git
   - Verify `requirements.txt` is complete
   - Review Docker build logs for missing dependencies

2. **App Won't Start**:
   - Check environment variables are set correctly
   - Review application logs for startup errors
   - Ensure `wsgi.py` is properly configured

3. **High Memory Usage**:
   - The spaCy model and ML libraries use significant memory
   - Consider upgrading to a paid Render plan if needed

4. **Slow Performance**:
   - Free tier has limitations
   - Consider caching strategies for better performance

## 💡 Performance Tips

1. **Upgrade Plan**: Free tier has sleep mode - upgrade for 24/7 availability
2. **Add Redis**: For caching and session management
3. **Database**: Add PostgreSQL for persistent data storage
4. **CDN**: Use Render's CDN for static files

## 🌟 Your Live App

Once deployed, your DocScanner AI will be available at:
```
https://your-app-name.onrender.com
```

The app includes:
- Document text analysis
- Writing improvement suggestions
- AI-powered feedback
- Real-time WebSocket updates (if enabled)
- Knowledge base management

## 🔄 Updates

To update your deployed app:
1. Make changes locally
2. Commit and push to GitHub
3. Render automatically rebuilds and deploys

---

🎉 **Congratulations!** Your DocScanner AI is now running in production with Docker on Render!