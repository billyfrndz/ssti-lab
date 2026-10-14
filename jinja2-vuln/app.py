from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def index():
    name = request.args.get("name", "world")
    # VULNERABLE: user input rendered as template source
    return render_template_string("<h2>Hello " + name + "</h2>")

app.run(host="0.0.0.0", port=5000)