from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/dashboard")
def home():
    
    projects = []
    
    for i in range (1,20):
        if (i < 10):
            i = "0" + str(i)
        
        newProject = [ "Name" + str(i), "Open", "Writer", "Namen + " +  str(i) + " Member", str(i) + ".06.2024"]
        projects.append(newProject)
        
    return render_template('test.html', textForColumn=projects)


if __name__ == "__main__":
    app.run(debug=True)