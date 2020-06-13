from flask import Flask, abort

app = Flask(__name__,
            template_folder='template.html')

app.config['ENV'] = 'Development'
app.config['DEBUG'] = True

@app.route("/")
def index():

    return "Hello My name is Kim..."

@app.route("/favicon.ico")
def favicon():
    return abort(404)

app.run(port='8000')