from flask import Flask, render_template, request, redirect, url_for

import sqlite3


app = Flask(__name__)

app.secret_key = "uma-chave-secreta"


# ==========================================================
# CONFIGURAÇÃO DO BANCO
# ==========================================================

DATABASE = "banco.db"


def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


# ==========================================================
# CRIAR BANCO E TABELAS
# ==========================================================

def criar_banco():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Tabela de funções
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            funcao_id INTEGER NOT NULL,
            FOREIGN KEY (funcao_id) REFERENCES funcoes(id)
        )
    """)

    # Cadastra as três funções necessárias
    cursor.execute("""
        INSERT OR IGNORE INTO funcoes (nome)
        VALUES ('Administrator')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO funcoes (nome)
        VALUES ('Moderator')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO funcoes (nome)
        VALUES ('User')
    """)

    conexao.commit()
    conexao.close()


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================

@app.route("/", methods=["GET", "POST"])
def index():

    # ------------------------------------------------------
    # CADASTRAR USUÁRIO
    # ------------------------------------------------------

    if request.method == "POST":

        nome = request.form.get("nome")
        funcao = request.form.get("funcao")

        # Verifica se os campos foram preenchidos
        if nome and funcao:

            conexao = conectar_banco()
            cursor = conexao.cursor()

            # Procura a função escolhida
            cursor.execute("""
                SELECT id
                FROM funcoes
                WHERE nome = ?
            """, (funcao,))

            resultado = cursor.fetchone()

            if resultado:

                funcao_id = resultado["id"]

                # Insere o usuário no banco
                cursor.execute("""
                    INSERT INTO usuarios (nome, funcao_id)
                    VALUES (?, ?)
                """, (nome, funcao_id))

                conexao.commit()

            conexao.close()

        # Atualiza a página
        return redirect(url_for("index"))


    # ------------------------------------------------------
    # BUSCAR USUÁRIOS
    # ------------------------------------------------------

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            usuarios.id,
            usuarios.nome,
            funcoes.nome AS funcao
        FROM usuarios
        INNER JOIN funcoes
            ON usuarios.funcao_id = funcoes.id
        ORDER BY usuarios.id
    """)

    usuarios = cursor.fetchall()


    # ------------------------------------------------------
    # CONTADOR DE USUÁRIOS
    # ------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS quantidade
        FROM usuarios
    """)

    quantidade_usuarios = cursor.fetchone()["quantidade"]


    # ------------------------------------------------------
    # BUSCAR FUNÇÕES
    # ------------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            nome
        FROM funcoes
        ORDER BY id
    """)

    funcoes = cursor.fetchall()


    # ------------------------------------------------------
    # CONTADOR DE FUNÇÕES
    # ------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS quantidade
        FROM funcoes
    """)

    quantidade_funcoes = cursor.fetchone()["quantidade"]


    # ------------------------------------------------------
    # AGRUPAR USUÁRIOS POR FUNÇÃO
    # ------------------------------------------------------

    usuarios_por_funcao = {}

    for funcao in funcoes:

        cursor.execute("""
            SELECT usuarios.nome
            FROM usuarios
            WHERE usuarios.funcao_id = ?
            ORDER BY usuarios.id
        """, (funcao["id"],))

        usuarios_por_funcao[funcao["nome"]] = cursor.fetchall()


    conexao.close()


    # ------------------------------------------------------
    # ENVIAR DADOS PARA O HTML
    # ------------------------------------------------------

    return render_template(
        "index.html",

        usuarios=usuarios,

        funcoes=funcoes,

        usuarios_por_funcao=usuarios_por_funcao,

        quantidade_usuarios=quantidade_usuarios,

        quantidade_funcoes=quantidade_funcoes
    )


# ==========================================================
# CRIAR O BANCO QUANDO A APLICAÇÃO INICIAR
# ==========================================================

criar_banco()


# ==========================================================
# EXECUTAR LOCALMENTE
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)
