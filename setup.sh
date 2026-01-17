#!/bin/bash
# Setup script for Phoenix Insurance Scraper

echo "🏥 Phoenix Insurance Scraper - Setup"
echo "====================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed!"
    exit 1
fi
echo "✅ Python3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install playwright requests beautifulsoup4 aiohttp pydantic python-dotenv

# Install Playwright browsers
echo ""
echo "🌐 Installing Chromium browser..."
playwright install chromium
playwright install-deps chromium

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/users

echo ""
echo "====================================="
echo "✅ Setup complete!"
echo ""
echo "To run the scraper:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the scraper: python scrape_phoenix.py"
echo ""
