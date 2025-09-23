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
EOF

unset ANTHROPIC_API_KEY

# Make the key script executable
chmod +x .claude/anthropic_key.sh

echo "Claude API key helper configured successfully."