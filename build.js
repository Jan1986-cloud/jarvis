#!/usr/bin/env node

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

try {
  console.log('Building frontend...')
  execSync('npm --prefix jarvis-frontend-fixed install', { stdio: 'inherit' })
  execSync('npm --prefix jarvis-frontend-fixed run build', { stdio: 'inherit' })

  const srcDir = path.resolve('jarvis-frontend-fixed', 'dist')
  const destDir = path.resolve('jarvis-backend-fixed', 'src', 'static')
  fs.rmSync(destDir, { recursive: true, force: true })
  fs.mkdirSync(destDir, { recursive: true })
  fs.cpSync(srcDir, destDir, { recursive: true })
  console.log('Copied frontend dist to backend static assets')
} catch (err) {
  console.error(err)
  process.exit(1)
}