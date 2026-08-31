from flask import Flask, render_template, request, session

app = Flask(__name__)

app.secret_key = "chave-secreta"


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        nome = request.form.get("nome")
        sobrenome = request.form.get("sobrenome")
        instituicao = request.form.get("instituicao")
        disciplina = request.form.get("disciplina")

        # Guarda os dados
        session["nome"] = nome
        session["sobrenome"] = sobrenome
        session["instituicao"] = instituicao
        session["disciplina"] = disciplina

    return render_template(
        "index.html",

        nome=session.get("nome"),
        sobrenome=session.get("sobrenome"),
        instituicao=session.get("instituicao"),
        disciplina=session.get("disciplina")
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    mensagem = ""

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario and senha:
            mensagem = "Login enviado com sucesso!"
        else:
            mensagem = "Informe o usuário e a senha."

    return render_template(
        "login.html",
        mensagem=mensagem
    )


if __name__ == "__main__":
    app.run(debug=True)
