
from flask import Flask, request, render_template, redirect
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
            return 'POST'


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


@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    if request.method == 'GET':
        return render_template('logout.html')
    if request.method == 'POST':
        return 'POST'
    if request.method == 'DELETE':
        return 'DELETE'


@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM item")
            items = db_cur.fetchall()
        return render_template('items.html', items=items)
    if request.method == 'POST':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute('''INSERT INTO item (photo, name, description, price_hour, price_day, price_week, price_month)
            VALUES(:photo, :name, :description, :price_hour, :price_day, :price_week, :price_month) ''', request.form)
        return redirect('/items')



@app.route('/items/<items_id>', methods=['GET', 'DELETE'])
def item_details(items_id):
    if request.method == 'GET':
        with DB_local('identifier.sqlite') as db_cur:
            db_cur.execute("SELECT * FROM item WHERE id = ?", (items_id,))
            item = db_cur.fetchone()
            return render_template('items_id.html' , item=item)
    if request.method == 'DELETE':
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
        return render_template('leasers_id.html')


@app.route('/profile', methods=['GET', 'DELETE'])
def profile():
    if request.method == 'GET':
        return render_template('profile.html')
    if request.method == 'DELETE':
        return 'DELETE'



@app.route('/profile/<favouties>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def profile_fav(favouties):
    if request.method == 'GET':
        return render_template('favouties.html')
    if request.method == 'POST':
        return f'POST {favouties}'
    if request.method == 'PATCH':
        return f'PATCH {favouties}'
    if request.method == 'DELETE':
        return f'DELETE {favouties}'


@app.route('/profile/favouties/<favourite_id>', methods=['DELETE'])
def profile_user_fav(favourite_id):
    if request.method == 'DELETE':
        return f'DELETE {favourite_id}'


@app.route('/contracts', methods=['GET', 'POST'])
def contracts():
    if request.method == 'GET':
        return render_template('contracts.html')
    if request.method == 'POST':
        return 'POST'


@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH'])
def contract_details(contract_id):
    if request.method == 'GET':
        return render_template('contract_id.html')
    if request.method == 'PATCH':
        return f'PATCH {contract_id}'


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    if request.method == 'POST':
        return 'POST'


@app.route('/complain', methods=['POST'])
def complain():
    if request.method == 'POST':
        return 'POST'

@app.route('/compare', methods=['GET', 'PATCH'])
def compare():
    if request.method == 'GET':
        return render_template('compare.html')
    if request.method == 'PATCH':
        return 'PATCH'






if __name__ == '__main__':
    app.run(debug=True)