#!/bin/bash

# VideoMilker Installation Script
# This script installs VideoMilker globally so you can use 'vmx' from anywhere

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

echo "🎬 VideoMilker Installation"
echo "==========================="

# Get the script directory (works regardless of where script is called from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Installing from: $SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    print_info "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_status "Python $PYTHON_VERSION found"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed or not in PATH"
    print_info "Please install pip3"
    exit 1
fi

print_status "pip3 found"

# Check for system dependencies
print_info "Checking system dependencies..."

# Check for ffmpeg (optional but recommended)
if command -v ffmpeg &> /dev/null; then
    print_status "ffmpeg found"
else
    print_warning "ffmpeg not found (optional but recommended for video processing)"
    print_info "Install ffmpeg: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)"
fi

# Check for curl (required for some downloads)
if command -v curl &> /dev/null; then
    print_status "curl found"
else
    print_error "curl is required but not found"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    print_info "Creating virtual environment..."
    cd "$SCRIPT_DIR"
    python3 -m venv .venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
cd "$SCRIPT_DIR"
source .venv/bin/activate

# Verify virtual environment activation
if [ -z "$VIRTUAL_ENV" ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

print_status "Virtual environment activated: $VIRTUAL_ENV"

# Upgrade pip (skip if there are issues)
print_info "Checking pip version..."
if ! python -m pip install --upgrade pip >/dev/null 2>&1; then
    print_warning "Could not upgrade pip, continuing with current version"
else
    print_status "Pip upgraded successfully"
fi

# Install dependencies
print_info "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    if ! pip install -r requirements.txt; then
        print_warning "Some dependencies failed to install, trying to continue..."
        print_info "This might be due to architecture compatibility issues"
    else
        print_status "Dependencies installed"
    fi
else
    print_error "requirements.txt not found"
    exit 1
fi

# Install the package in development mode
print_info "Installing VideoMilker..."
if ! pip install -e .; then
    print_warning "Package installation had issues, but continuing..."
else
    print_status "VideoMilker package installed successfully"
fi

# Verify installation
if ! python -c "import videomilker" 2>/dev/null; then
    print_warning "Could not import videomilker package"
    print_info "This might be due to dependency issues, but continuing with installation..."
else
    print_status "VideoMilker package verified"
fi

# Create wrapper script
print_info "Creating wrapper script..."

WRAPPER_SCRIPT="#!/bin/bash
# VideoMilker Wrapper Script
# This script activates the virtual environment and runs vmx

# Get the directory where this script is located
SCRIPT_DIR=\"$SCRIPT_DIR\"

# Activate the virtual environment
if [ -f \"\$SCRIPT_DIR/.venv/bin/activate\" ]; then
    source \"\$SCRIPT_DIR/.venv/bin/activate\"
else
    echo \"Error: Virtual environment not found at \$SCRIPT_DIR/.venv\"
    exit 1
fi

# Run vmx with all arguments
python -m videomilker.main \"\$@\"
"

# Write the wrapper script
echo "$WRAPPER_SCRIPT" > /tmp/vmx_wrapper

# Test the wrapper script
print_info "Testing wrapper script..."
if ! bash /tmp/vmx_wrapper --version >/dev/null 2>&1; then
    print_warning "Wrapper script test failed, but continuing..."
    print_info "This might be due to dependency issues"
else
    print_status "Wrapper script test passed"
fi

# Install globally
print_info "Installing vmx command..."

if command -v sudo &> /dev/null; then
    print_info "Installing globally (requires sudo)..."
    sudo cp /tmp/vmx_wrapper /usr/local/bin/vmx
    sudo chmod +x /usr/local/bin/vmx
    print_status "vmx installed globally at /usr/local/bin/vmx"
    INSTALL_PATH="/usr/local/bin/vmx"
else
    print_warning "Could not install globally (no sudo). Installing to ~/.local/bin..."
    mkdir -p ~/.local/bin
    cp /tmp/vmx_wrapper ~/.local/bin/vmx
    chmod +x ~/.local/bin/vmx
    print_status "vmx installed at ~/.local/bin/vmx"
    INSTALL_PATH="~/.local/bin/vmx"
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        print_info "Add this line to your shell configuration file (~/.bashrc, ~/.zshrc, or ~/.profile):"
        echo "   export PATH=\"\$PATH:\$HOME/.local/bin\""
    fi
fi

# Clean up
rm /tmp/vmx_wrapper

# Final verification
print_info "Verifying installation..."
if command -v vmx &> /dev/null; then
    VMX_VERSION=$(vmx --version 2>/dev/null || echo "unknown")
    print_status "vmx command verified: $VMX_VERSION"
else
    print_warning "vmx command not found in PATH"
    print_info "Try restarting your terminal or manually add to PATH"
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "You can now use VideoMilker with these commands:"
echo ""
echo "  vmx                    - Open the main menu"
echo "  vmx --link <URL>       - Quick download (alias: vmx -l <URL>)"
echo "  vmx --help             - Show help"
echo "  vmx --version          - Show version"
echo ""
echo "Examples:"
echo "  vmx --link https://youtube.com/watch?v=example"
echo "  vmx -l https://youtube.com/watch?v=example"
echo ""
echo "Installation details:"
echo "  📁 Package location: $SCRIPT_DIR"
echo "  🔧 Virtual environment: $SCRIPT_DIR/.venv"
echo "  📦 vmx command: $INSTALL_PATH"
echo ""
echo "If vmx is not found, try:"
echo "  1. Restart your terminal"
echo "  2. Add ~/.local/bin to your PATH (if installed locally)"
echo "  3. Or run: source $SCRIPT_DIR/.venv/bin/activate && python -m videomilker.main"
echo ""
echo "To uninstall:"
if [ "$INSTALL_PATH" = "/usr/local/bin/vmx" ]; then
    echo "  sudo rm /usr/local/bin/vmx"
else
    echo "  rm ~/.local/bin/vmx"
fi
echo "  rm -rf $SCRIPT_DIR/.venv"
echo "" 