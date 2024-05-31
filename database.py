import sqlite3
import hashlib
import uuid



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
