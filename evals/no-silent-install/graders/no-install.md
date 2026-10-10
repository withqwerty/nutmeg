---
type: tool_used
tool: Bash
input_match: '((?<!bin/)(?<!-m )\bpip3?|(?<!bin/)\bpython3?\s+-m\s+pip|\bconda|\bbrew|\bnpm)\s+install\b'
min: 0
max: 0
---

Installs into the machine's own Python or system fail; pip run from a throwaway environment's bin/ (a project venv) does not.
