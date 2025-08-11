#!/bin/bash

# LinkedIn Android Poster - Setup Script
echo "🚀 LinkedIn Android Poster - Automated Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

NPM_VERSION=$(npm --version)
print_success "npm $NPM_VERSION found"

# Install backend dependencies
print_status "Installing Python backend dependencies..."
cd backend || exit 1

if pip3 install -r requirements.txt; then
    print_success "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi

# Install frontend dependencies
print_status "Installing React frontend dependencies..."
cd ../frontend || exit 1

if npm install; then
    print_success "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

# Return to root directory
cd ..

# Setup environment file
print_status "Setting up environment configuration..."
if [ ! -f .env ]; then
    if cp .env.example .env; then
        print_success "Created .env file from template"
        print_warning "IMPORTANT: Edit .env file with your API credentials before running!"
    else
        print_error "Failed to create .env file"
        exit 1
    fi
else
    print_warning ".env file already exists - skipping creation"
fi

# Initialize database
print_status "Initializing SQLite database..."
cd backend || exit 1

if python3 -c "from database import init_db; init_db(); print('Database initialized successfully!')"; then
    print_success "Database initialized"
else
    print_error "Failed to initialize database"
    exit 1
fi

cd ..

# Make scripts executable
chmod +x start.sh
chmod +x setup.sh

print_success "Setup completed successfully!"
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Edit the .env file with your API credentials:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Get your API keys:"
echo "   📁 Reddit: https://www.reddit.com/prefs/apps (Free)"
echo "   🤖 OpenAI: https://platform.openai.com/api-keys (~$0.03/post)"
echo "   🐦 X/Twitter: https://developer.twitter.com (Optional)"
echo ""
echo "3. Start the application:"
echo "   ${GREEN}./start.sh${NC}"
echo ""
echo "4. Access your dashboard:"
echo "   🌐 http://localhost:5173"
echo ""
echo "📖 For detailed setup instructions, see:"
echo "   - README.md (Quick start guide)"
echo "   - PROJECT.md (Complete documentation)"
echo ""
print_success "Happy Android content curation! 🚀"