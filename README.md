# learning-backend-


the static folder is use for storing image and other data # Flask Todo App

This is a simple Todo List web application built using Flask. I created this project while learning Flask and backend development to understand how CRUD (Create, Read, Update, Delete) operations work with a database.

The application allows users to add, update, and delete tasks. All data is stored in a SQLite database using SQLAlchemy.

## Features

* Add a new todo
![alt text](<static/photo/Screenshot 2026-08-12 233127.png>)
* Update an existing todo
![alt text](<static/photo/Screenshot 2026-08-12 233405.png>)
* Delete a todo
* Store the date and time when a todo is created
![alt text](<static/photo/Screenshot 2026-08-12 233423.png>)
* Simple and responsive user interface

## Technologies Used

* Python
* Flask
* SQLAlchemy
* SQLite
* HTML
* Bootstrap 5

## Project Structure

```text
learning-backend-/
│
├── app.py
├── instance/
│   └── todo.db
├── templates/
│   ├── base.html
│   ├── index.html
│   └── update.html
├── static/
├── requirements.txt
└── README.md
```

## Running the Project

Run the application using:

```bash
python app.py
```

Then open your browser and visit:

```text
http://127.0.0.1:5001/
```

## What I Learned

Through this project, I learned:

* Flask routing
* Jinja2 templates
* Form handling
* CRUD operations
* SQLAlchemy ORM
* Working with SQLite
* Integrating Bootstrap with Flask

## Future Improvements

* Mark todos as completed
* Add search functionality
* User authentication
* Better UI design
* Deploy the application

## Author

**Siddheshwar Khandare**

GitHub: https://github.com/siddheshwarkhandare
