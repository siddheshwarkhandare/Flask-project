from flask import Flask,render_template,request,redirect
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

@app.route('/', methods = ['GET','POST'])
def home():
    if request.method=='POST':
        titl=request.form['title']
        des = request.form['desc']
        firstin = todo(title=titl,desc=des)
        db.session.add(firstin)
        db.session.commit()


    alltodoes=todo.query.all()
    return render_template('index.html',alltodoes=alltodoes)


@app.route("/delete/<int:sno>")
def delete(sno):
    do=todo.query.filter_by(sno=sno).first()
    db.session.delete(do)
    db.session.commit()

    return redirect('/')

@app.route("/see")
def update():
    alltodoes=todo.query.all()







# This MUST be at the very bottom, without an 'if' block for now
with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True, port=5001)