from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import jsonify
import sqlite3
import uuid
import database

app = Flask(__name__)


@app.route("/dashboard")
def dashboard():

    # Erstellt eine Liste von Projektdaten für 19 Projekte mit formatierten Details
    projects = []

    for i in range(1, 20):
        if i < 10:
            i = "0" + str(i)

        new_project = [
            "name" + str(i),
            "open",
            "writer",
            "namen + " + str(i) + " member",
            str(i) + ".06.2024",
        ]
        projects.append(new_project)

    return render_template("dashboard.html", text_for_column=projects)


# Dictionary which safes the information for the new project
new_project_info = dict(
    project_name="", project_description="", project_member=[], project_funder=[]
)


@app.route("/NewProject")
def new_project():
    # rendering the NewProject page with project_user and project_funding as parameters
    return render_template(
        "NewProjectUI.html",
        name_value=new_project_info["project_name"],
        description_value=new_project_info["project_description"],
        user=new_project_info["project_member"],
        funder=new_project_info["project_funder"],
    )


# function to add a new Member to a newProject
@app.route("/NewProject/add_user", methods=["POST"])
def add_user():
    # request from the html where forms have the name name. Because this is an input the typed name of the new member is selected.
    user = request.form["name"]
    # the new Member is appended to the project_user list
    new_project_info["project_member"].append(user)
    # with redirect(url_for) we directly get back to the NewProject page
    return redirect(url_for("new_project"))


# Function to save the projectname and the project description
@app.route("/NewProject/save_data", methods=["POST"])
def save_data():
    # request the json data which contains the projectname and the projectdescription
    data = request.json
    # set variables to save the project_name and the project_description
    project_name = data.get("project_name")
    project_description = data.get("project_description")

    # if Project_name data or project_description data were correctly transfered save the data in the dictionary
    if project_name or project_description:
        new_project_info["project_name"] = project_name
        new_project_info["project_description"] = project_description
        # return successmessage
        return (
            jsonify(
                {
                    "message": "Project data saved successfully",
                    "projects": new_project_info,
                }
            ),
            200,
        )
    # if data was not transfered correctly
    else:
        # return error message
        return jsonify({"message": "Invalid data"}), 400


@app.route("/NewProject/add_funding", methods=["POST"])
def add_funding():
    # request from the html where forms have the name name. Because this is an input the typed name of the new funder is selected
    funder = request.form["name"]
    # the new funder is added to the project_funder list
    new_project_info["project_funder"].append(funder)
    # redirect to the NewProject page
    return redirect(url_for("new_project"))


# Nach dem Entwurf eines Projekts werden die Daten in der Datenbank gespeichert
@app.route("/NewProject/create_project")
def create_project():

    # Objekt der Datenbank erzeugen und connecten
    db = database.Database()
    nid = db.get_id()
    conn = db.create_connection(db.project_db)

    project_table = """CREATE TABLE IF NOT EXISTS PROJECT (
                      PID VARCHAR(40) PRIMARY KEY,
                      NAME VARCHAR(30) NOT NULL,
                      DESCRIPTION TEXT NOT NULL,
                      ADMIN VARCHAR(40) NOT NULL,
                      FUNDER TEXT
                ); """

    user_table = f"""
                CREATE TABLE IF NOT EXISTS {nid} (
                      PID VARCHAR(40) NOT NULL,
                      ROLE VARCHAR(5) NOT NULL,
                      FOREIGN KEY (PID) REFERENCES PROJECT(PID)
                );
            """

    # User Tabelle erstellen
    db.create_table(conn, user_table)

    # PID erstellen
    pid = str(uuid.uuid4())

    # Die NID des Admins vom Projekt
    user_admin = nid

    # Tupel erstellen
    user_values = (pid, "admin")

    # Tupel in Tabelle einfügen
    db.insert_user(conn, user_values)

    # Drucke User Tabelle
    print_table(conn, nid)

    # die benötigten Daten aus dem Dictionary holen
    project_name = new_project_info["project_name"]
    project_description = new_project_info["project_description"]
    project_funder = new_project_info["project_funder"]
    project_funder_str = ",".join(project_funder)

    # Projekt Tabelle erstellen
    db.create_table(conn, project_table)

    # Tupel erstellen
    project_values = (
        pid,
        project_name,
        project_description,
        user_admin,
        project_funder_str,
    )

    # Tupel in Projekt Tabelle einfügen
    db.insert_project(conn, project_values)

    # Plan: Die PID zu den einzelnen Member Tabellen einfügen
    for member in new_project_info["project_member"]:
        member_id = db.get_from_name_id(conn, member)
        db.add_values_to_member(conn, member_id, (pid, "read"))

    # drucke PROJKET Tabelle
    print_table(conn, "PROJECT")

    # Das Dictonary nach dem eingeben wieder leeren
    new_project_info["project_name"] = ""
    new_project_info["project_description"] = ""
    new_project_info["project_funder"] = []
    new_project_info["project_member"] = []

    return redirect(url_for("dashboard"))


# Druckt die Tabelle
def print_table(conn, table_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()
        print(f"Data from {table_name}:")
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Error reading from table {table_name}: {e}")



if __name__ == "__main__":
    app.run(debug=True)
