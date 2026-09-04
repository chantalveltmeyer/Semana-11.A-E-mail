from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Chave usada para a sessão
app.secret_key = "chave-secreta"

# Caminho do banco de dados
CAMINHO_BANCO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "banco.db"
)


# ==========================================
# CONEXÃO COM O BANCO
# ==========================================

def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


# ==========================================
# CRIAÇÃO DO BANCO
# ==========================================

def criar_banco():

    conexao = conectar_banco()

    # --------------------------------------
    # TABELA DE ALUNOS
    # --------------------------------------

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sobrenome TEXT NOT NULL,
            instituicao TEXT NOT NULL,
            disciplina TEXT NOT NULL
        )
    """)

    # --------------------------------------
    # TABELA DE USUÁRIOS
    # --------------------------------------

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)

    # --------------------------------------
    # VERIFICA SE A COLUNA "funcao" EXISTE
    # --------------------------------------

    colunas = conexao.execute("""
        PRAGMA table_info(usuarios)
    """).fetchall()

    nomes_colunas = [coluna["name"] for coluna in colunas]

    # Se a tabela já existia sem a coluna funcao,
    # adiciona a coluna automaticamente.
    if "funcao" not in nomes_colunas:

        conexao.execute("""
            ALTER TABLE usuarios
            ADD COLUMN funcao TEXT NOT NULL DEFAULT 'User'
        """)

    conexao.commit()
    conexao.close()


# Cria o banco quando o programa inicia
criar_banco()


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    # --------------------------------------
    # CADASTRO DO ALUNO
    # --------------------------------------

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
        """, (
            nome,
            sobrenome,
            instituicao,
            disciplina
        ))

        conexao.commit()
        conexao.close()

        # Redireciona para evitar duplicação do cadastro
        return redirect(url_for("index"))

    # --------------------------------------
    # BUSCA OS USUÁRIOS CADASTRADOS
    # --------------------------------------

    conexao = conectar_banco()

    usuarios = conexao.execute("""
        SELECT id, usuario, funcao
        FROM usuarios
        ORDER BY id
    """).fetchall()

    conexao.close()

    # --------------------------------------
    # MOSTRA A PÁGINA
    # --------------------------------------

    return render_template(
        "index.html",

        nome=session.get("nome"),
        sobrenome=session.get("sobrenome"),
        instituicao=session.get("instituicao"),
        disciplina=session.get("disciplina"),

        # Envia os usuários para o HTML
        usuarios=usuarios,

        # Usuário atualmente logado
        usuario_logado=session.get("usuario"),
        funcao_logado=session.get("funcao")
    )


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    mensagem = ""

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        # Verifica se os campos foram preenchidos
        if usuario and senha:

            conexao = conectar_banco()

            usuario_banco = conexao.execute("""
                SELECT *
                FROM usuarios
                WHERE usuario = ?
                AND senha = ?
            """, (
                usuario,
                senha
            )).fetchone()

            conexao.close()

            # ----------------------------------
            # LOGIN CORRETO
            # ----------------------------------

            if usuario_banco:

                # Salva usuário na sessão
                session["usuario"] = usuario_banco["usuario"]

                # Salva a função na sessão
                session["funcao"] = usuario_banco["funcao"]

                mensagem = "Login realizado com sucesso!"

                # Vai para a página inicial
                return redirect(url_for("index"))

            # ----------------------------------
            # LOGIN INCORRETO
            # ----------------------------------

            else:

                mensagem = "Usuário ou senha incorretos."

        else:

            mensagem = "Informe o usuário e a senha."

    return render_template(
        "login.html",
        mensagem=mensagem
    )


# ==========================================
# CADASTRO DE USUÁRIO
# ==========================================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    mensagem = ""

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        # Pega a função escolhida no formulário
        funcao = request.form.get("funcao")

        # ----------------------------------
        # VERIFICA A FUNÇÃO
        # ----------------------------------

        # Só permite essas duas funções
        if funcao not in ["User", "Administrador"]:
            funcao = "User"

        # ----------------------------------
        # VERIFICA USUÁRIO E SENHA
        # ----------------------------------

        if usuario and senha:

            conexao = conectar_banco()

            try:

                # ----------------------------------
                # CADASTRA O USUÁRIO
                # ----------------------------------

                conexao.execute("""
                    INSERT INTO usuarios
                    (usuario, senha, funcao)
                    VALUES (?, ?, ?)
                """, (
                    usuario,
                    senha,
                    funcao
                ))

                conexao.commit()

                mensagem = "Usuário cadastrado com sucesso!"

            except sqlite3.IntegrityError:

                mensagem = "Esse usuário já existe."

            finally:

                conexao.close()

        else:

            mensagem = "Preencha usuário e senha."

    return render_template(
        "cadastro.html",
        mensagem=mensagem
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    # Remove os dados da sessão
    session.clear()

    return redirect(url_for("index"))


# ==========================================
# EXECUÇÃO DO SISTEMA
# ==========================================

if __name__ == "__main__":

    # Garante que o banco exista
    criar_banco()

    # Inicia o Flask
    app.run(debug=True)
