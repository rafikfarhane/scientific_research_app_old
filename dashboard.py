from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/dashboard")
def home():
    first = ["Name1", "Open", "Writer", "Lücke + 9 Members", "24.05.2024"]
    second = ["Name2", "Open", "Writer", "Neuer + 3 Members", "27.05.2024"]
    third = ["Name4", "Closed", "Writer", "Vini + 5 Members", "29.05.2024"]
    projects = [first,second,third]
    return render_template('test.html', textForColumn=projects)


if __name__ == "__main__":
    app.run(debug=True)