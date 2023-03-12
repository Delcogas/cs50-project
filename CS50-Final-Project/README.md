# CS50 Fit Story

#### Video Demo:  <https://youtu.be/Qv9i9m31_qI>
#### Description:

CS50 Fit Story´s web page is a Toy Story looking web page designed to book Fitness and Dance classes online.
At first, you will be prompted to enter your user name and your password. If you do not have a username yet,
you should be able to clic the *Register* button located on the upper right side of the web page, in order -
to create your user. Either way, you should be able to log in once entered your user and password, and click
the *register* or *log in* button.
You then will be welcomed to your online session, where you will find all of you classes in a table. If you
do not see any classes, that may be because you haven´t signed up for a class yet. If this is the first time
entering the page, you most likely will figure out not having cash to purchase any class. So first, you may
go to the *Add cash* button on the upper left side of your screen. As for this CS50 Course, we did not manage
to work with real money, or a credit card for example, so in this case we will simply type how much money is
wanted in our user, and then clic *add*.
Once we have enough money to purchase a class, we may go to the *Sign up for a class* button, also located in
the upper side part of the screen. We would be able to select the type of class (if a fitness class is
needed, or a dance class), the week day and time desired before *Signing up* to the class. After clicking  
the *Sign up* button, you should be seeing a succesful message, if all went well. If your user does not have # enough money, an unsuccesful message should be telling you to add more money to your account and try again.
After that, clicking on *CS50 FIT Story* or *My Classes* should let you see a table with that first class
saved. You can choice to sign up for as many classes as you want, as long as there is enough money to 
purchase them. If, for some reason, you would like to deregister from a signed up class, you should clic on
the *deregister* button next to that specific class that you wish to cancel. After deregistering from a 
class, you should see a successfull message from deregistering (teacher will not be so happy though) and
two things would happen: the class will no longer show in the table with your classes, and the money should
be refunded to your account.
After registering to all your wanted classes, you may want to Log out you from you account, by clicking the
*Log Out* button located in the upper right side of your screen.
###### How does the backend of the page work?
Using Flask, Javascript, Python and SQL, this web application keeps track of users names, classes,
transactions and more in order to have an ordered web page showing the signed up classes for every user.
Inside CS50´s Final Project foulder, there is a *static* foulder with some images, gifs and icons used
for the frontend of the page. A *templates* foulder with all the html pages used in the web application.
A file named app.py, where the app per se lives in python, a *classes.db* file, the sqlite3 database
with tables in order to save all the information going on every time users interact with the page,
a *helpers.py* file with some additional functions in order to make the programming of the page easier,
and a *requirements.txt* file.
classes.db has tables such as *users*, which keeps track of the user´s id, name, password hash and their
cash; *transactions*, that keeps track of every sign up, deregistration, money moving from and to the users # account, date of the transcation and of course the user involved; and *classes*, that has the prices for
fitness and dance classes.
In order to make the app work, there are different functions using methods GET and POST, in order to protect
users information. The *index* function uses current session in order to work with the user that signed in,
then searchs for all the transactions created for that specific user using the classes.db database, in order
to have all the classes saved in the *classes* variable, and lastly searchs for the user´s cash in the cash
table from the classes.db database, and saves it in the *current_cash* variable. At the end, the index
function renders the index.html page, considering the classes and cash the users has. In order to understand
index.html, we need to know that all the pages are extensions of layout.html, that has buttons, background
and some other features that are common to the whole web page. Extending layout.html using jinja syntax,
index.html shows a welcome message and a table showing all the classes, created with for loop.
Inside app.py, after the index function, we have a login function that first of all forgets any user session.
This functon accepts both GET and POST methods and when submitting via POST, after inserting name and
password, the login functions checks if the name and password entered matches an existing name and password
inside the user´s database. If it does, you will be redirected to your user information, classes and cash.
Basically the "/" route seen in the index function, and the index.html web page.
But if it doesn´t, an error message will appear letting you know that either the user does not exist, or the 
password was wrong. Of course, there are some safety checks, such as an error message letting you know if 
no password or name at all was entered. If the users enters the login route via GET, login.html will show up
asking you to enter the name an password.
After that, we see a logout function in the app.py file. This function runs when the user clicks the
*Log out* button. It simply forgets the session and redirects the user to the / route.
The *register* function, checks if the users enters name, password, and again the password to make sure no 
typos are written. The functions lets you know if you forgot to type any field, and also checks if the
username already exists. If the user name is valid, a new row will be added to the users table in classes.db,
with the name and a password hash. Finally, to make it user friendly, the user will be redirected to
index.html, already signed in for the first time.
The *sign up* function also works with GET and POST methods. If reached to the */sign_up* route via GET,
user will be redirected to sign_up.html, asking for the name and password. But if reached the route
via POST, that is, by clicking the submit button, the function checks if the user and password registered
matches an existing user in the users table. If it does, you will log in and see the index.html page with
all the information for that user.
The *deregister* function only works with the POST method. If the users wants to cancel a class, clicking
the deregister button will check for the class_id, a unique number for that class, and delete it from the
user, returning also the money back to their account by interacting with the cash and transaction tables.
The *add_cash* function also works with the GET and POST methods. If reached via GET, user will be promted
to add the amount of cash desired. If reached via POST, by clicking the add button, that cash will be
added to the users account in the users table, as long as the user enters a positive integer value.
The frontend of the page uses Toy Story related letters, background images, GIF files,
and more just to make it look nicer, and to have fun with a part of my childhood during this final project.
Most of the front end was created using Bootstrap and some of the features from CS50´s Finance problem set.
Finally, GIF´s where all taken from *https://giphy.com*.
