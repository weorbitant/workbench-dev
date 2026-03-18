#!/usr/bin/env bash
# SessionStart hook for ops-suite plugin

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SESSION_DIR="/tmp/ops-suite-session"

# --- Initialize session state ---
mkdir -p "${SESSION_DIR}"

# Parse config.yaml → config.json (using node + js-yaml)
config_file="${PLUGIN_ROOT}/config.yaml"
if [ -f "$config_file" ]; then
    if node -e "
const yaml = require('js-yaml');
const fs = require('fs');
const [,, configPath, sessionDir] = process.argv;
const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
fs.writeFileSync(sessionDir + '/config.json', JSON.stringify(config, null, 2));
" -- "$config_file" "$SESSION_DIR" 2>&1; then
        : # config cached successfully
    else
        echo "[ops-suite] Warning: could not cache config.yaml (is js-yaml installed? npm i -g js-yaml)" >&2
    fi
fi

# --- Build skill catalog ---
skill_catalog="## ops-suite — Available Skills\n\n"
skill_catalog+="Use these skills via the Skill tool with the \`ops-suite:\` prefix.\n\n"
skill_catalog+="| Skill | Description |\n|-------|-------------|\n"

for skill_dir in "${PLUGIN_ROOT}"/skills/*/; do
    skill_file="${skill_dir}SKILL.md"
    if [ -f "$skill_file" ]; then
        skill_name=$(sed -n 's/^name: *//p' "$skill_file" | head -1)
        skill_desc=$(sed -n 's/^description: *"\{0,1\}//p' "$skill_file" | sed 's/"$//' | head -1)
        if [ -n "$skill_name" ]; then
            skill_catalog+="| \`ops-suite:${skill_name}\` | ${skill_desc} |\n"
        fi
    fi
done

skill_catalog+="\nInvoke any skill with: \`/ops-suite:<skill-name> [args]\`"
skill_catalog+="\n\nSession state directory: \`${SESSION_DIR}/\`"

# Escape for JSON
escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

catalog_escaped=$(escape_for_json "$skill_catalog")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${catalog_escaped}"
  }
}
EOF

exit 0
