# This script sets up Claude API key helper in .claude/

mkdir -p .claude

# Write settings.json
cat > .claude/settings.json <<'EOF'
{
  "apiKeyHelper": ".claude/anthropic_key.sh"
}
EOF

# Write anthropic_key.sh with your API key (replace with your real key)
cat > .claude/anthropic_key.sh <<'EOF'
#!/bin/sh
echo "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"
EOF

# Make the key script executable
chmod +x .claude/anthropic_key.sh

echo "Claude API key helper configured successfully."

