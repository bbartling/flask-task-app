from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import TaskForm


from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from dataclasses import dataclass


BASE_DIR = Path(__file__).parent
print(BASE_DIR)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR.joinpath('db.sqlite'))
print(SQLALCHEMY_DATABASE_URI)

 
db = SQLAlchemy()

def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    print('Setup DB Success!')
    
    
def db_drop_and_create_all(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('DB drop all and create all Success!')
        t1 = Task(title='New Task 1')
        t2 = Task(title='New Task 2')
        db.session.add(t1)
        db.session.add(t2)
        db.session.commit()
        tasks = Task.query.all()
        print('tasks: ',tasks)
        print('t1.id: ',t1.id)
        print('t2.id: ',t2.id)
        print(Task.query.all())
        
    
@dataclass
class Task(db.Model):
    
    id: int
    title: str
    date: datetime
    completed: bool
    
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(140))
    date = db.Column(db.DateTime(),default=datetime.now())
    completed = db.Column(db.Boolean(),default=False)
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        
    def __repr__(self):
        return f'<Task id: {self.id} - {self.title}'



app = Flask(__name__)
setup_db(app)
db_drop_and_create_all(app)


@app.route('/')
def index():
    tasks = Task.query.all()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(tasks)
    return render_template('index.html')


@app.route('/create', methods=['POST'])
def create_task():
    print('request.get_json()',request.get_json())
    user_input = request.get_json()
    
    form = TaskForm(data=user_input)
    print('form.validate(): ',form.validate())
    if form.validate():
        task = Task(title=form.title.data)
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task)
    
    return redirect(url_for('index'))



@app.route('/delete', methods=['POST'])
def delete_task():
    task_id = request.get_json().get('id')
    task = Task.query.filter_by(id=task_id).first()
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'result':'Ok'})


@app.route('/complete', methods=['POST'])
def complete_task():
    task_id = request.get_json().get('id')
    task = Task.query.filter_by(id=task_id).first()
    
    task.completed = True
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({'result':'Ok'})


if __name__ == '__main__':
    app.run()