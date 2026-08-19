from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
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
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)

class todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False) 
    desc =  db.Column(db.String(500), nullable=False)
    date_created = db.Column(
        db.DateTime,
        default=lambda: datetime.now(IST)
    )

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
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return {"error": "No voice text received"}, 400

    print("Voice command:", text)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""
You are a Todo assistant.

The user said:
"{text}"

Understand what the user wants and return ONLY JSON.

Possible actions:

create
delete
update
list

For create:
{{
    "action": "create",
    "title": "task title",
    "description": "task description"
}}

For delete:
{{
    "action": "delete",
    "title": "task title"
}}

For update:
{{
    "action": "update",
    "old_title": "old task title",
    "title": "new task title",
    "description": "new description"
}}

For list:
{{
    "action": "list"
}}
"""
    )

    print("Gemini response:", response.text)

    return {
        "message": "Gemini understood the command",
        "text": text,
        "ai_response": response.text
    }


@app.route("/test-ai")
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