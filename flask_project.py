import json
import capitalize as capitalize
import requests
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, PasswordField
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fasdfasdo;fadfasdofjasidfuhasdfiou'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    isactive = db.Column(db.Boolean(), default=True)
    text = db.Column(db.Text(), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
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

    def load_user(user_id):
        return db.session.query(User).get(user_id)


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField()


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin'))

        flash("Invalid username/password", 'error')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))



@app.route('/')
def index():
    api_key = '3d54eaad2124ca78ec826c93f2337aa6'
    url = f'http://api.openweathermap.org/data/2.5/weather?q=Tbilisi&appid={api_key}&units=metric'
    r = requests.get(url)
    result_json = r.text
    res = json.loads(result_json)
    city_name = res['name']
    country_code = res['sys']['country']
    coord_lon = res['coord']['lon']
    coord_lat = res['coord']['lat']
    city_weather = (res['weather'][0]['main'])
    city_sky = (res['weather'][0]['description'])
    temp = res['main']['temp']
    temp_feel = res['main']['feels_like']
    pressure = res['main']['pressure']
    humidity = res['main']['humidity']
    wind_speed = res['wind']['speed']
    wind_dirrection = res['wind']['deg']
    item = Item.query.all()
    return render_template('index.html', items=item, city_name=city_name,country_code=country_code,coord_lon=coord_lon,
                           coord_lat=coord_lat,city_weather=city_weather,city_sky=city_sky,temp=temp,temp_feel=temp_feel,
                           pressure=pressure,humidity=humidity,wind_speed=wind_speed,wind_dirrection=wind_dirrection)


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
@login_required
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


@app.route('/admin/')
@login_required
def admin():
    return render_template('create.html')


if __name__ == '__main__':
    app.run(debug=True)
