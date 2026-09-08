from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# CONEXÃO COM O BANCO
def conectar_banco():
    banco = sqlite3.connect("banco.db")
    banco.row_factory = sqlite3.Row
    return banco


# CRIAÇÃO DO BANCO
def criar_banco():
    banco = conectar_banco()

    banco.execute("""
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            disciplina TEXT NOT NULL,
            descricao TEXT NOT NULL
        )
    """)

    banco.commit()
    banco.close()


# PÁGINA INICIAL
@app.route("/")
def inicio():
    return render_template("index.html")


# LOGIN
@app.route("/login")
def login():
    return render_template("login.html")


# CADASTRO DE USUÁRIO
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


# AJUDA
@app.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")


# CADASTRAR ATIVIDADE
@app.route("/atividades/cadastrar", methods=["GET", "POST"])
def cadastrar_atividade():

    if request.method == "POST":
        titulo = request.form["titulo"]
        disciplina = request.form["disciplina"]
        descricao = request.form["descricao"]

        banco = conectar_banco()

        banco.execute(
            """
            INSERT INTO atividades (titulo, disciplina, descricao)
            VALUES (?, ?, ?)
            """,
            (titulo, disciplina, descricao)
        )

        banco.commit()
        banco.close()

        return redirect("/atividades")

    return render_template("atividades.html")


# VISUALIZAR ATIVIDADES
@app.route("/atividades")
def atividades():
    banco = conectar_banco()

    atividades = banco.execute(
        "SELECT * FROM atividades"
    ).fetchall()

    banco.close()

    return render_template(
        "lista_atividades.html",
        atividades=atividades
    )


# EDITAR ATIVIDADE
@app.route("/atividades/editar/<int:id>", methods=["GET", "POST"])
def editar_atividade(id):

    banco = conectar_banco()

    atividade = banco.execute(
        "SELECT * FROM atividades WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        titulo = request.form["titulo"]
        disciplina = request.form["disciplina"]
        descricao = request.form["descricao"]

        banco.execute(
            """
            UPDATE atividades
            SET titulo = ?, disciplina = ?, descricao = ?
            WHERE id = ?
            """,
            (titulo, disciplina, descricao, id)
        )

        banco.commit()
        banco.close()

        return redirect("/atividades")

    banco.close()

    return render_template(
        "editar_atividade.html",
        atividade=atividade
    )


# INICIAR APLICAÇÃO
if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
