# Fase 1: Bouw de Node.js frontend
FROM node:18-slim as frontend-builder

# Ga naar de frontend map en kopieer de package files
WORKDIR /app/jarvis-frontend-fixed
COPY jarvis-frontend-fixed/package.json ./
COPY jarvis-frontend-fixed/package-lock.json ./
RUN npm install

# Kopieer de rest van de frontend code en bouw het
COPY jarvis-frontend-fixed/ ./
RUN npm run build


# Fase 2: Bouw de Python backend en de uiteindelijke image
FROM python:3.11-slim

WORKDIR /app

# Kopieer de requirements en installeer de Python packages
COPY jarvis-backend-fixed/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de backend code
COPY jarvis-backend-fixed/ ./

# Kopieer de gebouwde frontend-bestanden van de vorige fase naar een 'static' map
COPY --from=frontend-builder /app/jarvis-frontend-fixed/dist ./static

# Voer de applicatie uit
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "wsgi:application"]