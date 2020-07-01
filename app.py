from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from send_mail import send_mail
from datetime import date 

app = Flask(__name__)

POSTGRES_ENV = 'prod'

if POSTGRES_ENV == 'dev':
    app.debug = True
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user="postgres",pw="NEW-pass-1966",url="127.0.0.1",db="lexus")
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL 
else:
    app.debug = False
    # below line needs changing for PROD!
    #DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user="postgres",pw="NEW-pass-1966",url="127.0.0.1",db="lexus")
    DB_URL = "postgres://gqthvmyynbwqxu:384b01605d6802af4f2fab446f93db1c9f55d337b23b88c69d8e35da94ed8cd0@ec2-3-231-16-122.compute-1.amazonaws.com:5432/d8c8mndalo6glb"
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL 

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.String(200))

    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments

class Users(db.Model):
    #email = StringField('Email', [validators.Length(min=8, max=50)])
    #username = StringField('Username', [validators.Length(min=8, max=25)])
    #password1 = StringField('Password', [
    #validators.DataRequired(), 
    #validators.EqualTo('confirm', message='Passwords do not match')])
    #confirm = PasswordField('Confirm Password')
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(50), unique=True)
    password1 = db.Column(db.String(20))
    registration_date = db.Column(db.Date)
    idea = db.Column(db.String(20))

    def __init__(self, email, username, password1, registration_date, idea):
        self.email = email 
        self.username = username  
        self.password1 = password1  
        self.registration_date = registration_date 
        self.idea = idea 

@app.route('/registeruser', methods=['POST'])
def registeruser():
    print ('inside registeruser')
    #form = Users(request.form)
    if request.method == 'POST':
    #if request.method == 'POST' and form.validate():
        email = request.form['email']
        username = request.form['username']
        password1 = request.form['password1']
        password1_candidate = request.form['password1_candidate']
        registration_date = date.today()
        idea = request.form['idea']
        #print ('email = ' + email)
        #print ('user = ' + username)
        #print ('passw    = ' + password1)
        #print ('passw_oth    = ' + password1_candidate)
        #if sha256_crypt.verify(password1_candidate, password1):
        #    app.logger.info('Password matched')
        #    #sha256_crypt.verify(password1_candidate, password1):
        #    #registration_date = ??
        if db.session.query(Users).filter(Users.username == username).count() == 0:
            data = Users(email, username, password1, registration_date, idea)
            db.session.add(data)
            db.session.commit()
            #send_mail(customer, dealer, rating, comments)
            #flash ('you are  registered, now you can login')
            return render_template('successlogin.html')
        else:
            app.logger.info('User already exists')
            #flash ('User already exists')
            return render_template('register.html')
        #else:
        #    app.logger.info('Passwords do not match')
        #    flash ('Passwords do not match')
        #    return render_template('login.html', form=form)
    return render_template('index.html', form=form)

@app.route('/loginuser', methods=['POST'])
def loginuser():
    # need to change this 
    # needs more work
    #
    print ('inside loginuser')
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        #cur = mysql.connection.cursor()  
        #result = cur.execute("select * from users where username = %s", [username])
        if db.session.query(Users).filter(Users.username == username, Users.password1 == password1).count() == 0:
            app.logger.info('User and password combination not found in the application')
            #flash ('User, password combination is not registered within the application!')
            return render_template('login.html')
            #return redirect(url_for("login"))
        else:
            app.logger.info('Password and login ok')
            #flash ('Login all ok')
            #return render_template('view.html')
            return redirect(url_for('viewreg', Users = Users))
            #return render_template('view.html', Feedback = Feedback)
    #return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/view', methods=['GET', 'POST'])
def view():
    #if request.method == 'GET':
    # query from a class
    table = db.session.query(Feedback).all()
    return render_template('view.html', Feedback=Feedback.query.all())

@app.route('/viewreg', methods=['GET', 'POST'])
def viewreg():
    #if request.method == 'GET':
    # query from a class
    table = db.session.query(Users).all()
    return render_template('viewreg.html', Users=Users.query.all())

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']
        print(customer, dealer, rating, comments)
        if customer == '' or dealer == '':
            return render_template('index.html', message='Please enter required fields')
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            data = Feedback(customer, dealer, rating, comments)
            db.session.add(data)
            db.session.commit()
            send_mail(customer, dealer, rating, comments)
            return render_template('success.html')
        return render_template('index.html', message='You have already submitted feedback')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
