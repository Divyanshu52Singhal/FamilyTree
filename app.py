from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=".env")
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# Helper function to convert ObjectId to string in documents
def convert_objectid_to_str(document):
    if document is None:
        return None
        
    document_copy = document.copy()
    if '_id' in document_copy:
        document_copy['_id'] = str(document_copy['_id'])
    if 'parent_id' in document_copy and document_copy['parent_id']:
        document_copy['parent_id'] = str(document_copy['parent_id'])
    return document_copy

@app.route('/')
def index():
    """Render the main page with the family tree."""
    # Get all people from the database
    people = list(mongo.db.people.find())
    surnames = list(mongo.db.surnames.find())
    
    # Convert ObjectId to string for JSON serialization
    people = [convert_objectid_to_str(p) for p in people]
    surnames = [convert_objectid_to_str(s) for s in surnames]
    
    # Build the tree structure
    def build_family_tree(person_id):
        children = [p for p in people if p.get('parent_id') == person_id]
        try:
            person = next(p for p in people if p['_id'] == person_id)
            return {
                'person': person,
                'children': [build_family_tree(child['_id']) for child in children]
            }
        except StopIteration:
            return None
    
    # Find root nodes (people without parents)
    roots = [p for p in people if not p.get('parent_id')]
    family_trees = [build_family_tree(root['_id']) for root in roots if root]
    
    return render_template('index.html', family_trees=family_trees, people=people, surnames=surnames)

@app.route('/api/tree_data')
def tree_data():
    """API endpoint to get the tree data in JSON format."""
    people = list(mongo.db.people.find())
    surnames = list(mongo.db.surnames.find())
    
    # Convert ObjectId to string for JSON serialization
    people = [convert_objectid_to_str(p) for p in people]
    surnames = [convert_objectid_to_str(s) for s in surnames]
    
    # Create a dictionary mapping surname to color
    surname_colors = {s['surname']: s['color'] for s in surnames}
    
    # Attach color information to people based on their surname
    for person in people:
        if person.get('surname') in surname_colors:
            person['color'] = surname_colors[person['surname']]
        else:
            person['color'] = "#000000"  # Default color if surname not found
    
    return jsonify({
        'people': people,
        'surnames': surnames
    })

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    """Add a new person to the family tree."""
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        parent_id = request.form.get('parent_id')
        
        # Convert empty string to None for parent_id
        if parent_id == '':
            parent_id = None
        else:
            parent_id = ObjectId(parent_id)
        
        # Insert the new person into the database
        mongo.db.people.insert_one({
            'name': name,
            'surname': surname,
            'parent_id': parent_id
        })
        
        return redirect(url_for('index'))
    
    # If GET request, show the form with existing people as potential parents
    people = list(mongo.db.people.find())
    surnames = list(mongo.db.surnames.find())
    
    # Convert ObjectId to string for JSON serialization
    people = [convert_objectid_to_str(p) for p in people]
    surnames = [convert_objectid_to_str(s) for s in surnames]
    
    return render_template('add_person.html', people=people, surnames=surnames)

@app.route('/add_surname', methods=['GET', 'POST'])
def add_surname():
    """Add a new surname category with color."""
    if request.method == 'POST':
        surname = request.form.get('surname')
        color = request.form.get('color')
        
        # Insert the new surname into the database
        mongo.db.surnames.insert_one({
            'surname': surname,
            'color': color
        })
        
        return redirect(url_for('index'))
    
    return render_template('add_surname.html')


@app.route('/delete_person/<person_id>', methods=['POST'])
def delete_person(person_id):
    """Delete a person from the family tree."""
    # First, update any children to remove this parent
    mongo.db.people.update_many(
        {'parent_id': ObjectId(person_id)},
        {'$set': {'parent_id': None}}
    )
    
    # Then delete the person
    mongo.db.people.delete_one({'_id': ObjectId(person_id)})
    
    return redirect(url_for('index'))

@app.route('/edit_person/<person_id>', methods=['GET', 'POST'])
def edit_person(person_id):
    """Edit a person's details."""
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        parent_id = request.form.get('parent_id')
        
        # Convert empty string to None for parent_id
        if parent_id == '':
            parent_id = None
        else:
            parent_id = ObjectId(parent_id)
        
        # Update the person in the database
        mongo.db.people.update_one(
            {'_id': ObjectId(person_id)},
            {'$set': {
                'name': name,
                'surname': surname,
                'parent_id': parent_id
            }}
        )  
        return redirect(url_for('index'))
    
    # GET request - show edit form with current values
    person = mongo.db.people.find_one({'_id': ObjectId(person_id)})
    if not person:
        return redirect(url_for('index'))
    
    # Get all other people for parent selection
    people = list(mongo.db.people.find({'_id': {'$ne': ObjectId(person_id)}}))
    surnames = list(mongo.db.surnames.find())
    
    # Convert ObjectIds to strings
    person = convert_objectid_to_str(person)
    people = [convert_objectid_to_str(p) for p in people]
    surnames = [convert_objectid_to_str(s) for s in surnames]
    
    return render_template('edit_person.html', 
                         person=person, 
                         people=people, 
                         surnames=surnames)

if __name__ == '__main__':
    app.run(debug=True)