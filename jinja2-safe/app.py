from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = "<h2>Hello {{ name }}</h2>"

@app.route("/")
def index():
    name = request.args.get("name", "world")
    # SAFE: user input passed as data, not template source
    return render_template_string(PAGE, name=name)

app.run(host="0.0.0.0", port=5000)