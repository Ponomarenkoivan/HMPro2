from functools import wraps
from typing import Dict, Any
from unittest import result

from click.formatting import join_options
from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3

from sqlalchemy import select
from sqlalchemy.sql.functions import current_user

from database import init_db, db_session
import models
import celery_tasks


app = Flask(__name__)

app.secret_key = 'vemoevmerivjnteb'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DB_local():
    def __init__(self, file_name):
        self.con = sqlite3.connect(file_name)
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
    def __enter__(self):
        return self.cur
    def __exit__(self, type, value, traceback):
        self.con.commit()
        self.con.close()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('logged_in') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrap





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        init_db()
        user = db_session.scalar(select(models.User).where(models.User.login == username))
        if user and user.password == password:
            session['logged_in'] = user.login
            return "Login successful, welcome " + user.login
        else:
            return "Wrong username or password", 401



@app.route('/register', methods=['GET', 'POST'])
def register(form_data=None):
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = dict(request.form)
        init_db()
        user = models.User(**form_data)
        db_session.add(user)
        db_session.commit()
        return redirect('/login')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        init_db()
        items_query = select(models.Item)
        items = list(db_session.execute(items_query).scalars())
        return render_template('items.html', items=items)

    if request.method == 'POST':
        if session.get('logged_in') is None:
            return redirect('/login')
        else:
            init_db()
            user = db_session.scalar(select(models.User).where(models.User.login == session['logged_in']))
            query_args = dict(request.args)
            query_args['owner'] = user.id
            new_item = models.Item(**query_args)
            db_session.add(new_item)
            db_session.commit()
            return redirect('/items')



@app.route('/items/<items_id>', methods=['GET', 'DELETE'])
def item_details(items_id):
    if request.method == 'GET':
        init_db()
        item = db_session.scalar(select(models.Item).filter_by(id=items_id)).scalar()

        if not item:
            return "Item not found", 404
        return render_template('items_id.html', item=item, user_id=session['logged_in'])
    if request.method == 'DELETE':
        if session.get('logged_in') is None:
            return redirect('/login')
        return f'DELETE {items_id}'


@app.route('/leasers', methods=['GET'])
def leasers(full_name):
    if request.method == 'GET':
        init_db()
        leaser_query= select(models.Contract)
        leasers = list(db_session.execute(leaser_query).scalars())
        return render_template('leasers.html', leasers=leasers)


@app.route('/leasers/<leasers_id>', methods=['GET'])
def leaser_details(leasers_id):
    if request.method == 'GET':
        init_db()
        leasers_query = select(models.Contract).where(models.Contract.id == leasers_id)
        leaser = list(db_session.execute(leasers_query).scalars())
        return render_template('leasers_id.html', leaser=leaser)


@app.route('/profile', methods=['GET', 'DELETE'])
@login_required
def profile():
    if 'logged_in' not in session:
        return redirect('/login')
    user_login = session['logged_in']

    if request.method == 'GET':
        init_db()
        user = db_session.scalar(select(models.User).where(models.User.login == user_login))
        if not user:
            return redirect('/login')
        return render_template('profile.html', user=user)
    if request.method == 'DELETE':
        return 'DELETE'



@app.route('/profile/<favorites>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@login_required
def profile_fav(favorites):
    init_db()
    user_login = session['logged_in']

    if request.method == 'GET':
        favorites = db_session.scalar(select(models.Favorite).where(models.Favorite.user == user_login)).all
        if not favorites:
            return "No favorites", 404
        return render_template('favorites.html', favorites=favorites)
    if request.method == 'POST':
        new_favorite = models.Favorite(**request.json)
        db_session.add(new_favorite)
        db_session.commit()
        return redirect('/profile')
    if request.method == 'PATCH':
        return f'PATCH {favorites}'
    if request.method == 'DELETE':
        return f'DELETE {favorites}'


@app.route('/profile/favorites/<favorite_id>', methods=['DELETE'])
@login_required
def profile_user_fav(favorite_id):
    if request.method == 'DELETE':
        return f'DELETE {favorite_id}'


@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        init_db()
        contracts = db_session.scalars(select(models.Contract)).scalars()
        return render_template('contracts.html', contracts=contracts)

    if request.method == 'POST':
        user = db_session.scalar(select(models.User).where(models.User.login == session.get('logged_in')))
        if not user:
            return redirect('/login')

        item_id = request.form['item']
        item = db_session.scalar(select(models.Item).where(models.Item.id == item_id))
        if not item:
            return "Item not found", 404

        query_args = dict(request.args)
        new_contract = models.Contract(**query_args)
        db_session.add(new_contract)
        db_session.commit()
        celery_tasks.send_email(new_contract.id)
        return redirect('/contracts')


@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH'])
@login_required
def contract_details(contract_id):
    if request.method == 'GET':
        init_db()
        contract = db_session.scalar(select(models.Contract).where(models.Contract.id == contract_id))
        if not contract:
            return "Contract not found", 404
        return render_template('contract_id.html', contract=contract)

    if request.method == 'PATCH':
        return f'PATCH {contract_id}'


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        init_db()
        user_login = session['logged_in']
        user = db_session.scalar(select(models.User).where(models.User.login == user_login))
        search_results = db_session.scalar(select(models.Search_history).where(models.Search_history.user == user_login))
        return render_template('search.html', search_results=search_results)
    if request.method == 'POST':
        search_results = request.form.get('search_text')
        if not search_results:
            return "Search text not found", 404
        query_args = dict(request.args)
        search_entry= models.Contract(**query_args)
        db_session.add(search_entry)
        db_session.commit()
        return redirect('/search')

@app.route('/complain', methods=['POST'])
@login_required
def complain():
    init_db()
    user_login = session['logged_in']
    user = db_session.scalar(select(models.User).where(models.User.login == user_login))

    if request.method == 'POST':
        complaint_text = request.form.get('complain')
        if not complaint_text:
            return "Complaint text is required", 400
        query_args = dict(request.args)
        feedback = models.Feedback(**query_args)
        db_session.add(feedback)
        db_session.commit()
        return "Complaint submitted", 201

@app.route('/compare', methods=['GET', 'PATCH'])
@login_required
def compare():
    if request.method == 'GET':
        init_db()
        compare_items = db_session.scalar(select(models.Item).where(models.Item.description == 'description')).all()
        return render_template('compare.html')
    if request.method == 'PATCH':
        return 'PATCH'

@app.route('/add_task', methods=['GET'])
def set_task():
    celery_tasks.add.delay(1, 1)
    return 'Task send'



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)