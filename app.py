from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")


if __name__ == "__main__":
    app.run(debug=True)