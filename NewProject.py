from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

#List to safe the members of a new project
project_nutzer = []
#List of funders of the new project
project_funding = []

@app.route("/NewProject")
def NewProject():
    #rendering the NewProject page with project_nutzer and project_funding as parameters    
    return render_template("NewProjectUI.html", nutzer=project_nutzer, funder=project_funding)

#function to add a new Member to a newProject
@app.route("/NewProject/nutzer_hinzufuegen", methods=['POST'])
def nutzer_hinzufuegen():
    #request from the html where forms have the name name. Because this is an input the typed name of the new member is selected.
    name = request.form['name']
    #the new Member is appended to the project_nutzer list
    project_nutzer.append(name)
    #with redirect(url_for) we directly get back to the NewProject page
    return redirect(url_for("NewProject"))

@app.route("/NewProject/funding_hinzufuegen", methods=['POST'])
def funding_hinzufuegen():
    #request from the html where forms have the name name. Because this is an input the typed name of the new funder is selected
    name = request.form['name']
    #the new funder is added to the project_funder list
    project_funding.append(name)
    #redirect to the NewProject page
    return redirect(url_for("NewProject"))


if __name__ == "__main__":
    app.run(debug=True)