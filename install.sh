#!/bin/bash

# VideoMilker Global Installation Script
# This script installs VideoMilker globally so you can use 'vmx' from anywhere

set -e

echo "🎬 VideoMilker Global Installation"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed or not in PATH"
    exit 1
fi

echo "✅ Python and pip found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "🔗 Installing VideoMilker globally..."
pip install -e .

# Create a global symlink for vmx
echo "🔗 Creating global symlink..."

# Get the Python executable path from the virtual environment
PYTHON_PATH=$(which python)
SCRIPT_PATH="$PYTHON_PATH -m videomilker.main"

# Create a wrapper script
cat > /tmp/vmx << EOF
#!/bin/bash
# VideoMilker wrapper script
source $(pwd)/.venv/bin/activate
python -m videomilker.main "\$@"
EOF

chmod +x /tmp/vmx

# Try to install globally (requires sudo on some systems)
if command -v sudo &> /dev/null; then
    echo "🔐 Installing globally (requires sudo)..."
    sudo cp /tmp/vmx /usr/local/bin/vmx
    sudo chmod +x /usr/local/bin/vmx
    echo "✅ vmx installed globally at /usr/local/bin/vmx"
else
    echo "⚠️  Could not install globally (no sudo). Installing to ~/.local/bin..."
    mkdir -p ~/.local/bin
    cp /tmp/vmx ~/.local/bin/vmx
    chmod +x ~/.local/bin/vmx
    echo "✅ vmx installed at ~/.local/bin/vmx"
    echo "💡 Add ~/.local/bin to your PATH if not already there:"
    echo "   export PATH=\$PATH:~/.local/bin"
fi

# Clean up
rm /tmp/vmx

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
echo "If vmx is not found, try:"
echo "  1. Restart your terminal"
echo "  2. Add ~/.local/bin to your PATH"
echo "  3. Or run: source .venv/bin/activate && python -m videomilker.main"
echo "" 