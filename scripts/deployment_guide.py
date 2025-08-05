"""
Deploy Doc-Scanner to various cloud platforms
"""

# Heroku deployment
heroku_commands = """
# 1. Install Heroku CLI
# 2. Login to Heroku
heroku login

# 3. Create app
heroku create your-doc-scanner-app

# 4. Set environment variables
heroku config:set GOOGLE_API_KEY=your_api_key

# 5. Create Procfile
echo "web: python run.py" > Procfile

# 6. Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
"""

# Railway deployment
railway_commands = """
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Set environment variables
railway variables set GOOGLE_API_KEY=your_api_key

# 5. Deploy
railway up
"""

# AWS EC2 deployment
aws_commands = """
# 1. Launch EC2 instance (Ubuntu 20.04)
# 2. Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx

# 3. Clone repository
git clone https://github.com/yourusername/doc-scanner.git
cd doc-scanner

# 4. Install requirements
pip3 install -r requirements.txt

# 5. Configure nginx
sudo cp nginx.conf /etc/nginx/sites-available/doc-scanner
sudo ln -s /etc/nginx/sites-available/doc-scanner /etc/nginx/sites-enabled/

# 6. Start application
python3 run.py
"""

print("Choose your deployment platform:")
print("1. Heroku (easiest)")
print("2. Railway (modern)")
print("3. AWS EC2 (scalable)")
print("4. Docker (containerized)")
