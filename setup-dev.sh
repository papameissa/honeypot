#!/bin/bash

# ============================================================
# HoneyTrap Development Environment Setup
# Automated setup script for local development
# ============================================================

set -e  # Exit on error

echo "🍯 HoneyTrap Development Setup"
echo "=============================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
if ! command -v python3.10 &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3.10+ is required but not installed."
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "  Found Python $PYTHON_VERSION"
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python3.10"
    echo "  Found Python 3.10"
fi

# Create virtual environment
echo ""
echo "✓ Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists, skipping..."
else
    $PYTHON_CMD -m venv venv
    echo "  Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  Virtual environment activated"

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "  pip upgraded"

# Install dependencies
echo ""
echo "✓ Installing Python dependencies..."
pip install -r requirements.txt
pip install -e ".[dev]"
echo "  Dependencies installed"

# Copy environment file
echo ""
echo "✓ Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "  .env already exists, skipping..."
else
    cp .env.example .env
    echo "  Created .env from template"
    echo "  ⚠️  Edit .env with your configuration settings"
fi

# Check for Docker
echo ""
echo "✓ Checking for Docker & Docker Compose..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | cut -d',' -f1)
    echo "  Docker found: v$DOCKER_VERSION"
else
    echo "  ⚠️  Docker not found (optional for local dev)"
fi

if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | awk '{print $3}' | cut -d',' -f1)
    echo "  Docker Compose found: v$COMPOSE_VERSION"
fi

# Verify installation
echo ""
echo "✓ Verifying installation..."
python -c "import flask; print(f'  Flask {flask.__version__}')"
python -c "import sqlalchemy; print(f'  SQLAlchemy {sqlalchemy.__version__}')"
python -c "import pytest; print(f'  pytest {pytest.__version__}')"

echo ""
echo "============================================================"
echo "✅ Setup complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
if [ ! -f ".env" ]; then
    echo "1. Edit .env file with your database credentials"
    echo "2. Run: make db-init"
    echo "3. Run: make run"
else
    echo "1. Run: make db-init"
    echo "2. Run: make run"
fi
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
echo "For help:"
echo "  make help"
echo ""
