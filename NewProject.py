from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

project_nutzer = []
project_funding = []

@app.route("/NewProject")
def NewProject():    
    return render_template("NewProjectUI.html", nutzer=project_nutzer, funder=project_funding)

@app.route("/NewProject/nutzer_hinzufuegen", methods=['POST'])
def nutzer_hinzufuegen():
    name = request.form['name']
    project_nutzer.append(name)
    return redirect(url_for("NewProject"))

@app.route("/NewProject/funding_hinzufuegen", methods=['POST'])
def funding_hinzufuegen():
    name = request.form['name']
    project_funding.append(name)
    return redirect(url_for("NewProject"))


if __name__ == "__main__":
    app.run(debug=True)