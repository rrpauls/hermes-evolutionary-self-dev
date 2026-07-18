#!/bin/bash
#
# install-evolutionary-skills.sh
# Automatic installation of Evolutionary Self-Development skills into Hermes Agent
#
# Usage:
#   1. Clone the fork: git clone https://github.com/YOUR_USERNAME/hermes-evolutionary-self-dev.git
#   2. cd hermes-evolutionary-self-dev
#   3. ./install-evolutionary-skills.sh
#
# The script copies all meta-skills from optional-skills/evolutionary-self-dev/
# into ~/.hermes/skills/evolutionary-self-dev/
#
# After installation:
#   - Restart Hermes or use the /skills command in chat
#   - AGENTS.md will be automatically copied (see below)
#

set -e

echo "=========================================="
echo "  Hermes Evolutionary Self-Development"
echo "  Skills Installer"
echo "=========================================="
echo

# Resolve paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/optional-skills/evolutionary-self-dev"
DEST_DIR="$HOME/.hermes/skills/evolutionary-self-dev"
AGENTS_SOURCE="$SCRIPT_DIR/AGENTS.md"
AGENTS_DEST="$HOME/.hermes/AGENTS.md"

# Check that the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Skills directory not found: $SOURCE_DIR"
    echo "   Make sure you are running the script from the fork root."
    exit 1
fi

echo "📁 Skills source: $SOURCE_DIR"
echo "📁 Destination:     $DEST_DIR"
echo

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    echo "📂 Creating directory $DEST_DIR..."
    mkdir -p "$DEST_DIR"
else
    echo "📂 Directory already exists. Will perform update."
fi

# Copy all skills
echo "📦 Copying skills..."
cp -r "$SOURCE_DIR"/* "$DEST_DIR"/

echo "✅ Skills copied successfully!"

# Copy AGENTS.md (if exists)
if [ -f "$AGENTS_SOURCE" ]; then
    echo "📄 Copying AGENTS.md..."
    cp "$AGENTS_SOURCE" "$AGENTS_DEST"
    echo "✅ AGENTS.md copied to $AGENTS_DEST"
else
    echo "⚠️  AGENTS.md not found in the fork (skipping)"
fi
echo

# List installed skills
echo "📋 Installed Evolutionary Self-Development skills:"
ls -1 "$DEST_DIR" | sed 's/^/   - /'
echo

# Integration recommendations
echo "=========================================="
echo "  Next Steps"
echo "=========================================="
echo
echo "1. Restart Hermes (or use /skills in chat to refresh)."
echo
echo "2. AGENTS.md has been automatically copied to:"
echo "   $AGENTS_DEST"
echo
echo "   It contains ready-to-use instructions and triggers for running"
echo "   hermes-evolution-orchestrator after complex tasks."
echo
echo "3. Recommended first tests:"
echo "   - Activate 'hermes-evolution-orchestrator' manually"
echo "   - Try 'ooda-framework' on any uncertain decision"
echo "   - Run 'loop-auditor' to audit the current cycle"
echo
echo "=========================================="
echo "  Installation completed successfully!"
echo "=========================================="
