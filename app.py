from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)

class todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False) 
    desc =  db.Column(db.String(500), nullable=False)
    date_created =  db.Column(db.DateTime,default= datetime.utcnow)

    def __repr__(self):
        return f"{self.sno},{self.title}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/about")
def about_page():
    return "this is about page"

# This MUST be at the very bottom, without an 'if' block for now
app.run(debug=True, port=5001)