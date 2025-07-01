# ⚡ JARVIS - QUICK START GIDS

> **Jarvis werkend in 5 minuten!**

## 🎯 **KIES UW METHODE:**

### 🖥️ **LOKAAL (EENVOUDIGST)**
```bash
# 1. Unzip package
unzip jarvis-complete-package.zip
cd jarvis-complete-package

# 2. Backend (Terminal 1)
cd jarvis-backend-fixed
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py

# 3. Frontend (Terminal 2)
cd jarvis-frontend-fixed
npm install
npm run dev

# 4. Open browser: http://localhost:5173
```

### 🌐 **RAILWAY CLOUD (AANBEVOLEN)**
```bash
# 1. Upload naar GitHub
cd jarvis-complete-package
git remote add origin https://github.com/USERNAME/jarvis-ai-assistant.git
git push -u origin main

# 2. Deploy op Railway
# - Ga naar railway.app
# - "Deploy from GitHub"
# - Selecteer repository
# - Set environment variables
# - Deploy!
```

### 🐳 **DOCKER (GEVORDERD)**
```bash
cd jarvis-complete-package
docker-compose up -d
# Open browser: http://localhost:3000
```

## ✅ **VEREISTEN:**
- **Python 3.10+** ([Download](https://python.org))
- **Node.js 18+** ([Download](https://nodejs.org))
- **Git** (voor GitHub upload)

## 🎭 **TEST JARVIS:**
```
User: "Hallo Jarvis"
Jarvis: "Natuurlijk meneer, ik voer dit direct uit ondanks mijn twijfels over de methode."

User: "Noem me dokter"  
Jarvis: "Meneer, ik zal u dokter gebruiken, meneer."
```

## 🚨 **PROBLEMEN?**
- **Python/Node.js niet gevonden**: Download en herstart terminal
- **Port in gebruik**: Gebruik andere terminal of herstart computer
- **Build errors**: Check internet verbinding en probeer opnieuw

**Meer hulp**: Zie `COMPLETE_INSTALLATIE_GIDS.md`

---
*"Meneer, ik ben klaar om u te dienen."* - Jarvis 🤖

