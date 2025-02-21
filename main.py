from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# MongoDB connection URI
MONGODB_URI = "mongodb+srv://HAMZA:1234%235678@cluster0.l2gs9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client.get_database('api_db')  # Database name
    users_collection = db.users  # Collection name
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)  # Exit if connection fails

# Helper function to get all users from the MongoDB collection
def get_all_users():
    try:
        users = users_collection.find()
        all_users = []
        for user in users:
            all_users.append({
                "id": str(user["_id"]),
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "title": user.get("title", "")
            })
        return all_users
    except Exception as e:
        print(f"Error retrieving users: {e}")
        return []

# Helper function to insert a user into MongoDB
def insert_user(user_data):
    try:
        user = users_collection.insert_one(user_data)
        return str(user.inserted_id)
    except Exception as e:
        print(f"Error inserting user: {e}")
        return None

# Helper function to update a user in MongoDB
def update_user_in_db(user_id, updated_data):
    try:
        result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
        return result.matched_count > 0
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

# Helper function to delete a user from MongoDB
def delete_user_from_db(user_id):
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = get_all_users()
        if users:
            return jsonify(users)
        return jsonify({"message": "No users found."}), 404
    except Exception as e:
        print(f"Error in GET /api/users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        new_user = request.get_json()
        new_user_id = insert_user(new_user)
        if new_user_id:
            new_user['id'] = new_user_id
            return jsonify(new_user), 201
        return jsonify({"error": "Failed to add user"}), 400
    except Exception as e:
        print(f"Error in POST /api/users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        updated_data = request.get_json()
        success = update_user_in_db(user_id, updated_data)
        if success:
            return jsonify({"message": "User updated successfully"})
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Error in PUT /api/users/{user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        success = delete_user_from_db(user_id)
        if success:
            return jsonify({"message": f"User with id {user_id} has been deleted"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Error in DELETE /api/users/{user_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)