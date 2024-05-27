from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import jsonify
import sqlite3

app = Flask(__name__)

@app.route("/dashboard")

def dashboard():
    
    # Erstellt eine Liste von Projektdaten für 19 Projekte mit formatierten Details
    projects = []
    
    for i in range (1,20):
        if (i < 10):
            i = "0" + str(i)
        
        new_project = [ "name" + str(i), "open", "writer", "namen + " +  str(i) + " member", str(i) + ".06.2024"]
        projects.append(new_project)
        
    return render_template('dashboard.html', text_for_column=projects)



#Dictionary which safes the information for the new project
new_project_info = dict(project_name = "",
                        project_description = "",
                        project_member = [],
                        project_funder = []
                        )

@app.route("/NewProject")
def new_project():
    #rendering the NewProject page with project_nutzer and project_funding as parameters    
    return render_template("NewProjectUI.html", name_value = new_project_info["project_name"], description_value = new_project_info["project_description"], nutzer=new_project_info["project_member"], funder=new_project_info["project_funder"])

#function to add a new Member to a newProject
@app.route("/NewProject/nutzer_hinzufuegen", methods=['POST'])
def nutzer_hinzufuegen():
    #request from the html where forms have the name name. Because this is an input the typed name of the new member is selected.
    nutzer = request.form['name']
    #the new Member is appended to the project_nutzer list
    new_project_info["project_member"].append(nutzer)
    #with redirect(url_for) we directly get back to the NewProject page
    return redirect(url_for("new_project"))


#Function to save the projectname and the project description
@app.route("/NewProject/saveData", methods = ['POST'])
def saveData():
    #request the json data which contains the projectname and the projectdescription
    data = request.json
    #set variables to save the project_name and the project_description
    project_name = data.get('project_name')
    project_description = data.get('project_description')

    #if Project_name data or project_description data were correctly transfered save the data in the dictionary
    if project_name or project_description:
        new_project_info["project_name"] = project_name
        new_project_info["project_description"] = project_description
        #return successmessage
        return jsonify({"message": "Project data saved successfully", "projects": new_project_info}), 200
    #if data was not transfered correctly 
    else:
        #return error message
        return jsonify({"message": "Invalid data"}), 400

@app.route("/NewProject/funding_hinzufuegen", methods=['POST'])
def funding_hinzufuegen():
    #request from the html where forms have the name name. Because this is an input the typed name of the new funder is selected
    funder = request.form['name']
    #the new funder is added to the project_funder list
    new_project_info["project_funder"].append(funder)
    #redirect to the NewProject page
    return redirect(url_for("new_project"))



if __name__ == "__main__":
    app.run(debug=True)