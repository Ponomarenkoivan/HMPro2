from functools import wraps
from typing import Dict, Any

from click.formatting import join_options
from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3
app = Flask(__name__)
# /login [GET, POST]
# /register [GET, POST]
# /logout [GET ? POST ?? DELETE]
#
# /profile (/user, /me) [GET, PUT(PATCH), DELETE]
#       ?  /favouties [GET, POST, DELETE, PATCH]
#       ??  /favouties/<favourite_id> [DELETE]
#       не додавав, вважаю непотрібним /search_history [GET, DELETE]
#
# /items [GET, POST]
# /items/<item_id> [GET, DELETE]
# /leasers [GET]
# /leasers/<leaser_id> [GET]
#
# /contracts [GET, POST]
# /contracts/<contract_id> [GET, PATCH/PUT]
#
# /search [GET, (POST)]
#
# /complain [POST]
# /compare [GET, PUT/PATCH]
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

class DataBase:
    db_file = 'identifier.sqlite'
    def select(self, table, filter_dict=None, join_conditions=None, join_table=None):
        if filter_dict is None:
            filter_dict = {}

        with DB_local(self.db_file) as db:
            query = f'SELECT * FROM {table}'
            if join_table is not None:
                query += f' JOIN {join_conditions} ON'
                join_conditions_list = []
                for left_field, right_field in join_conditions.items():
                    join_conditions_list.append(f'{table}.{left_field}={join_table}.{right_field}')
                query += ' AND '.join(join_conditions_list)

            if filter_dict:
                itms = [f"{key} = ?" for key in filter_dict.keys()]
                query += ' WHERE ' + ' AND '.join(itms)

            db.execute(query, tuple(value for value in filter_dict.values()))
            return  db.fetchall()

    def insert(self, table, data):
        with DB_local(self.db_file) as db:
            query = f'INSERT INTO {table} ('
            query += ', '.join(data.keys())
            query += ') VALUES ('
            query += ', '.join([f':{itm}' for itm in data.keys()])
            query += ')'
            db.execute(query, data)

db_connector = DataBase()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = db_connector.select('user', {'login': username, 'password': password})

        if user_data:

            session['logged_in'] = user_data[0]['login']
            return "Login successful, welcome " + user_data[0]['login']
        else:
            return "Wrong username or password", 401



@app.route('/register', methods=['GET', 'POST'])
def register(form_data=None):
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form_data = request.form
        db_connector.insert('user', form_data)
        return redirect('/login')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        items = db_connector.select('item')
        return render_template('items.html', items=items)

    if request.method == 'POST':
        if session.get('logged_in') is None:
            return redirect('/login')
        else:
            user_id = db_connector.select('user', {'login': session['logged_in']})[0]['id']

            query_args = dict(request.form)
            query_args['owner'] = user_id

            db_connector.insert('item', query_args)
            return redirect('/items')



@app.route('/items/<items_id>', methods=['GET', 'DELETE'])
def item_details(items_id):
    if request.method == 'GET':
        item = db_connector.select('item', {'id': items_id})[0]
        return render_template('items_id.html', item=item)
    if request.method == 'DELETE':
        if session.get('logged_in') is None:
            return redirect('/login')
        return f'DELETE {items_id}'


@app.route('/leasers', methods=['GET'])
def leasers(full_name):
    if request.method == 'GET':
        leasers = db_connector.select('leaser', {'full_name': full_name})
        return render_template('leasers.html', leasers=leasers)


@app.route('/leasers/<leasers_id>', methods=['GET'])
def leaser_details(leasers_id):
    if request.method == 'GET':
        leasers_id = db_connector.select('leaser', {'id': leasers_id})[0]['id']
        return render_template('leasers_id.html', leasers=leasers)


@app.route('/profile', methods=['GET', 'DELETE'])
@login_required
def profile():
    if request.method == 'GET':
        user_data = db_connector.select('user', {'login': session.get('logged_in')})
        if not user_data:
            return redirect('/login')
        full_name = user_data[0].get('full_name')
        return render_template('user.html', full_name=full_name)
    if request.method == 'DELETE':
        return 'DELETE'



@app.route('/profile/<favouties>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@login_required
def profile_fav(favouties, favourites=None):
    if request.method == 'GET':
        result = db_connector.select('favorites', {'id': favourites})
        if not result:
            return "Item not found", 404
        item = result[0].get('item')
        return render_template('favourites.html', item=item)
    elif request.method == 'POST':
        new_item = request.form.get('new_item')
        db_connector.insert('favorites', {'id': favourites, 'item': new_item})
        return f'POST {favourites}', 201
    if request.method == 'PATCH':
        return f'PATCH {favouties}'
    if request.method == 'DELETE':
        return f'DELETE {favouties}'


@app.route('/profile/favouties/<favourite_id>', methods=['DELETE'])
@login_required
def profile_user_fav(favourite_id):
    if request.method == 'DELETE':
        return f'DELETE {favourite_id}'


@app.route('/contracts', methods=['GET', 'POST'])
@login_required
def contracts():
    if request.method == 'GET':
        contracts = db_connector.select('contract')
        return render_template('contracts.html', contracts=contracts)
    elif request.method == 'POST':
        user_data = db_connector.select('user', {'login': session.get('logged_in')})
        if not user_data:
            return redirect('/login')
        taker = user_data[0].get('id')
        item_id = request.form['item']
        item_data = db_connector.select('item', {'id': item_id})
        if not item_data:
            return "Item not found", 404
        leaser = item_data[0].get('owner')
        contract_data = {
            'text': request.form['text'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'leaser': leaser,
            'taker': taker,
            'item': item_id,
            'status': "pending"
        }
        db_connector.insert('contract', contract_data)
        return 'POST'


@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH'])
@login_required
def contract_details(contract_id):
    if request.method == 'GET':
        contract_data = db_connector.select('contract', {'id': contract_id})
        if contract_data:
            contract = contract_data[0]
            return render_template('contract_id.html', contract=contract)
        else:
            return "Contract not found",404
    if request.method == 'PATCH':
        return f'PATCH {contract_id}'


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        search_results = db_connector.select('search_history')
        return render_template('search.html', search_results=search_results)
    if request.method == 'POST':
        search_term = request.form.get('search_text')
        db_connector.insert('search_history', {'term': search_term})
        return 'POST'


@app.route('/complain', methods=['POST'])
@login_required
def complain():
    if request.method == 'POST':
        db_connector.insert('feedback', {'complain': request.form['complain']})
        return 'POST'

@app.route('/compare', methods=['GET', 'PATCH'])
@login_required
def compare():
    if request.method == 'GET':
        db_connector.select('item', {'description': request.args.get('description')})
        return render_template('compare.html')
    if request.method == 'PATCH':
        return 'PATCH'






if __name__ == '__main__':
    app.run(debug=True)