from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import jsonify
import sqlite3
<<<<<<< HEAD
import hashlib
=======
>>>>>>> remotes/origin/project_db
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
    project_name="", project_description="", project_member=[], project_funder=[]
)


@app.route("/NewProject")
def new_project():
    # rendering the NewProject page with project_nutzer and project_funding as parameters
    return render_template(
        "NewProjectUI.html",
        name_value=new_project_info["project_name"],
        description_value=new_project_info["project_description"],
        nutzer=new_project_info["project_member"],
        funder=new_project_info["project_funder"],
    )


# function to add a new Member to a newProject
@app.route("/NewProject/nutzer_hinzufuegen", methods=["POST"])
def nutzer_hinzufuegen():
    # request from the html where forms have the name name. Because this is an input the typed name of the new member is selected.
    nutzer = request.form["name"]
    # the new Member is appended to the project_nutzer list
    new_project_info["project_member"].append(nutzer)
    # with redirect(url_for) we directly get back to the NewProject page
    return redirect(url_for("new_project"))


# Function to save the projectname and the project description
@app.route("/NewProject/saveData", methods=["POST"])
def saveData():
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


@app.route("/NewProject/funding_hinzufuegen", methods=["POST"])
def funding_hinzufuegen():
    # request from the html where forms have the name name. Because this is an input the typed name of the new funder is selected
    funder = request.form["name"]
    # the new funder is added to the project_funder list
    new_project_info["project_funder"].append(funder)
    # redirect to the NewProject page
    return redirect(url_for("new_project"))


class Database:
    def __init__(self):
        self.id = None
        self.p_db_name = "project.db"
        self.l_db_name = "sign_in_up_user_data.db"
        self.l_allUser_db = "all_users.db"

<<<<<<< HEAD
    def create_connection(self, name):

        # Erstellen einer Datenbankverbindung zu einer SQLite-Datenbank
        l_conn = None
        try:
            l_conn = sqlite3.connect(name)
            return l_conn
        except sqlite3.Error as e:
            print(e)
        return l_conn

    def hash_password(self, password):

        # Hashen eines Passworts
        # passwort wird mit encode() als Byte-Sequenz angegeben und dann gehasht
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()

    def generate_user_id(self):
        """Generiere zufällige user_id"""
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

   
    def l_register_user(self, conn, username, mail, password):

        # Hinzufügen eines neuen Benutzers zur Tabelle 'l_nutzerdaten
        password_hash = self.hash_password(password)
        user_id = self.generate_user_id()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO l_nutzerdaten (nutzer_id, nutzername, mail, passwort_hash) VALUES (?, ?, ?, ?)",
                (user_id, username, mail, password_hash),
            )
            conn.commit()
            
            self.l_add_user_to_all_users(username,user_id)
            
            print(f"User added successfully with ID {user_id}.")
            
        except sqlite3.IntegrityError:
            print("Username or email already exists.")
        except sqlite3.Error as e:
            print(e)

    def l_add_user_to_all_users(self,username, user_id):
        conn = self.create_connection(self.l_allUser_db)
        
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO all_users (user_id, username) VALUES (?, ?)",
                (user_id, username),
            )
        conn.commit()
        
        print(f"User {username} was added")
        
    
    
    def get_from_name_id(self,conn,username):
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
    
    def l_login_user(self, conn, username, password):

        # Einloggen eines Benutzers
        password_hash = self.hash_password(password)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nutzer_id, passwort_hash FROM l_nutzerdaten WHERE nutzername = ?",
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
        conn = db.create_connection(self.l_db_name)
        conn_all_users = db.create_connection(self.l_allUser_db)

        user_table = """
                CREATE TABLE IF NOT EXISTS l_nutzerdaten (
                    nutzer_id TEXT PRIMARY KEY,
                    nutzername VARCHAR UNIQUE NOT NULL,
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
        #db.l_register_user(conn, "testuser13", "test5@example.com", "password13")

        # Logge den Benutzer ein
        #db.l_login_user(conn, "testuser13", "password13")

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


# Teste die Funktionalitäten der Database-Klasse visuell
=======
@app.route("/NewProject/create_project")
def create_project():
    # platzhalter
    nid = "abs12345"

    # Objekt der Datenbank erzeugen und connecten
    db = Database(nid)

    conn = db.p_create_connection()

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
    u_values = (pid, 'admin')      
    # Tupel in Tabelle einfügen                     
    db.p_insert_user(conn, u_values)  


    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM \"{nid}\"")

    # Spaltennamen abrufen
    column_names = [description[0] for description in cursor.description]
    print(" | ".join(column_names))

    # Zeilen abrufen und drucken
    rows = cursor.fetchall()
    for row in rows:
        print(" | ".join(map(str, row)))


    project_name = new_project_info['project_name']
    project_description = new_project_info['project_description']
    project_funder = new_project_info['project_funder']
    project_funder_str = ','.join(project_funder)
    
    # Projekt Tabelle erstellen
    db.create_table(conn, project_table)       
    # Tupel erstellen
    
    p_values = (pid, project_name, project_description, 
                user_admin, project_funder_str)
    # Tupel in Projekt Tabelle einfügen
    
    db.p_insert_project(conn, p_values)   

                        
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM PROJECT")

    # Spaltennamen abrufen
    column_names = [description[0] for description in cursor.description]
    print(" | ".join(column_names))

    # Zeilen abrufen und drucken
    rows = cursor.fetchall()
    for row in rows:
        print(" | ".join(map(str, row)))

    
    new_project_info["project_name"] = ""
    new_project_info["project_description"] = ""
    new_project_info["project_funder"] = []
    new_project_info["project_member"] = []


    """
    # Plan: Die PID zu den einzelnen Member Tabellen einfügen, aber wie?
    for member in request.form.getlist('project_members'):          # Besprechen!!!
        db.p_insert_user(conn, member, pid, 'read')
    """



    return redirect(url_for("dashboard"))






class Database:
    # Konstruktor mit der ID des Nutzers
    def __init__(self, nid):
        self.id = nid
        self.p_db_name = 'project.db'
        self.l_db_name = "nutzerdaten.db"


    # Funktion zur Verbindung mit der Datenbank herstellen
    def p_create_connection(self):
        """Erstellen einer Datenbankverbindung zu einer SQLite-Datenbank"""
        p_conn = None
        try:
            p_conn = sqlite3.connect(self.p_db_name)
            return p_conn
        # Diese Zeilen fangen Fehler ab
        except sqlite3.Error as e:                   
            print(e)
        return p_conn


    # Datenbank Tabelle für Projekte erstellen
    def create_table(self, p_conn, sqlcode):
        try:
            c = p_conn.cursor()
            c.execute(sqlcode)
            p_conn.commit()
        except sqlite3.Error as e:
            print(e)


    # Tupel in die Nutzer Tabelle einfügen
    def p_insert_user(self, p_conn, tupel):
        """Values werden in die User Tabelle eingefügt"""
        try:
            # Values(?,?) sind Platzhalter die vom Tupel ersetzt werden
            sql = f''' INSERT INTO {self.id}(PID, ROLE)
                    VALUES(?,?) '''                         
            cur = p_conn.cursor()
            cur.execute(sql, tupel)
            p_conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            print(e)



    # Tupel in die Projekt Tabelle einfügen
    def p_insert_project(self, p_conn, p_tupel):
        """Values werden in die Projekt Tabelle eingefügt"""
        try:
            sql = f''' INSERT INTO PROJECT(PID, NAME, DESCRIPTION, ADMIN, FUNDER)
                    VALUES(?,?,?,?,?) '''
            cur = p_conn.cursor()
            cur.execute(sql, p_tupel)
            p_conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            print(e)



>>>>>>> remotes/origin/project_db
if __name__ == "__main__":
    db = Database()
    db.test()
