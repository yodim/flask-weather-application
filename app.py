# importing librairies
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import http.client
import folium
import json


app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/Users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# defining the User class
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# defining login form
class LoginForm(FlaskForm):
    username = StringField('', validators=[InputRequired(), Length(min=4, max=15)],  render_kw={"placeholder": "Username"})
    password = PasswordField('', validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember me')

# defining the signup form
class RegisterForm(FlaskForm):
    username = StringField('', validators=[InputRequired(), Length(min=4, max=15)], render_kw={"placeholder": "Username"})
    password = PasswordField('', validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Password"})


# defining login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if (current_user.is_authenticated): # block users to access the login page if logged in
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
        return '<h1>Invalid username or password</h1>'
    return render_template('login.html', form=form)


# defining signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if (current_user.is_authenticated): # block users to access the signup page if logged in
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New user has been created!</h1>'
    return render_template('signup.html', form=form)

# defining home page route
@app.route('/')
@login_required
def home():
    infos = get_infos()
    weather = get_weather()
    start_coords = (infos['lat'], infos['lon'])
    folium_map = folium.Map(location=start_coords, zoom_start=14)
    tooltip = "Click me!"
    folium.Marker(
        [infos['lat'], infos['lon']], popup="<i>You are here !</i>", tooltip=tooltip
    ).add_to(folium_map)
    folium_map.save('templates/map.html')
    return render_template('index.html', name=current_user.username, folium_map=folium_map, city=infos['city'], ip=infos['ip'], 
                            temp_c=weather['temp_c'], wind_kph=weather['wind_kph'], humidity=weather['humidity'])

# defining the map route
@app.route('/map')
def map():
    return render_template('map.html')

# defining the lougout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



# defining a function that returns the coordinates of the user's location, his ip and his city
def get_infos():
    conn = http.client.HTTPSConnection("find-any-ip-address-or-domain-location-world-wide.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Host': "find-any-ip-address-or-domain-location-world-wide.p.rapidapi.com",
        'X-RapidAPI-Key': "0aa2a0e7efmsh7ca67aa8200a5d8p1a276ejsnc1b3a893f8ef"
    }
    conn.request("GET", "/iplocation?apikey=873dbe322aea47f89dcf729dcc8f60e8", headers=headers)
    res = conn.getresponse()
    json_data = res.read()
    data = json.loads(json_data)
    return {'ip':data["ip"], 'lat':data["latitude"], 'lon':data["longitude"], 'city':data["city"]}

# defining a function that returns the weather of the user's location
def get_weather():
    conn = http.client.HTTPSConnection("weatherapi-com.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Host': "weatherapi-com.p.rapidapi.com",
        'X-RapidAPI-Key': "0aa2a0e7efmsh7ca67aa8200a5d8p1a276ejsnc1b3a893f8ef"
        }
    conn.request("GET", "/current.json?q="+get_infos()['city'], headers=headers)
    res = conn.getresponse()
    json_data = res.read()
    data = json.loads(json_data)['current']
    return { 'temp_c':data['temp_c'], 'humidity':data['humidity'], 'wind_kph':data['wind_kph'] }