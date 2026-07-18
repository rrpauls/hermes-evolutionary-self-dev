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

# Определяем пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/optional-skills/evolutionary-self-dev"
DEST_DIR="$HOME/.hermes/skills/evolutionary-self-dev"
AGENTS_SOURCE="$SCRIPT_DIR/AGENTS.md"
AGENTS_DEST="$HOME/.hermes/AGENTS.md"

# Проверяем наличие исходной директории
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Ошибка: Директория с навыками не найдена: $SOURCE_DIR"
    echo "   Убедись, что ты запускаешь скрипт из корня форка."
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

# Список установленных навыков
echo "📋 Установленные Evolutionary Self-Development навыки:"
ls -1 "$DEST_DIR" | sed 's/^/   - /'
echo

# Рекомендация по интеграции
echo "=========================================="
echo "  Следующие шаги"
echo "=========================================="
echo
echo "1. Перезапусти Hermes (или используй /skills в чате для обновления)."
echo
echo "2. Файл AGENTS.md уже автоматически скопирован в:"
echo "   $AGENTS_DEST"
echo
echo "   Он содержит готовые инструкции и триггеры для запуска"
echo "   hermes-evolution-orchestrator после сложных задач."
echo
echo "3. Рекомендуемые первые тесты:"
echo "   - Активируй 'hermes-evolution-orchestrator' вручную"
echo "   - Попробуй 'ooda-framework' на любой неопределённой задаче"
echo "   - Запусти 'loop-auditor' для аудита текущего цикла"
echo
echo "=========================================="
echo "  Установка завершена успешно!"
echo "=========================================="
