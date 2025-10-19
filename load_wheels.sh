#!/bin/bash

WHEELS_DIR="wheels"
WHEELS_LIST="wheels_list.txt"

echo "🔄 Updating Scrapy wheels..."

# Criar diretório se não existir
mkdir -p "$WHEELS_DIR"

# Limpar wheels antigos
rm -f "$WHEELS_DIR"/*.whl

# Baixar Scrapy e dependências
echo "📦 Downloading wheels..."
echo "$LIB_LIST"
pip3 download --python-version 3.12 --only-binary=:all: -d "$WHEELS_DIR" scrapy

# Gerar lista de wheels
echo "📝 Generating wheels_list.txt..."
find "$WHEELS_DIR" -type f -name "*.whl" -printf '\047%f\047,\n' > "$WHEELS_LIST"

echo "✅ Done! Wheels updated."
echo "📊 Total wheels: $(wc -l < $WHEELS_LIST)"