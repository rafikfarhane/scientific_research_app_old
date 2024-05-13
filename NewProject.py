from flask import Flask, render_template


app = Flask(__name__)

@app.route("/NewProject")
def NewProject():
    return render_template("NewProjectUI.html")

if __name__ == "__main__":
    app.run(debug=True)