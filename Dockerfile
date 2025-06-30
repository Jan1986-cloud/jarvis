FROM node:20-alpine AS frontend-builder

WORKDIR /app/jarvis-frontend
COPY jarvis-frontend/ ./
RUN npm install
RUN chmod +x ./node_modules/.bin/vite
RUN npm run build

FROM python:3.10-bullseye

WORKDIR /app

COPY jarvis-backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY jarvis-backend/ ./

COPY --from=frontend-builder /app/jarvis-frontend/dist ./src/static

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--chdir", "src", "wsgi:app"]