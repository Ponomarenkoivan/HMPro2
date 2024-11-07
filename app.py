from functools import wraps

from flask import Flask, request, render_template, redirect, session
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with DB_local('identifier.sqlite') as db:
            db.execute('SELECT * FROM user WHERE login = ? AND password = ?',
                       (username, password))
            user = db.fetchone()
            if user:
                session['logged_in'] = user['login']
                return "Login successful, welcome " + user['login']
            else:
                return "Wrong username or password", 401



@app.route('/register', methods=['GET', 'POST'])
def register(form_data=None):
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        with DB_local('identifier.sqlite') as db_cur:
            form_data = request.form
            db_cur.execute('''INSERT INTO user 
            (login, password, ipn, full_name, contacts, pfoto) 
            VALUES (?, ?, ?, ?, ?, ?)''',
                (
                            form_data['login'], form_data['password'], form_data['ipn'],
                            form_data['full_name'], form_data['contacts'], form_data['pfoto'])
                        )
        return redirect('/login')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM item")
            items = db_cur.fetchall()
        return render_template('items.html', items=items)

    if request.method == 'POST':
        if session.get('logged_in') is None:
            return redirect('/login')
        else:

            with DB_local('identifier.sqlite') as db_cur:
                user_login = session['owner']
                db_cur.execute("SELECT id FROM user WHERE login = ?", (user_login,))
                user_id = db_cur.fetchone()['id']

                query_args = dict(request.form)
                query_args['owner'] = user_id

                db_cur.execute('''INSERT INTO item (photo, name, description, price_hour, price_day, price_week, price_month, owner)
                            VALUES(:photo, :name, :description, :price_hour, :price_day, :price_week, :price_month, :owner)''',query_args)
            return redirect('/items')



@app.route('/items/<items_id>', methods=['GET', 'DELETE'])
def item_details(items_id):
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM item WHERE id = ?", (items_id,))
            item = db_cur.fetchone()
        return render_template('items_id.html', item=item)
    if request.method == 'DELETE':
        if session.get('logged_in') is None:
            return redirect('/login')
        return f'DELETE {items_id}'


@app.route('/leasers', methods=['GET'])
def leasers(full_name):
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT full_name FROM user")
            user = db_cur.fetchall()
        return render_template('leasers.html', user=user)


@app.route('/leasers/<leasers_id>', methods=['GET'])
def leaser_details(leasers_id):
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT leaser FROM contract WHERE id = ?", (leasers_id,))
            leaser = db_cur.fetchone()
        return render_template('leasers_id.html', leaser=leaser)


@app.route('/profile', methods=['GET', 'DELETE'])
@login_required
def profile():
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            query = f'SELECT * FROM user WHERE login = ?'
            print(query)
            db_cur.execute(query, (session['logged_in'],))
            full_name = db_cur.fetchone()['full_name']
        return render_template('user.html', full_name=full_name)
    if request.method == 'DELETE':
        return 'DELETE'



@app.route('/profile/<favouties>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@login_required
def profile_fav(favouties):
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT item FROM favorites WHERE id = ?", (favouties,))
            item = db_cur.fetchone()
        return render_template('favouties.html' , item=item)
    if request.method == 'POST':
        return f'POST {favouties}'
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
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM contract")
            contracts = db_cur.fetchall()
            return render_template('contracts.html', contracts=contracts)
    if request.method == 'POST':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute('select id from user where login = ?', (session['logged_in'],))
            my_id = db_cur.fetchone()['id']
            taker = my_id
            item_id = request.form['item']

            db_cur.execute('select * from item where id = ?', (item_id,))
            leaser = db_cur.fetchone()['owner']

            contract_status = "pending"

            query_args = (request.form['text'], request.form['start_date'], request.form['end_date'], leaser, taker, item_id, contract_status)
            inser_query = '''insert into contract (text, start_date, end_date, leaser, taker, item, status) values (?, ?, ?, ?, ?, ?, ?)'''
            db_cur.execute(inser_query, query_args)


        return 'POST'


@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH'])
@login_required
def contract_details(contract_id):
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM contract WHERE id = ?", (contract_id,))
            contract = db_cur.fetchone()
        return render_template('contract_id.html')
    if request.method == 'PATCH':
        return f'PATCH {contract_id}'


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM search")
        return render_template('search.html')
    if request.method == 'POST':
            return 'POST'


@app.route('/complain', methods=['POST'])
@login_required
def complain():
    if request.method == 'POST':
        return 'POST'

@app.route('/compare', methods=['GET', 'PATCH'])
@login_required
def compare():
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM item WHERE id = ?", (session['logged_in'],))
            item = db_cur.fetchone()
        return render_template('compare.html')
    if request.method == 'PATCH':
        return 'PATCH'






if __name__ == '__main__':
    app.run(debug=True)