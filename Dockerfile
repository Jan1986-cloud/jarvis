FROM node:18-alpine AS frontend-builder

WORKDIR /app/jarvis-frontend
COPY jarvis-frontend/ ./
RUN npm install
RUN npm run build

FROM python:3.10-slim

WORKDIR /app

COPY jarvis-backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY jarvis-backend/ ./

COPY --from=frontend-builder /app/jarvis-frontend/dist ./src/static

CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 wsgi:application