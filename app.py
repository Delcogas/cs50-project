import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

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
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    """Show portfolio of stocks"""
    # Use current session
    user_id = session["user_id"]

    # Search for transactions created by current user
    historic_transactions = db.execute(
        "SELECT symbol, SUM(shares) AS shares, price, SUM(price*shares) as total_value FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)

    # Store current cash in variable
    total_cash = db.execute("SELECT cash FROM users WHERE id = ? ", user_id)

    # Add total cash
    cash = total_cash[0]["cash"]

    total = cash

    # Add sum of cash plus stocks values
    for transaction in historic_transactions:
        total += transaction["total_value"]

    return render_template("index.html", summary=historic_transactions, cash=cash, total=total, usd=usd)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol")

        symbol = request.form.get("symbol")

        # Ensure shares were submitted
        if not request.form.get("shares"):
            return apology("must provide shares")

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("must provide a positive integer share")

        if shares <= 0:
            return apology("must provide a positive integer share")

        if not lookup(symbol.upper()):
            return apology("provided symbol does not exist")

        stock = lookup(symbol.upper())

        user_id = session["user_id"]
        current_cash = db.execute("SELECT cash FROM users WHERE id = ? ", user_id)
        transaction_value = shares * stock["price"]

        user_cash = current_cash[0]["cash"]
        if transaction_value > user_cash:
            return apology("Not Enough money to buy")

        updated_cash = user_cash - transaction_value

        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        transaction_date = datetime.datetime.now()

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES(?, ?, ?, ?, ?)",
                   user_id, stock["symbol"], shares, stock["price"], transaction_date)

        flash("Purchased!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transaction_history = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    return render_template("history.html", transactions=transaction_history)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Personal touch: Add the possibility of adding extra cash"""
    if request.method == "POST":

        if not request.form.get("add_cash"):
            return apology("Must add cash")
        add_cash = int(request.form.get("add_cash"))

        user_id = session["user_id"]

        current_user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        updated_cash = current_user_cash + add_cash

        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        return redirect("/")

    return render_template("add_cash.html")


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
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol")

        symbol = request.form.get("symbol")

        stock = lookup(symbol.upper())

        if not stock:
            return apology("provided symbol does not exist")

        return render_template("quoted.html", name=stock["name"], price=stock["price"], symbol=stock["symbol"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted

        symbol = request.form.get("symbol")
        if not symbol or symbol == "Choose stock to sell":
            return apology("must provide symbol")

        # Ensure shares were submitted
        if not request.form.get("shares"):
            return apology("must provide shares")

        shares = int(request.form.get("shares"))

        if shares <= 0:
            return apology("must provide a positive integer share")

        if not lookup(symbol.upper()):
            return apology("provided symbol does not exist")

        user_id = session["user_id"]
        user_stocks = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)[0]["symbol"]
        user_shares = db.execute("SELECT shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id,
                                 symbol)[0]["shares"]

        if user_shares < shares:
            return apology("You do not own as many shares")

        current_cash = db.execute("SELECT cash FROM users WHERE id = ? ", user_id)[0]["cash"]
        stock = lookup(symbol.upper())
        transaction_value = shares * stock["price"]

        updated_cash = current_cash + transaction_value

        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        transaction_date = datetime.datetime.now()

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES(?, ?, ?, ?, ?)",
                   user_id, stock["symbol"], (-1)*shares, stock["price"], transaction_date)

        flash("Sold!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    user_id = session["user_id"]
    user_stocks = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
    return render_template("sell.html", symbols=[row["symbol"] for row in user_stocks])
