from flask import Flask,flash,render_template,request,redirect,url_for
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone, timedelta
import os
import json
from dotenv import load_dotenv
from google import genai 


load_dotenv()
client = genai.Client(
    api_key=os.getenv("voice_api")
)

IST = timezone(timedelta(hours=5, minutes=30))


app = Flask(__name__)
app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
csrf = CSRFProtect(app)
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
login_manager= LoginManager(app)
login_manager.login_view='login'


db = SQLAlchemy(app)
migrate=Migrate(app,db)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True, nullable=False)
    hash_password=db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(150),unique=True,nullable=False)

    def hash_generate(self,password):
        self.hash_password=generate_password_hash(password)

    def hash_check(self, password):
        return check_password_hash(self.hash_password,password)
class todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False) 
    desc =  db.Column(db.String(500), nullable=False)
    date_created = db.Column(
        db.DateTime,
        default=lambda: datetime.now(IST)
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"{self.sno},{self.title}"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password = request.form['password']
        user=User.query.filter_by(username=username).first()

        if user and user.hash_check(password):
            login_user(user)
            return redirect('/')
        else:
            flash('invalide username/password')
    return render_template('/user/login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()  
    return redirect(url_for('home'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        email = request.form['email']
        password=request.form['password']
        conpassword=request.form['confirm_password']

        if password!= conpassword:
            flash("Password not  match")
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash("Username already exist")
            return redirect(url_for('/register'))
        
        if  User.query.filter_by(email=email).first():
            flash("Email already exist")
            return redirect(url_for('/register'))

        
        user=User(
            username=username,
            email=email,
        )
        user.hash_generate(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')

    return render_template('/user/register.html')

@app.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user:
            token = serializer.dumps(user.username, salt='password-reset')
            reset_url = url_for('reset_password', token=token, _external=True)
            # For now, just show the link (later replace with email sending)
            flash(f'Reset link (demo only): {reset_url}')
        else:
            flash('No account found with that username')

        return redirect(url_for('forgot_password'))

    
    return render_template('/user/forgot_pass.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("You need to login to add a todo.")
            return redirect(url_for('login'))

        titl = request.form['title']
        des = request.form['desc']
        firstin = todo(title=titl, desc=des, user_id=current_user.id)
        db.session.add(firstin)
        db.session.commit()
        return redirect('/')

    # show the logged-in user's todos, or nothing if not logged in
    if current_user.is_authenticated:
        alltodoes = todo.query.filter_by(user_id=current_user.id).all()
    else:
        alltodoes = []

    return render_template('index.html', alltodoes=alltodoes)


@app.route("/delete/<int:sno>")
@login_required
def delete(sno):
    do=todo.query.filter_by(sno=sno).first()
    db.session.delete(do)
    db.session.commit()

    return redirect('/')

@app.route("/update/<int:sno>",methods = ['GET','POST'])

def update(sno):
    do=todo.query.filter_by(sno=sno).first()

    if request.method=='POST':
        do.title=request.form['title']
        do.desc=request.form['desc']

        db.session.commit() 
        return redirect("/")       

    return render_template('update.html',todo=do)

@app.route("/cancel")
def cancel():
    return redirect('/update/')


@app.route("/voice", methods=["POST"])
@login_required
def voice():

    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return {"error": "No voice text received"}, 400

    print("Voice command:", text)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""
You are a Todo assistant.

Understand the user's command.

User command:
{text}

Return ONLY valid JSON.

For creating a task:
{{
    "action": "create",
    "title": "task title",
    "description": "task description"
}}

For deleting:
{{
    "action": "delete",
    "title": "task title"
}}

For updating:
{{
    "action": "update",
    "old_title": "old task title",
    "title": "new task title",
    "description": "new description"
}}

For listing:
{{
    "action": "list"
}}
"""
    )

    ai_text = response.text.strip()

    print("Gemini:", ai_text)

    # Remove markdown ```json if Gemini adds it
    ai_text = ai_text.replace("```json", "").replace("```", "").strip()

    try:
        command = json.loads(ai_text)
    except json.JSONDecodeError:
        return {
            "error": "Gemini returned invalid JSON",
            "gemini": ai_text
        }, 500

    action = command.get("action")

    # CREATE
    if action == "create":

        title = command.get("title")
        description = command.get("description", "")

        if not title:
            return {"error": "No title provided"}, 400

        new_todo = todo(
            title=title,
            desc=description
        )

        db.session.add(new_todo)
        db.session.commit()

        print("Created:", title)

        return {
            "success": True,
            "action": "create",
            "title": title,
            "description": description
        }

    return {
        "success": True,
        "action": action,
        "command": command
    }

   

@app.route("/test-ai")
@login_required
def test_ai():
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Say hello to my Flask Todo app."
    )

    return response.text




with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True, port=5001)