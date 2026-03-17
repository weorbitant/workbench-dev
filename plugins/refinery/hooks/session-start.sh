#!/usr/bin/env bash
# SessionStart hook for refinery plugin

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Build skill catalog from SKILL.md frontmatter
skill_catalog="## refinery — Available Skills\n\n"
skill_catalog+="Use these skills via the Skill tool with the \`refinery:\` prefix.\n\n"
skill_catalog+="| Skill | Description |\n|-------|-------------|\n"

for skill_dir in "${PLUGIN_ROOT}"/skills/*/; do
    skill_file="${skill_dir}SKILL.md"
    if [ -f "$skill_file" ]; then
        skill_name=$(sed -n 's/^name: *//p' "$skill_file" | head -1)
        skill_desc=$(sed -n 's/^description: *"\{0,1\}//p' "$skill_file" | sed 's/"$//' | head -1)
        if [ -n "$skill_name" ]; then
            skill_catalog+="| \`refinery:${skill_name}\` | ${skill_desc} |\n"
        fi
    fi
done

skill_catalog+="\nInvoke any skill with: \`/refinery:<skill-name> [args]\`"

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
