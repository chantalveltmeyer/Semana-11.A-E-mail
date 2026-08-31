from flask import Flask, render_template, request, session, redirect
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "chave-secreta"

CAMINHO_BANCO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "banco.db"
)

# --------------------------------
# CONEXÃO COM O BANCO
# --------------------------------

def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


# --------------------------------
# CRIAÇÃO DAS TABELAS
# --------------------------------

def criar_banco():

    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            instituicao TEXT NOT NULL,
            disciplina TEXT NOT NULL
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


criar_banco()


# --------------------------------
# PÁGINA PRINCIPAL
# --------------------------------

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        nome = request.form.get("nome")
        sobrenome = request.form.get("sobrenome")
        instituicao = request.form.get("instituicao")
        disciplina = request.form.get("disciplina")

        # Salva os dados na sessão
        session["nome"] = nome
        session["sobrenome"] = sobrenome
        session["instituicao"] = instituicao
        session["disciplina"] = disciplina

        # Salva os dados no banco
        conexao = conectar_banco()

        conexao.execute("""
            INSERT INTO alunos
            (nome, sobrenome, instituicao, disciplina)
            VALUES (?, ?, ?, ?)
        """, (nome, sobrenome, instituicao, disciplina))

        conexao.commit()
        conexao.close()

    return render_template(
        "index.html",
        nome=session.get("nome"),
        sobrenome=session.get("sobrenome"),
        instituicao=session.get("instituicao"),
        disciplina=session.get("disciplina")
    )


# --------------------------------
# LOGIN
# --------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    mensagem = ""

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario and senha:

            conexao = conectar_banco()

            usuario_banco = conexao.execute("""
                SELECT * FROM usuarios
                WHERE usuario = ? AND senha = ?
            """, (usuario, senha)).fetchone()

            conexao.close()

            if usuario_banco:
                mensagem = "Login realizado com sucesso!"
                session["usuario"] = usuario
            else:
                mensagem = "Usuário ou senha incorretos."

        else:
            mensagem = "Informe o usuário e a senha."

    return render_template(
        "login.html",
        mensagem=mensagem
    )


# --------------------------------
# CADASTRO DE USUÁRIO
# --------------------------------

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    mensagem = ""

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario and senha:

            conexao = conectar_banco()

            try:

                conexao.execute("""
                    INSERT INTO usuarios (usuario, senha)
                    VALUES (?, ?)
                """, (usuario, senha))

                conexao.commit()

                mensagem = "Usuário cadastrado com sucesso!"

            except sqlite3.IntegrityError:

                mensagem = "Esse usuário já existe."

            conexao.close()

        else:

            mensagem = "Preencha usuário e senha."

    return render_template(
        "cadastro.html",
        mensagem=mensagem
    )


# --------------------------------
# EXECUÇÃO
# --------------------------------

if __name__ == "__main__":

    criar_banco()

    app.run(debug=True)
