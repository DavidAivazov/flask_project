from logging import Manager
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = Manager(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    isactive = db.Column(db.Boolean(), default=True)
    text = db.Column(db.Text(), nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/')
def index():
    item = Item.query.all()
    return render_template('index.html', items=item)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/buy/<int:id>')
def buy_item(id):
    item = Item.query.get(id)
    price = f"{item.price}00"
    api = Api(
        # კომპანიის იდ
        merchant_id=1396424,
        # კომპანიის key თანხის მისაღებად
        secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "GEL",
        "amount": price
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']

        item = Item(title=title, price=price, text=text)

        try:
            if title == "" or price == "" or text == "":
                return 'ERROR[0]'
            else:
                db.session.add(item)
                db.session.commit()
            return redirect('/')
        except:
            return 'ERROR[1]'

    else:
        return render_template('create.html')


@app.route('/admin')
def admin():
    return 'test'


if __name__ == '__main__':
    app.run(debug=True)
