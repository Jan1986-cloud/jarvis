# Fase 1: Bouw de Node.js frontend
FROM node:18-slim as frontend-builder

WORKDIR /app

# Kopieer en installeer frontend dependencies
COPY jarvis-frontend-fixed/package.json ./jarvis-frontend-fixed/
COPY jarvis-frontend-fixed/package-lock.json ./jarvis-frontend-fixed/
RUN npm install --prefix jarvis-frontend-fixed

# Kopieer de rest van de frontend code en bouw het
COPY jarvis-frontend-fixed/ ./jarvis-frontend-fixed/
RUN npm run build --prefix jarvis-frontend-fixed


# Fase 2: Bouw de Python backend en de uiteindelijke image
FROM python:3.11-slim

WORKDIR /app

# Installeer Python dependencies
COPY jarvis-backend-fixed/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de backend code
COPY jarvis-backend-fixed/ .

# Kopieer de gebouwde frontend-bestanden van de vorige fase
COPY --from=frontend-builder /app/jarvis-frontend-fixed/build ./static

# Voer de applicatie uit
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "wsgi:application"]