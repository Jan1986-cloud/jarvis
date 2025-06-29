#!/bin/bash
set -e

# Build frontend and copy assets to backend static folder
cd jarvis-frontend
npm install
npm run build
cd ..

cp -r jarvis-frontend/dist/. jarvis-backend/src/static/