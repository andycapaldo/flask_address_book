from flask import request
from . import api
from app import db
from app.models import AddressBook


# Endpoint to get all addresses
@api.route('/addresses', methods=['GET'])
def get_addresses():
    addresses = db.session.execute(db.select(AddressBook)).scalars().all()
    return [address.to_dict() for address in addresses]


# Endpoint to get an address by ID
@api.route('/addresses/<address_id>')
def get_address(address_id):
    address = db.session.get(AddressBook, address_id)
    if not address:
        return {'error': f"Address with an ID of {address_id} does not exist"}, 404
    return address.to_dict()


# Endpoint to create a new address
@api.route('/addresses', methods=['POST'])
def create_address():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate incoming data
    required_fields = ['first_name', 'last_name', 'phone_number', 'address']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        if missing_fields:
            return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
        
    # Get data from the request
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    address = data.get('address')

    # Create a new address to add to the database of addresses in our book!
    new_address = AddressBook(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address)
    db.session.add(new_address)
    db.session.commit()
    return new_address.to_dict(), 201