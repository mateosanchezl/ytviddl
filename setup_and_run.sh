#!/bin/bash

# YouTube Video Downloader - Setup and Run Script
# This script automates the entire setup process and starts both servers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.7+ and try again."
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check npm
if ! command_exists npm; then
    print_error "npm is not installed. Please install npm and try again."
    exit 1
fi

# Check FFmpeg
if ! command_exists ffmpeg; then
    print_warning "FFmpeg is not installed. The app may not work properly."
    print_warning "Please install FFmpeg:"
    print_warning "  macOS: brew install ffmpeg"
    print_warning "  Ubuntu/Debian: sudo apt install ffmpeg"
    print_warning "  Windows: Download from https://ffmpeg.org/download.html"
    echo
fi

print_success "Prerequisites check completed"

# Check if ports are available
print_status "Checking port availability..."

# if port_in_use 5000; then
#     print_error "Port 5000 is already in use. Please stop the service using this port and try again."
#     exit 1
# fi

if port_in_use 5173; then
    print_error "Port 5173 is already in use. Please stop the service using this port and try again."
    exit 1
fi

print_success "Ports are available"

# Setup Python backend
print_status "Setting up Python backend..."

cd py

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

print_success "Python backend setup completed"

# Setup Node.js frontend
print_status "Setting up Node.js frontend..."

cd ../front

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

print_success "Node.js frontend setup completed"

# Start backend server
print_status "Starting Python backend server..."
cd ../py
source .venv/bin/activate
python api.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! port_in_use 5000; then
    print_error "Backend server failed to start"
    cleanup
    exit 1
fi

print_success "Backend server started on http://localhost:5000"

# Start frontend server
print_status "Starting React frontend server..."
cd ../front
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! port_in_use 5173; then
    print_error "Frontend server failed to start"
    cleanup
    exit 1
fi

print_success "Frontend server started on http://localhost:5173"

# Open browser
print_status "Opening browser..."
if command_exists open; then
    # macOS
    open http://localhost:5173
elif command_exists xdg-open; then
    # Linux
    xdg-open http://localhost:5173
elif command_exists start; then
    # Windows
    start http://localhost:5173
else
    print_warning "Could not automatically open browser. Please manually navigate to http://localhost:5173"
fi

print_success "YouTube Video Downloader is now running!"
echo
echo -e "${GREEN}Frontend:${NC} http://localhost:5173"
echo -e "${GREEN}Backend API:${NC} http://localhost:5000"
echo
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo

# Wait for user to stop
wait 