#!/bin/bash

# MCP Platform Startup Script
# This script starts both the FastAPI MCP server and React client

echo "🚀 Starting MCP Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python; then
    echo -e "${RED}❌ Python is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please create it with your OPENAI_API_KEY${NC}"
    exit 1
fi

# Install Python dependencies if needed
# echo "📦 Installing Python dependencies..."
# pip install -r requierements.txt > /dev/null 2>&1

# Install React dependencies if needed
# echo "📦 Installing React dependencies..."
# cd mcp_react-client
# npm install > /dev/null 2>&1
# cd ..

# Function to start MCP server
start_mcp_server() {
    echo -e "${BLUE}🔧 Starting MCP Server...${NC}"
    python mcp_server_http.py &
    MCP_SERVER_PID=$!
    echo "MCP Server PID: $MCP_SERVER_PID"
    sleep 3
}

# Function to start FastAPI web server
start_fastapi_server() {
    echo -e "${BLUE}🌐 Starting FastAPI Web Server...${NC}"
    python mcp_host.py &
    FASTAPI_PID=$!
    echo "FastAPI Server PID: $FASTAPI_PID"
    sleep 4
}

# Function to start React client
start_react_client() {
    echo -e "${BLUE}⚛️  Starting React Client...${NC}"
    cd mcp_react_client
    npm start &
    REACT_PID=$!
    echo "React Client PID: $REACT_PID"
    cd ..
}

# Function to cleanup processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down MCP Platform...${NC}"
    
    if [ ! -z "$MCP_SERVER_PID" ]; then
        kill $MCP_SERVER_PID 2>/dev/null
        echo "✅ MCP Server stopped"
    fi
    
    if [ ! -z "$FASTAPI_PID" ]; then
        kill $FASTAPI_PID 2>/dev/null
        echo "✅ FastAPI Server stopped"
    fi
    
    if [ ! -z "$REACT_PID" ]; then
        kill $REACT_PID 2>/dev/null
        echo "✅ React Client stopped"
    fi
    
    echo -e "${GREEN}👋 MCP Platform stopped successfully${NC}"
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup INT

# Enable python virtual environment if needed
if [ -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}🔄 Activating Python virtual environment...${NC}"
    source venv/bin/activate
fi

# Start all services
start_mcp_server
start_fastapi_server
start_react_client

echo -e "\n${GREEN}🎉 MCP Platform is now running!${NC}"
echo -e "${GREEN}📱 React Client: ${NC}http://localhost:3000"
echo -e "${GREEN}🔧 FastAPI Server: ${NC}http://localhost:8001"
echo -e "${GREEN}⚙️  MCP Server: ${NC}http://localhost:8000"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for user input
wait
