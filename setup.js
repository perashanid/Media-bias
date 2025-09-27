#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🎯 Media Bias Detector - Setup Script');
console.log('=' * 50);

// Check if Python is available
try {
    execSync('python --version', { stdio: 'pipe' });
    console.log('✅ Python is available');
} catch (error) {
    console.log('❌ Python is not available. Please install Python 3.8+');
    process.exit(1);
}

// Check if pip is available
try {
    execSync('pip --version', { stdio: 'pipe' });
    console.log('✅ pip is available');
} catch (error) {
    console.log('❌ pip is not available. Please install pip');
    process.exit(1);
}

// Install Python dependencies
console.log('📦 Installing Python dependencies...');
try {
    execSync('pip install -r requirements.txt', { stdio: 'inherit' });
    console.log('✅ Python dependencies installed');
} catch (error) {
    console.log('⚠️  Some Python dependencies may have failed to install');
}

// Install frontend dependencies
console.log('📦 Installing frontend dependencies...');
try {
    execSync('npm install', { cwd: 'frontend', stdio: 'inherit' });
    console.log('✅ Frontend dependencies installed');
} catch (error) {
    console.log('❌ Failed to install frontend dependencies');
    process.exit(1);
}

console.log('\n🎉 Setup complete!');
console.log('Run "npm run dev" to start the full application');