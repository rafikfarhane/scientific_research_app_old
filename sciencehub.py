from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import jsonify
import sqlite3
import hashlib
import uuid

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
    project_name = "", project_description = "", project_member = [], project_funder = []
)


@app.route("/NewProject")
def new_project():
    # rendering the NewProject page with project_user and project_funding as parameters
    return render_template(
        "NewProjectUI.html",
        name_value = new_project_info["project_name"],
        description_value = new_project_info["project_description"],
        user = new_project_info["project_member"],
        funder = new_project_info["project_funder"],
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
    db = Database()
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
    project_values = (pid, project_name, project_description, 
                user_admin, project_funder_str)
    
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
        cursor.execute(f"SELECT * FROM \"{table_name}\"")
        rows = cursor.fetchall()
        print(f"Data from {table_name}:")
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Error reading from table {table_name}: {e}")



######################################################################################################################################################



class Database:
    def __init__(self):
        self.id = None
        self.project_db = "project.db"
        self.login_db = "sign_in_user_data.db"
        self.all_users_db = "all_users.db"



    def create_connection(self, name):
        # Erstellen einer Datenbankverbindung zu einer SQLite-Datenbank
        conn = None
        try:
            conn = sqlite3.connect(name)
            return conn
        except sqlite3.Error as e:
            print(e)
        return conn



    def hash_password(self, password):
        # Hashen eines Passworts
        # passwort wird mit encode() als Byte-Sequenz angegeben und dann gehasht
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()



    def generate_user_id(self):
        # Generiere zufällige user_id
        return str(uuid.uuid4())



    def get_id(self):
        return self.id



    def set_id(self, new_id):
        self.id = new_id



    def create_table(self, conn, sqlcode):
        try:
            cursor = conn.cursor()
            cursor.execute(sqlcode)
            conn.commit()
            print("Created table")
        except sqlite3.Error as e:
            print(e)

   

    def register_user(self, conn, username, mail, password):
        # Hinzufügen eines neuen Benutzers zur Tabelle "user_data
        password_hash = self.hash_password(password)
        user_id = self.generate_user_id()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_data (user_id, username, mail, passwort_hash) VALUES (?, ?, ?, ?)",
                (user_id, username, mail, password_hash),
            )
            conn.commit()
            self.add_user_to_all_users(username,user_id)
            print(f"User added successfully with ID {user_id}.")
        except sqlite3.IntegrityError:
            print("Username or email already exists.")
        except sqlite3.Error as e:
            print(e)



    def add_user_to_all_users(self,username, user_id):
        conn = self.create_connection(self.all_users_db)

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO all_users (user_id, username) VALUES (?, ?)",
            (user_id, username),
        )
        conn.commit()

        print(f"User {username} was added")



    def get_from_name_id(self, conn, username):
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM all_users WHERE username = ?",
                (username,),
            )
            # fetcone -> geht auf die erste Zeile (einzige Zeile)
            row = cursor.fetchone()
            if row is not None:
                # Tupel entpacken
                db_user_id = row
                print("Login successful.")
                return db_user_id
            else:
                print("User not found.")

        except sqlite3.Error as e:
            print(e)
    


    def login_user(self, conn, username, password):
        # Einloggen eines Benutzers
        password_hash = self.hash_password(password)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, passwort_hash FROM user_data WHERE username = ?",
                (username,),
            )
            # fetcone -> geht auf die erste Zeile (einzige Zeile)
            row = cursor.fetchone()
            if row is not None:
                # Tupel entpacken
                db_user_id, db_password_hash = row
                if db_password_hash == password_hash:
                    # Setze self.id auf die ID des eingeloggten Benutzers
                    self.id = db_user_id
                    print("Login successful.")
                else:
                    print("Incorrect password.")
            else:
                print("User not found.")
        except sqlite3.Error as e:
            print(e)



    def test(self):
        # Erstelle eine Instanz der Database-Klasse
        db = Database()

        # Öffne eine Verbindung zur Datenbank
        conn = db.create_connection(self.login_db)
        conn_all_users = db.create_connection(self.all_users_db)

        user_table = """
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id TEXT PRIMARY KEY,
                    username VARCHAR UNIQUE NOT NULL,
                    mail TEXT VARCHAR NOT NULL,
                    passwort_hash TEXT NOT NULL
                )"""
        # Erstelle die Nutzertabelle
        db.create_table(conn, user_table)

        all_users_table = """CREATE TABLE IF NOT EXISTS all_users (
                    user_id TEXT PRIMARY KEY,
                    username VARCHAR UNIQUE NOT NULL
                )"""
        # Erstelle all nutzertabelle
        db.create_table(conn_all_users, all_users_table)

        # Registriere einen neuen Benutzer
        # db.register_user(conn, "testuser13", "test5@example.com", "password13")

        # Logge den Benutzer ein
        # db.login_user(conn, "testuser13", "password13")

        # Gib die UserID des eingeloggten Benutzers aus
        print("User ID:", db.get_id())

        # Teste get_from_name_id Methode
        user_id = db.get_from_name_id(conn_all_users, "testuser12")
        print("Returned User ID from get_from_name_id:", user_id)

        cursor = conn_all_users.cursor()
        cursor.execute(f"SELECT * FROM all_users")

        # Spaltennamen abrufen
        column_names = [description[0] for description in cursor.description]
        print(" | ".join(column_names))

        # Zeilen abrufen und drucken
        rows = cursor.fetchall()
        for row in rows:
            print(" | ".join(map(str, row)))

        # Schließe die Verbindung zur Datenbank
        conn.close()
        conn_all_users.close()



    def insert_user(self, conn, tupel):
        # Values werden in die User Tabelle eingefügt
        try:
            # Values(?,?) sind Platzhalter die vom Tupel ersetzt werden
            sql = f''' INSERT INTO {self.id}(PID, ROLE)
                    VALUES(?,?) '''                         
            cur = conn.cursor()
            cur.execute(sql, tupel)
            conn.commit()

            # Rückgabe der ID der zuletzt eingefügten Zeile, nützlich für 
            # Referenzzwecke in nachfolgenden Operationen
            return cur.lastrowid
        
        except sqlite3.Error as e:
            print(e)



    def insert_project(self, conn, tupel):
        # Values werden in die Projekt Tabelle eingefügt
        try:
            sql = f''' INSERT INTO PROJECT(PID, NAME, DESCRIPTION, ADMIN, FUNDER)
                    VALUES(?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, tupel)
            conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            print(e)


        
    def add_values_to_member(self, conn, nid, tupel):
        # Values werden in die Tabelle eines anderen Users eingefügt
        try:
            sql = f''' INSERT INTO {nid}(PID, ROLE)
                    VALUES(?,?) '''                         
            cur = conn.cursor()
            cur.execute(sql, tupel)
            conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            print(e)



if __name__ == "__main__":
    app.run(debug=True)
    #db = Database()
    #db.test()