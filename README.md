# Server-Side Template Injection (SSTI) Lab

A hands-on vulnerability lab demonstrating Server-Side Template Injection (SSTI) in Python/Flask (Jinja2), highlighting exploitation to Remote Code Execution (RCE) and secure remediation practices.

---

## Architecture Overview

| Port | Service | Status | Description |
| :--- | :--- | :--- | :--- |
| `3001` | Vulnerable Service | **VULNERABLE** | Dynamically concatenates user input directly into the template string before compilation. |
| `3002` | Secure Service | **SECURE** | Uses static template strings and passes user input via template context variables. |

---

## Vulnerability Analysis

### Root Cause
SSTI occurs when user-supplied input is embedded directly into a template structure rather than being passed as context data. The template engine treats attacker-controlled input as native template code instead of plaintext strings.

### Vulnerable Code (`:3001`)
```python
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def index():
    name = request.args.get("name", "Guest")
    # Flaw: String formatting introduces untrusted input directly into the template syntax
    template = f"Hello {name}"
    return render_template_string(template)

if __name__ == "__main__":
    app.run(port=3001)