import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///classes.db")

CLASS_TYPES = [
    "Fitness",
    "Dance"
]

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
]

TIMES = [
    "10:30",
    "11:30",
    "12:30",
    "17:30",
    "18:30",
    "19:30"
]
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show current classes"""
    # Use current session
    user_id = session["user_id"]

    # Search for transactions created by current user
    classes = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    
    # Store current cash in variable
    current_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    return render_template("index.html", classes=classes, current_cash=current_cash)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure Confirmation password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password")

        # Ensure both passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("both passwords must match")

        # Remember user and a hashed password
        name = request.form.get("username")
        password = request.form.get("password")
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Insert variables into database, as long as user´s name does not already exist
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name, hash_password)
        except:
            return apology("Username already exists")

        # After registering, log in new user
        session["user_id"] = new_user

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure class type was submitted
        if not request.form.get("class_type"):
            return apology("Must choose a class type")

        # Ensure day was submitted
        if not request.form.get("day"):
            return apology("Must choose a day")

        # Ensure time was submitted
        if not request.form.get("time"):
            return apology("Must choose a time")

        # Save user´s choice
        class_type = request.form.get("class_type")
        day = request.form.get("day")
        time = request.form.get("time")

        # Ensure user´s choice is valid
        if class_type not in CLASS_TYPES:
            return apology("Must choose a valid class")
        if day not in DAYS:
            return apology("Must choose a valid day")
        if time not in TIMES:
            return apology("Must choose a valid time")
        
        # Use current session
        user_id = session ["user_id"]

        # Take class price according to user´s choice
        if class_type == 'Fitness':
            price = db.execute("SELECT price FROM classes where class_type = 'Fitness'")

        if class_type == 'Dance':
            price = db.execute("SELECT price FROM classes where class_type = 'Dance'")

        # Ensure user does not sign in to the same class twice
        current_concat = db.execute("SELECT concat FROM transactions WHERE user_id = ?", user_id)
        concat_str = class_type + day + time
        
        for row in current_concat:
            if concat_str == row["concat"]:
                return apology("You are already signed to that class")

        # Ensure user has enough cash to purchase class            
        current_cash = db.execute ("SELECT cash FROM users where id = ? LIMIT 1", user_id)
        user_cash = current_cash[0]["cash"]

        current_price = price[0]["price"]
        if current_price > user_cash:
            return apology("Not Enough money. Please add cash to your account")
        
        # Update user´s cash in account
        updated_cash = user_cash - current_price
        try:
            db.execute("UPDATE users set cash = ? WHERE id = ?", updated_cash, user_id)
        except Exception as e:
            return apology("Error updating cash")

        # Update class into transactions table
        try:
            db.execute("INSERT INTO transactions (user_id, class_type, qty, price, Day, Time, concat) VALUES(?, ?, 1, ?, ?, ?, ?)", user_id, class_type, current_price, day, time, concat_str)
        except:
            return apology("Error inserting class")

        # Return success message
        return render_template("success.html")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("sign_up.html", class_types=CLASS_TYPES, days=DAYS, times=TIMES)

@app.route("/deregister", methods=["POST"])
def deregister():

    # Use current session
    user_id = session ["user_id"]

    # class price
    class_id = request.form.get("class_id")
    class_type = request.form.get("class_type")

    # Save class price in order to return the cash to user
    if class_type == 'Fitness':
        class_price = db.execute("SELECT price FROM classes where class_type = 'Fitness'")

    if class_type == 'Dance':
        class_price = db.execute("SELECT price FROM classes where class_type = 'Dance'")

    if class_price:
        class_price = (class_price[0]["price"])
    else:
        return apology("Class price not found.")

    # forget class
    if class_id:
        db.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", class_id, user_id)
    
    # Return cash to user
    current_cash = db.execute ("SELECT cash FROM users where id = ? LIMIT 1", user_id)
    user_cash = current_cash[0]["cash"]
        
    updated_cash = user_cash + class_price
    
    try:
        db.execute("UPDATE users set cash = ? WHERE id = ?", updated_cash, user_id)
    except Exception as e:
        return apology("Error updating cash")

    # Return success message
    return render_template("success_deregister.html")

@app.route("/add_cash", methods=["GET", "POST"])
def add_cash():

    # Use current session
    user_id = session ["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure cash was submitted
        if not request.form.get("add_cash"):
            return apology("Choose how much cash you would like to add")

        # Ensure integer as cash was submitted
        try:
            additional_cash = int(request.form.get("add_cash"))
        except:
            return apology("Must provide a positive integer as cash")

        if additional_cash <= 0:
            return apology("Must provide a positive integer as cash")
        
        # Update user´s cash
        current_cash = db.execute ("SELECT cash FROM users where id = ? LIMIT 1", user_id)[0]["cash"]

        updated_cash = current_cash + additional_cash

        try:
            db.execute("UPDATE users set cash = ? WHERE id = ?", updated_cash, user_id)
        except Exception as e:
            return apology("Error updating cash")
        
        # Return success message
        return render_template("success_cash.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add_cash.html")