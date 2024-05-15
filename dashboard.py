from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/dashboard")
def home():
    # Erstellt eine Liste von Projektdaten für 19 Projekte mit formatierten Details
    
    projects = []
    
    for i in range (1,20):
        if (i < 10):
            i = "0" + str(i)
        
        newProject = [ "name" + str(i), "open", "writer", "namen + " +  str(i) + " member", str(i) + ".06.2024"]
        projects.append(newProject)
        
    return render_template('dashboard.html', textForColumn=projects)


if __name__ == "__main__":
    app.run(debug=True)