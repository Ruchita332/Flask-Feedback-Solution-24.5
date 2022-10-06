from http.client import UNAUTHORIZED
from flask import Flask, render_template, flash, redirect, session
from werkzeug.exceptions import Unauthorized


from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

from models import Feedback, db, connect_db, User

app = Flask (__name__)

app.config ['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hash_user_login'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SECRET_KEY'] = 'oh-so-secret'


connect_db(app)


####################################################################################

@app.route("/")
def root():
    if 'username' in session:
        return redirect (f"users/{session['username']}")
    return render_template("base.html")

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 Not Found page"""
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    """Show 401 Unauthorized user page"""
    return render_template('401.html'), 401

@app.route ("/register", methods = ["GET", "POST"])
def regirster():
    """Display the register user form and handle the user input"""

    if "username" in session:
        return redirect (f"/users/{session['username']}")
    
    form = RegisterForm();


    # """POST route"""
    if form.validate_on_submit():
        # Get the user input 
        username = form.username.data;
        password = form.password.data;
        email = form.email.data;
        first_name = form.first_name.data;
        last_name  = form.last_name.data;
        
        # print (f"username {username} email {email} firstname {first_name} last {last_name}")

        # Handle the input to create a new user
        new_user = User.register(username, password, email, first_name, last_name)
        
        db.session.commit ()
        
        session['username'] = new_user.username;

        flash (f"New user {username} created")
        return redirect (f"/users/{username}")

    else:
        """Show a form register/create a user form."""
        return render_template ("/users/register.html", form = form)

@app.route('/login', methods = ["GET", "POST"])
def login():
    """Display login form and handle user login"""

    if "username" in session:
        return redirect (f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate
        user = User.authenticate (username, password) # returns <user> if match otherwise False
        
        if user:
            session ['username'] = user.username;
            return redirect (f"/users/{username}")

        else:
            # username or password could not be authentiated/not a match
            form.username.errors = ["Invalid username/password."]
            return render_template ("/users/login.html", form=form)

    return render_template ("users/login.html", form = form)



@app.route ("/logout")
def logout():
    """Logout user"""
    session.pop("username")
    return redirect ("/login")

@app.route ("/users/<username>")
def show_user(username):
    """Check if the user is loggin in and display info"""

    if "username" not in session or username != session['username']:
        """User is not logged yet """
        raise Unauthorized()

    else:
        user = User.query.get (username)
        form = DeleteForm ()

        return render_template ("users/user.html", user=user, form = form)

@app.route ("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Check if the user is logged in to make the authorize delete request and execute the req """
    
    if "username" not in session or username != session['username']:
        """User is not logged yet """
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")

####################################################################################
"""Feedback routes"""

@app.route("/users/<username>/feedback/add", methods =["GET", "POST"])
def add_user_feedback(username):
    """if a user is authorized dispaly add-feedback form and process the input"""

    if "username" not in session or username != session ['username']:
        """User is not authorize to make any changes to the current account"""
        raise Unauthorized()
    
    """Else the user is authorized"""

    form = FeedbackForm()

    # POST route validate and process the inputs
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback (
            title = title,
            content = content,
            username = username
        )

        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{username}")

    else:
        #GET route display the form
        return render_template ("feedback/add.html", form=form)

@app.route ("/feedback/<int:feedback_id>/update", methods = ["GET", "POST"])
def edit_feedback(feedback_id):
    """Show the update-feedback form and handle the input.
    Make sure that the request is by the authorized user"""

    feedback = Feedback.query.get_or_404(feedback_id)


    if "username" not in session or feedback.username != session ['username']:
        """User is not authorized to make a update request"""
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

     # POST route validate and process the inputs
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    
    else: 
        # GET route display the form
        return render_template("/feedback/edit.html", form = form, feedback = feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods = ["POST"])
def delete_feedback(feedback_id):
    """verfy if the user is logged in and delete the requested feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session ['username']:
        """User is not authorized to make the delete request"""
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect (f"/users/{feedback.username}")