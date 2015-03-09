#!flask/bin/python
import sqlite3
from flask import Flask
from flask import render_template,flash, redirect
from flask.ext.login import LoginManager
app= Flask(__name__)
app.config.from_object('config')

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required,user_logged_in

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Message, Mail
from werkzeug import generate_password_hash,check_password_hash


class SigninForm(Form):
	username = StringField('username', validators=[DataRequired()])
	password = StringField('password', validators=[DataRequired()])	
class LoginForm(Form):
	openid = StringField('openid', validators=[DataRequired()])
	name = StringField('name', validators=[DataRequired()])
	mark= StringField('mark', validators=[DataRequired()])
class SearchForm(Form):
	signin= StringField('signin', validators=[DataRequired()])

lm=LoginManager()
lm.init_app(app)
lm.login_view = '/'
lm.login_message = u'Log in here!'
	

@lm.user_loader
def load_user(id):
	c=sqlite3.connect('test.db')
	c=c.execute('SELECT * from userd where id=(?)',[id])
	userrow=c.fetchone()
	if userrow!=None:
		return User(userrow[1],userrow[2],userrow[3],userrow[4])


@app.route('/', methods=['GET', 'POST'])
def login():
	a=[];
	sign= SigninForm()
	s=SearchForm()
	u=sign.username.data
	if sign.validate_on_submit():
		passcheck=False
		user=sign.username.data
		password=sign.password.data
		m = sqlite3.connect('test.db')
		m.execute("DROP TABLE IF EXISTS LOG");
		search=m.execute("SELECT * FROM userd WHERE username = ? ",[user]);
		for i in search:
			passcheck=check_password_hash(i[1],password)
			username=i[0]
			password=i[1]
			
		if passcheck==False:
			flash("Incorrect Password or Username")
		else:
			m.execute("CREATE TABLE LOG(NAME TEXT)");
                	m.execute("INSERT INTO LOG VALUES(?)",[username]);
                	m.commit()
                	m.close()
	
			return redirect('/signin')
	if s.validate_on_submit():
                find=s.signin.data

	        c = sqlite3.connect('test.db')
	
		search=c.execute("SELECT * FROM "+find);

		for i in search:
			flash('%s %s     %s'%(i[0],i[1],i[2]))
		
		c.commit()
		c.close()
		return redirect('/show')	

        return render_template('index.html',
				sign=sign,s=s)



@app.route('/signup',methods=['GET', 'POST'])
def signup():
	u=SigninForm()

	if u.validate_on_submit():
                user=u.username.data
		passw=generate_password_hash(u.password.data)
                c = sqlite3.connect('test.db')
		c.execute('''CREATE TABLE '''+ user+'''
                         (ID           INT    NOT NULL,
                          NAME           TEXT    NOT NULL,
                          MARK           INT    NOT NULL)''');

		c.execute("INSERT INTO userd(username,password) VALUES(?,?)",[user,passw]);
		c.commit()
		c.close()
		return redirect('/signup')

	return render_template('signup.html',u=u)

		

@app.route('/signin', methods=['GET', 'POST'])
def index():
  try:
       form=LoginForm()
       b=[];
       c = sqlite3.connect('test.db')
       search=c.execute("SELECT * FROM LOG");
       for i in search:
		b.append(i[0])

       if form.validate_on_submit():
		#b="show"
               	idname=form.openid.data
               	name=form.name.data
               	mark=form.mark.data
               	conn = sqlite3.connect('test.db')
               	conn.execute("INSERT INTO "+b[0]+" (ID,NAME,MARK) VALUES (?,?,?)",[idname,name,mark]);
               	conn.commit()
               	conn.close()
               	return redirect('/index')
       return render_template('home.html',form=form)	
			
  except:
	return render_template('/error.html')
	return redirect('/')

@app.route('/show')
def show():
   

     return render_template('show.html')

@app.route("/logout")
#@login_required
def logout():
	logout_user()
	c = sqlite3.connect('test.db')
	c.execute("DROP TABLE IF EXISTS LOG");
	c.commit()
	c.close()
	return redirect('/')

app.run(debug=True)

