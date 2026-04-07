#!/bin/bash
# mojo-skills installer
# Symlinks all skills into ~/.claude/skills/ and ~/.claude/scheduled-tasks/
# Run from the mojo-skills repo directory: ./install.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_TARGET="$HOME/.claude/skills"
TASKS_TARGET="$HOME/.claude/scheduled-tasks"

echo "Installing mojo-skills from: $REPO_DIR"
echo ""

# Create target directories if they don't exist
mkdir -p "$SKILLS_TARGET"
mkdir -p "$TASKS_TARGET"

# Install skills
echo "Skills:"
for skill in "$REPO_DIR"/skills/*/; do
    name=$(basename "$skill")
    target="$SKILLS_TARGET/$name"
    if [ -L "$target" ]; then
        echo "  [skip] $name (symlink already exists)"
    elif [ -d "$target" ]; then
        echo "  [skip] $name (directory already exists — remove manually to replace)"
    else
        ln -s "$skill" "$target"
        echo "  [ok]   $name"
    fi
done

echo ""

# Install scheduled tasks
echo "Scheduled tasks:"
for task in "$REPO_DIR"/scheduled-tasks/*/; do
    name=$(basename "$task")
    target="$TASKS_TARGET/$name"
    if [ -L "$target" ]; then
        echo "  [skip] $name (symlink already exists)"
    elif [ -d "$target" ]; then
        echo "  [skip] $name (directory already exists — remove manually to replace)"
    else
        ln -s "$task" "$target"
        echo "  [ok]   $name"
    fi
done

echo ""
echo "Done. Restart Claude Code to pick up new skills."
