#!/bin/bash
# Paper Review System - Dependency Checker
# Checks if all required Python packages are installed

MISSING=()

check_package() {
    python3 -c "import $1" 2>/dev/null
    if [ $? -ne 0 ]; then
        MISSING+=("$2")
    fi
}

# Check core dependencies
check_package "mcp" "mcp>=1.0.0"
check_package "pymupdf" "pymupdf4llm>=0.2.9"
check_package "pydantic" "pydantic>=2.0"
check_package "httpx" "httpx>=0.27.0"
check_package "PIL" "Pillow>=10.0"

# Check optional (marker-pdf)
python3 -c "import marker" 2>/dev/null
MARKER_OK=$?

if [ ${#MISSING[@]} -eq 0 ]; then
    echo "✅ All required dependencies are installed."
    if [ $MARKER_OK -ne 0 ]; then
        echo "ℹ️  Optional: marker-pdf not installed (ML-based LaTeX recovery unavailable, pymupdf fallback will be used)"
    fi
    exit 0
else
    echo "❌ Missing dependencies detected:"
    for pkg in "${MISSING[@]}"; do
        echo "   - $pkg"
    done
    echo ""
    echo "To install all dependencies, run:"
    echo "   pip install -r \${CLAUDE_PLUGIN_ROOT}/requirements.txt"
    echo ""
    echo "Or install individually:"
    echo "   pip install ${MISSING[*]}"
    exit 1
fi
