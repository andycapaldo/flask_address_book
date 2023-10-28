from app import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import Phonebook, SignUpForm, LoginForm
from app.models import AddressBook, User



@app.route('/')
def index():
    # Shows all entries in the phonebook when user is logged in
    addresses = db.session.execute(db.select(AddressBook)).scalars().all()
    return render_template('index.html', addresses=addresses)


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

        login_user(new_user)
        flash(f"{new_user.username} has been created!")

        # Redirect to the home page
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # LoginForm instance
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data

        # Query the User table for a user with that username
        user = db.session.execute(db.select(User).where(User.username==username)).scalar()
        # Check if there is a user AND the password is correct for that user
        if user is not None and user.check_password(password):
            login_user(user, remember=remember_me)
            # Log the user in via Flask-Login
            flash(f'{user.username} has successfully logged in.')
            return redirect(url_for('index'))
        else:
            flash('Incorrect username and/or password')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out')
    return redirect(url_for('index'))


@app.route('/phonebook', methods=['GET', 'POST'])
@login_required
def phonebook():
    phonebook = Phonebook()
    if phonebook.validate_on_submit():
        first_name = phonebook.first_name.data
        last_name = phonebook.last_name.data
        phone_number = phonebook.phone_number.data
        address = phonebook.address.data

        # Check to make sure we don't get duplicate entries by phone number; assumption is that everyone has a different phone number
        check_book = db.session.execute(db.select(AddressBook).where( (AddressBook.phone_number==phone_number) )).scalars().all()
        if check_book:
            flash('This person is already in the phonebook!')
            return redirect(url_for('phonebook'))
        
        # Create a new instance of the AddressBook class with the data from the form
        new_address = AddressBook(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address, user_id=current_user.id)
        # Add the new entry into the database
        db.session.add(new_address)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('phonebook.html', phonebook=phonebook)


# Route to view a single entry in the phonebook by ID
@app.route('/address/<address_id>')
def address_view(address_id):
    address = db.session.get(AddressBook, address_id)
    if not address:
        flash('That entry does not exist')
        return redirect(url_for('index'))
    return render_template('address.html', address=address)


# Route to edit an AddressBook entry
@app.route('/address/<address_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    address = db.session.get(AddressBook, address_id)
    if not address:
        flash('That entry does not exist!')
        return redirect(url_for('index'))
    if current_user != address.author:
        flash('You can only edit phonebook entries you have created!')
        return redirect(url_for('address_view', address_id=address_id))
    # Create an instance of the PhoneBook form
    form = Phonebook()

    # If the form is submitted, update the post
    if form.validate_on_submit():
        address.first_name = form.first_name.data
        address.last_name = form.last_name.data
        check_phone_number = form.phone_number.data
        # Check to make sure another person in the phonebook doesn't have the same phone number (per the assumption above)

        check_book = db.session.execute(db.select(AddressBook).where( (AddressBook.phone_number==check_phone_number) )).scalars().all()
        if check_book:
            flash('That phone number belongs to another person in the phonebook!')
            return redirect(url_for('address_view', address_id=address_id))
        else:
        # If the phone number doesn't belong to another entry, we can update the rest of the entries successfully
            address.phone_number = form.phone_number.data
            address.address = form.address.data
            # Commit to the db
            db.session.commit()
            flash(f'Entry # {address.id} has been updated!', 'success')
            return redirect(url_for('index'))
    
    # Pre-populate the phonebook entry with the entry's data
    form.first_name.data = address.first_name
    form.last_name.data = address.last_name
    form.phone_number.data = address.phone_number
    form.address.data = address.address
    return render_template('edit_entry.html', address=address, form=form)



# Route for logged-in user to view their entries into the phonebook
@app.route('/profile')
@login_required
def profile():
    addresses = db.session.execute(db.select(AddressBook).where( (AddressBook.user_id == current_user.id))).scalars().all()
    return render_template('profile.html', addresses=addresses)

