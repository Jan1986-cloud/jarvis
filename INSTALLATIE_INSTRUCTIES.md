# Jarvis AI Assistant - Installatie Instructies

## 📦 Installatie Package

Het `jarvis-installation-package.zip` bestand bevat alle benodigde bestanden voor de Jarvis AI Assistant.

### Package Inhoud:
- `jarvis-backend/` - Flask backend applicatie
- `jarvis-frontend/` - React frontend applicatie  
- `deploy.sh` - Automatisch deployment script
- `README.md` - Project overzicht
- `jarvis_documentation.pdf` - Complete documentatie
- `project_summary.md` - Project samenvatting

## 🖥️ Lokale Installatie

### Vereisten:
- Python 3.11+
- Node.js 20.18+
- Git
- Google Cloud Project met Workspace APIs

### Stap 1: Package Uitpakken
```bash
unzip jarvis-installation-package.zip
cd jarvis-installation-package
```

### Stap 2: Google Cloud Setup
1. Ga naar [Google Cloud Console](https://console.cloud.google.com)
2. Maak een nieuw project aan
3. Schakel de volgende APIs in:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Docs API
   - Google Sheets API
   - Google Slides API
4. Maak OAuth 2.0 credentials aan:
   - Type: Web application
   - Redirect URI: `http://localhost:5000/api/auth/callback`
5. Download de credentials JSON
6. Verkrijg een Gemini API key van [Google AI Studio](https://makersuite.google.com)

### Stap 3: Backend Setup
```bash
cd jarvis-backend

# Maak virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt

# Maak .env bestand
cat > .env << EOF
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_strong_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
FLASK_ENV=development
EOF

# Initialiseer database
python -c "
import sys
sys.path.insert(0, 'src')
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Database initialized')
"
```

### Stap 4: Frontend Setup
```bash
cd ../jarvis-frontend

# Installeer dependencies
npm install

# Start development server
npm run dev
```

### Stap 5: Backend Starten
```bash
cd ../jarvis-backend
source venv/bin/activate
python src/main.py
```

### Stap 6: Toegang
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000/api/info

## 🚂 Railway.com Deployment

Railway.com is een uitstekende keuze voor eenvoudige cloud deployment.

### Voorbereiding voor Railway

1. **Repository Setup**
```bash
# Initialiseer git repository
git init
git add .
git commit -m "Initial Jarvis deployment"

# Push naar GitHub (optioneel)
git remote add origin https://github.com/yourusername/jarvis-ai.git
git push -u origin main
```

2. **Railway Configuratie Bestanden**

Maak `railway.toml` in de root:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "cd jarvis-backend && gunicorn --bind 0.0.0.0:$PORT wsgi:application"
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
```

Maak `Procfile` in de root:
```
web: cd jarvis-backend && gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:application
```

### Railway Deployment Stappen

1. **Account Setup**
   - Ga naar [Railway.app](https://railway.app)
   - Maak account aan met GitHub
   - Installeer Railway CLI (optioneel)

2. **Project Deployment**
   - Klik "New Project"
   - Kies "Deploy from GitHub repo"
   - Selecteer uw Jarvis repository
   - Railway detecteert automatisch Python/Node.js

3. **Environment Variables**
   In Railway dashboard, ga naar Variables tab:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GEMINI_API_KEY=your_gemini_api_key
   SECRET_KEY=your_strong_secret_key_for_production
   JWT_SECRET_KEY=your_jwt_secret_key_for_production
   FLASK_ENV=production
   PORT=5000
   ```

4. **Database Setup**
   - Railway biedt gratis PostgreSQL
   - Klik "Add Service" → "Database" → "PostgreSQL"
   - Railway genereert automatisch DATABASE_URL

5. **Domain Setup**
   - Railway geeft automatisch een .railway.app domain
   - Custom domain kan worden toegevoegd in Settings

6. **Google OAuth Update**
   - Update redirect URI in Google Cloud Console:
   - `https://your-app.railway.app/api/auth/callback`

### Railway CLI Deployment (Alternatief)

```bash
# Installeer Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialiseer project
railway init

# Deploy
railway up

# Set environment variables
railway variables set GOOGLE_CLIENT_ID=your_value
railway variables set GOOGLE_CLIENT_SECRET=your_value
railway variables set GEMINI_API_KEY=your_value
# ... etc
```

## 🔧 Production Optimalisaties

### Voor Railway Deployment:

1. **Frontend Build Integratie**
```bash
# In package.json van root, voeg toe:
{
  "scripts": {
    "build": "cd jarvis-frontend && npm install && npm run build && cp -r dist/* ../jarvis-backend/src/static/",
    "start": "cd jarvis-backend && gunicorn --bind 0.0.0.0:$PORT wsgi:application"
  }
}
```

2. **Database Migraties**
```python
# In wsgi.py, voeg toe:
with app.app_context():
    db.create_all()
```

3. **Static Files**
Railway serveert automatisch static files via Flask.

## 🔒 Security Checklist

### Voor Productie:
- [ ] Sterke SECRET_KEY en JWT_SECRET_KEY
- [ ] HTTPS ingeschakeld (Railway doet dit automatisch)
- [ ] Environment variables veilig opgeslagen
- [ ] Google OAuth redirect URI's bijgewerkt
- [ ] Rate limiting geconfigureerd
- [ ] Database backups ingesteld

## 🚨 Troubleshooting

### Veel voorkomende problemen:

1. **Google API Errors**
   - Controleer of alle APIs zijn ingeschakeld
   - Verify OAuth credentials
   - Check redirect URI's

2. **Database Errors**
   - Zorg dat DATABASE_URL correct is
   - Run database migrations

3. **Railway Build Errors**
   - Check build logs in Railway dashboard
   - Verify all dependencies in requirements.txt
   - Ensure Python version compatibility

4. **Frontend Not Loading**
   - Verify frontend is built en gekopieerd naar static/
   - Check CORS settings in Flask

## 📞 Support

- **Documentatie**: `jarvis_documentation.pdf`
- **GitHub Issues**: Voor bug reports
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)

## 🎉 Success!

Na succesvolle deployment:
- Lokaal: http://localhost:5173
- Railway: https://your-app.railway.app

Jarvis is nu klaar om uw Google Workspace te beheren! 🤖✨

