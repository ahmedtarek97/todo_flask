from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate
app = Flask(__name__)
# note if the database must be created as SQLAlchemy will not create it for us
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# Models
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<TODO {self.id} {self.description}>'


# db.create_all()


# Controllers
# CREATE
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        # to acess the todo object during the session only
        # to not cause an error
        body['description'] = todo.description
        body['id'] = todo.id
        body['completed'] = todo.completed
        # tells the view to redirect to the index route
        # but it requires page refresh to show changes

        # return redirect(url_for('index'))
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if not error:
            # the ajax version
            return jsonify(body)


# Update
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        print('completed', completed)
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


# READ
@app.route('/')
def index():
    # function to specify an html file to render
    # when the user visits this route
    # by default flak searches for these files in a folder named templates
    # so we should create this folder
    # we can pass variables that we can use in our template
    # the controller is telling the model to do a select * statment
    # on the todos table of the database
    # and it is telling the views to use the index.html template
    # to show that data
    return render_template('index.html', todos=Todo.query.order_by('id').all())
