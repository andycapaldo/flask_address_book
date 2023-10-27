from app import app, db
from flask import render_template, redirect, url_for, flash
from app.forms import Phonebook
from app.models import AddressBook



@app.route('/')
def index():
    return render_template('index.html')


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