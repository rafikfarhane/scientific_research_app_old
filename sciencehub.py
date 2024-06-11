from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import jsonify
from flask import flash
from datetime import date, datetime
import sqlite3
import hashlib
import uuid
import database

app = Flask(__name__)

# Flash key
app.secret_key = "your_secret_key"

db = database.Database()

# Dictionary which safes the information for the new project
new_project_info = dict(
    project_name="", project_description="", project_member=[], project_funder=[]
)


def create_dbs():
    # Öffne eine Verbindung zur Datenbank
    conn_user_data = db.create_connection(db.login_db)
    conn_all_users = db.create_connection(db.all_users_db)
    conn_project = db.create_connection(db.project_db)

    user_table = """
            CREATE TABLE IF NOT EXISTS user_data (
                user_id TEXT PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL,
                mail TEXT VARCHAR NOT NULL,
                passwort_hash TEXT NOT NULL
            )"""

    # Erstelle die Nutzertabelle mit allen Nutzern fürs login & registrieren
    db.create_table(conn_user_data, user_table)

    all_users_table = """CREATE TABLE IF NOT EXISTS all_users (
                user_id TEXT PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL
            )"""

    # Erstelle eine Nutzertabell mit allen Nutzern, um auf id & username zuzugreifen
    db.create_table(conn_all_users, all_users_table)

    project_table = """CREATE TABLE IF NOT EXISTS PROJECT (
                      PID VARCHAR(40) PRIMARY KEY,
                      NAME VARCHAR(30) NOT NULL,
                      DESCRIPTION TEXT NOT NULL,
                      ADMIN VARCHAR(40) NOT NULL,
                      FUNDER TEXT,
                      MEMBERS TEXT,
                      STATUS VARCHAR(7) NOT NULL,
                      CREATED_DATE NOT NULL
                ); """

    # Erstelle ein Projekttabelle für alle Projekte
    db.create_table(conn_project, project_table)


#Funktion um das new_project_info dict zu leeren
def empty_dict():
    new_project_info["project_name"] = ""
    new_project_info["project_description"] = ""
    new_project_info["project_funder"] = []
    new_project_info["project_member"] = []


#Funktion welche zu einem String die user zurueckgibt deren username mit diesem String beginnt
def search_for_users(query) -> dict:

    #Verbindung zur all_users databass erstellen
    conn = db.create_connection(db.all_users_db)
    cursor = conn.cursor()
    #Nutzer aus der Database abfragen, die mit dem selben String beginnen welcher eingegeben wurde 
    cursor.execute('SELECT username FROM all_users WHERE username LIKE ?', (query + '%',))
    users = cursor.fetchall()
    conn.close()
    #usernames zurueck an die html datei senden 
    user_list = [{'username': user[0]} for user in users]
    return user_list



@app.route("/")
def starting_page():
    return redirect("login")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login/check", methods=["POST"])
def check_login():
    # username vom input Field bekommen
    username = request.form["username"]

    # password vom input Field bekommen
    password = request.form["password"]

    # conection zur login Datenbank
    login_conn = db.create_connection(db.login_db)

    # wenn Passwort & Nutzername inkorrekt
    if db.login_user(login_conn, username, password) == False:
        flash("Username or password is wrong")
        return redirect(url_for("login"))

    else:
        # id des nutzer aus der DB anfragen
        cursor = login_conn.cursor()
        id = cursor.execute(
            "SELECT user_id FROM user_data WHERE username = ?",
            (username,),
        )

        # id aus der Anfrage ziehen
        row = cursor.fetchone()
        if row is not None:
            # Tupel entpacken
            id = row[0]

        # id auf den eingelogten Nutzer setzten
        db.set_id(id)

        return redirect(url_for("dashboard", username=username))


@app.route("/sign_up")
def sign_up():
    return render_template("register.html")


@app.route("/sign_up/complete_sign_up", methods=["POST"])
def complete_sign_up():
    name = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    repeat_password = request.form["repeat_password"]

    if password != repeat_password:
        flash("The passwords are not identical!")
        return redirect(url_for("sign_up"))

    else:
        conn = db.create_connection(db.login_db)

        if db.search_user(name, email) == True:
            register = db.register_user(conn, name, email, password)

            if register == False:
                flash("ERROR something went wrong")
                return redirect(url_for("sign_up"))

            cursor = conn.cursor()
            id = cursor.execute(
                "SELECT user_id FROM user_data WHERE username = ?",
                (name,),
            )

            row = cursor.fetchone()
            if row is not None:
                id = str(row[0])

            db.set_id(id)

            user_table = f"""
            CREATE TABLE IF NOT EXISTS {id} (
                    PID VARCHAR(40) NOT NULL,
                    ROLE VARCHAR(5) NOT NULL,
                    FOREIGN KEY (PID) REFERENCES PROJECT(PID)
                );
            """
            user_conn = db.create_connection(db.project_db)
            db.create_table(user_conn, user_table)

            return redirect(url_for("dashboard", username=name))
        else:
            flash("Username or E-Mail already exists")
            return redirect(url_for("sign_up"))


@app.route("/dashboard/<username>")
def dashboard(username):

    # wenn der übergebene Nutzer nicht mit dem angemeldeten Nutzer übereinstimmt, zurück zu login
    if db.get_id() != db.get_id_from_name(username):
        return redirect(url_for("login"))
    
    conn = db.create_connection(db.project_db)
    cursor = conn.cursor()

    # Die ID des Benutzers basierend auf dem Benutzernamen abrufen
    user_id = db.get_id_from_name(username)

    # Führen Sie die Abfrage aus, um alle Projekte des Benutzers zu erhalten
    cursor.execute(
        f"""SELECT P.NAME, P.STATUS, B.ROLE, P.ADMIN, P.MEMBERS, P.CREATED_DATE
        FROM {user_id} AS B JOIN PROJECT AS P ON B.PID = P.PID"""
    )

    # Holt alle Ergebnisse
    results = cursor.fetchall()

    # Erstellt eine Liste von Projektdaten für alle Projekte des Nutzers
    projects = []
    if results:
        for result in results:
            project_name, status, role, creator, members, date_str = result
            try:
                # Versuche, den Datum-String in ein Datum-Objekt umzuwandeln
                date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
            except ValueError:
                # Falls das Umwandeln fehlschlägt, setze date auf None oder eine Standardmeldung
                date = date.today()
                print("No date found")

            if members:
                members_count = len(members.split(','))
            else:
                members_count = 0

            values = [
                project_name,
                status,
                role,
                db.get_name_from_id(creator) + " + " + str(members_count) + " more members",
                # Datum zum dd.mm.yyyy Format umändern
                date.strftime('%d.%m.%Y') if date else "No Date"
            ]
            projects.append(values)
    else:
        flash("No projects found for this user")

    return render_template("dashboard.html", text_for_column=projects)


#log out aus aus seinem Account
@app.route("/log_out")
def log_out():
    #id wird auf none gesetzt somit ist man abgemeldet
    db.set_id(None)
    #zurueckleiten auf start seite
    return redirect(url_for("starting_page"))


# Add a project
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


@app.route('/NewProject/search_users', methods=['GET'])
def search_users():

    #Erhalt der Eingegeben Buchstaben aus dem Inputfeld
    query = request.args.get('q', '')
    #Rufe Funktion auf welche nach den entsprechenden usern sucht
    user_list = search_for_users(query)
    return jsonify(user_list)


#zurueck zum dashboard wenn man doch kein neues projekt erstellen will
@app.route("/NewProject/back_to_dashboard")
def back_to_dashboard():
    
    #hole die aktuelle id des nutzers
    id = db.get_id()
    #hole den dazu entsprechenden nutzername aus der datenbank
    name = db.get_name_from_id(id)
    #new_project_info dict leeren
    empty_dict()
    #leite zurueck auf die nutzer dashboard seite
    return redirect(url_for("dashboard", username = name))


# Function to add a new Member to a newProject
@app.route("/NewProject/add_user", methods=["POST"])
def add_user():
    # request from the html where forms have the name name. Because this is an input the typed name of the new member is selected.
    user = request.form["name"]
    #test ob user ueberhaupt existiert
    if db.user_exists(user) == True:
        if user not in new_project_info["project_member"]:
            # the new Member is appended to the project_user list
            new_project_info["project_member"].append(user)
        else:
            flash("This User is already part of your project")
    else:
        flash("This User does not exist")
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

    id = db.get_id()
    conn = db.create_connection(db.project_db)

    # PID erstellen
    pid = "p" + str(uuid.uuid4())

    # Die NID des Admins vom Projekt
    user_admin = id

    # Tupel erstellen
    user_values = (pid, "admin")

    # Tupel in Tabelle einfügen
    db.add_values_to_member(conn, id, user_values)

    # die benötigten Daten aus dem Dictionary holen
    project_name = new_project_info["project_name"]
    project_description = new_project_info["project_description"]
    project_members = new_project_info["project_member"]
    project_members_str = ",".join(project_members)
    project_funder = new_project_info["project_funder"]
    project_funder_str = ",".join(project_funder)

    # Tupel erstellen
    project_values = (
        pid,
        project_name,
        project_description,
        user_admin,
        project_funder_str,
        project_members_str,
        "open",
        date.today(),
    )

    # Tupel in Projekt Tabelle einfügen
    db.add_project(conn, project_values)

    # Plan: Die PID zu den einzelnen Member Tabellen einfügen
    for member in new_project_info["project_member"]:
        member_id = db.get_id_from_name(member)
        db.add_values_to_member(conn, member_id, (pid, "read"))

    # Das Dictonary nach dem eingeben wieder leeren

    empty_dict()
    name = db.get_name_from_id(id)

    return redirect(url_for("dashboard", username=name))


if __name__ == "__main__":
    create_dbs()
    app.run(debug=True)
