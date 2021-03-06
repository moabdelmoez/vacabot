#Create a file for HTTP routing
import os
import secrets
from PIL import Image
from flask import render_template, jsonify, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post, Vacation
from flask_login import login_user, current_user, logout_user, login_required

import dialogflow
import requests
import json

from dateutil.parser import parse
from datetime import datetime, timedelta, date
import time
#import timeout_decorator

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "mostbot-f83579cadd63.json"

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in :-)', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    #resize the uploaded image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


#Create a route for the new posts
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    #if current_user.is_authenticated:
    #    print("aaaaaa")
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                            form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post hase been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                            form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post hase been deleted!', 'success')
    return redirect(url_for('home'))

##Chatbot

@app.route('/index')
@login_required
def index():
    return render_template('index1.html', title='Vacation Request')
###
#Sending messages to Dialogflow and displaying responses

#@timeout_decorator.timeout(5)
def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    if text:
        try:
            text_input = dialogflow.types.TextInput(
                text=text, language_code=language_code)
            query_input = dialogflow.types.QueryInput(text=text_input)
            #with eventlet.Timeout(5):
            response = session_client.detect_intent(
                session=session, query_input=query_input)
            return response, True
            #return 'Sorry, try again 2!', False
        except:
            return 'Sorry, try again!', False
        

###
#Create a route that this text will be submitted tol
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def checkTeamAvailability(my_date):
    old_count = Vacation.query.filter_by(day=my_date.date()).count()
    existing_users = len(User.query.all())
    if (old_count+1)/existing_users > .5:
        return False, old_count
    else:
        return True, old_count

def checkDatesAvailability(my_dates_list):
    is_exist = 0
    exist_day = None
    users_count = 0
    is_available = False
    vacations_list = []
    for d in my_dates_list:
        if d.strftime('%A') not in ['Saturday', 'Sunday']:
            #if the day is not a weekend day, check if the date is reserved before
            if not Vacation.query.filter_by(day=d.date(),user_id=current_user.id).scalar():
                #check if this day is avaialble
                is_available, users_count = checkTeamAvailability(d)
                if is_available:
                    vacation = Vacation(day=d, owner=current_user)
                    vacations_list.append(vacation)
                else:
                    exist_day = d
                    break
            else:
                is_exist = 1
                exist_day = d
                break
    return { 
        'vacations_list': vacations_list, 
        'is_exist': is_exist,
        'exist_day': exist_day,
        'is_available': is_available,
        'users_count': users_count    
    }
    
@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    my_response, status = detect_intent_texts(project_id, "unique", message, 'en')
    print(my_response)
    if status and my_response:
        fulfillment_text = my_response.query_result.fulfillment_text
        today_date = datetime.today().date()
        print(my_response.query_result.intent.display_name)
        
        ## Vacation add request .. extract the date and save it in database
        if my_response.query_result.intent.display_name == "Vacation\'s Request - yes":
            my_date = dict(my_response.query_result.output_contexts[0].parameters)['start_date']
            my_date_end = dict(my_response.query_result.output_contexts[0].parameters)['end_date']
            saved_date = parse(my_date)
            dayname = saved_date.date().strftime('%A')
            if my_date_end:
                saved_date_end = parse(my_date_end)
            
            ## Validate and save
            if saved_date.date() < today_date:
                #check if it is an old date
                response_text = {"message": ["Oh! sorry, you cannot request a vacation in the past!"] }
            elif my_date_end and saved_date.date() >= saved_date_end.date():
                #check if the start date is not older than the end date
                response_text = {"message": ["Bad range! Please make sure about the two dates mentioned"] }
            elif dayname in ['Saturday','Sunday']:
                #check if the requested date is a weekend day
                response_text = {"message": ["Oh! this day is %s, it is a weekend! I'm afraid that you cannot request a vacation on a weekend day." %(dayname)] }  
            else:
                #form a list of the requested dates
                if my_date_end: 
                    my_dates_list = list(daterange(saved_date,saved_date_end))
                else:
                    my_dates_list = [saved_date]
                #try:
                available_dates = checkDatesAvailability(my_dates_list)
                print(available_dates)
                if available_dates['is_exist'] == 0 and available_dates['is_available']:
                    db.session.add_all(available_dates['vacations_list'])
                    db.session.commit()
                    response_text = {"message": [fulfillment_text] }
                elif available_dates['is_exist'] == 1:
                    exist_day = available_dates['exist_day'].strftime('%Y-%m-%d')
                    response_text = {"message": ["Oh! The date %s is reserved before in your planned vacations. I am afraid that you cannot request it again." %(exist_day)] }
                elif available_dates['is_available'] == False:
                    exist_day = available_dates['exist_day'].strftime('%Y-%m-%d')
                    response_text = {"message": ["Oh, I am so sorry! You cannot request a vacation on this day %s because %d colleagues have reserved this day before you" %(exist_day,available_dates['users_count']), 'The rules say that at least 50% of the team should be available'] }
                #except:
                #    response_text = {"message": ["Please try again later - Error 1"] }
        
        ## Vacation count request .. check in database and reply
        elif my_response.query_result.intent.display_name == "Vacation Count":
            try:
                my_vacations = Vacation.query.filter_by(user_id=current_user.id)
                old_vacations = 0
                planned_vacations = 0
                total_vacaations = os.getenv('TOTAL_PERMITTED_VACATIONS_PER_YEAR')
                for one_vacation in my_vacations:
                    if one_vacation.day.year == today_date.year and one_vacation.day <= today_date:
                        old_vacations += 1
                    elif one_vacation.day.year == today_date.year and one_vacation.day > today_date:
                        planned_vacations += 1
                remaining_vacations = int(total_vacaations) - old_vacations - planned_vacations
                vacations_summary = ['Your vacation summary this year is:',"Old vacations: %d, Upcomming planned vacations: %d, Remaining vacations: %d" %(old_vacations, planned_vacations, remaining_vacations)]
                response_text = {"message": vacations_summary }
            except:
                response_text = {"message": ["Please try again later - Error 2"] }
            
        else:
            response_text = { "message": [fulfillment_text] }
    else:
        response_text = { "message": ['Please try again later - Error 3'] }
    return jsonify(response_text)


@app.route('/dashboard')
@login_required
def dashboard():
    my_list = []
    start_date = parse('2018-01-01')
    end_date = parse('2019-01-01')
    users = User.query.all()
    for user in users:
        vacations = Vacation.query.filter_by(user_id=user.id).order_by(Vacation.day.asc()).filter(Vacation.day >= start_date).filter(Vacation.day < end_date)
        old_vacations = vacations.filter(Vacation.day <= date.today())
        new_vacations = vacations.filter(Vacation.day > date.today())
        total_vacaations = str(os.getenv('TOTAL_PERMITTED_VACATIONS_PER_YEAR'))
        print(total_vacaations)
        remaining = int(total_vacaations) - (old_vacations.count() + new_vacations.count())
        my_list.append({
            'user':user,
            'old_count':old_vacations.count(),
            'old':old_vacations,
            'new_count':new_vacations.count(),
            'new':list(new_vacations),
            'remaining':remaining
        })
    return render_template('dashboard.html', data=my_list)
