from flask import Flask, abort, render_template

app = Flask(__name__,
            template_folder= 'template')

app.config['ENV'] = 'Development'
app.config['DEBUG'] = True

@app.route("/")
def index():
    owner = " Hi! Everybody !"
    return render_template('template.html',
                            owner = owner)

@app.route("/favicon.ico")
def favicon():
    return abort(404)

app.run(port='8000')