from app import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import Phonebook, SignUpForm
from app.models import AddressBook, User



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check to see if we already have a User with that username or email
        check_user = db.session.execute(db.select(User).where( (User.username==username) | (User.email==email) )).scalars().all()
        if check_user:
            flash('A user with that username and/or email already exists')
            return redirect(url_for('signup'))
        
        new_user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the home page
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)

@app.route('/phonebook', methods=['GET', 'POST'])
def phonebook():
    phonebook = Phonebook()
    if phonebook.validate_on_submit():
        first_name = phonebook.first_name.data
        last_name = phonebook.last_name.data
        phone_number = phonebook.phone_number.data
        address = phonebook.address.data

        # Check to make sure we don't get duplicate entries by phone number; assumption is that everyone has a different phone number (home numbers are extremely rare these days)
        check_book = db.session.execute(db.select(AddressBook).where( (AddressBook.phone_number==phone_number) )).scalars().all()
        if check_book:
            flash('This person is already in the phonebook!')
            return redirect(url_for('phonebook'))
        
        # Create a new instance of the AddressBook class with the data from the form
        new_address = AddressBook(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address)
        # Add the new entry into the database
        db.session.add(new_address)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('phonebook.html', phonebook=phonebook)