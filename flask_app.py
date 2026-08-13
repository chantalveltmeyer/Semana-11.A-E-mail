from flask import Flask, render_template, request, session, flash

app = Flask(__name__)

app.secret_key = "chave-secreta"


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        name = request.form.get("name")

        if "name" in session and session["name"] != name:
            flash("Looks like you have changed your name!")

        session["name"] = name

    return render_template(
        "index.html",
        name=session.get("name")
    )