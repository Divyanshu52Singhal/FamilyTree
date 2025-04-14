# 🧬 Family Tree Web App

This is a **Flask-based web application** that allows users to **create and visualize family trees**. Users can add people, assign parent-child relationships, categorize surnames by colors, and view the entire structure in a clean hierarchical view.

## 🌐 Features

- Add new people with optional parent linkage to create a tree structure.
- Assign a surname and optional color code to each surname.
- Visualize the family tree hierarchically from root ancestors down.
- Edit and delete people from the tree.
- API endpoint to retrieve tree data in JSON format.
- Dynamically assign colors to nodes based on surname categories.

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/family-tree-app.git
cd family-tree-app
```
### 2.  Install dependencies
```
pip install -r requirements.txt
```

### 3. Create a .env file
To run the app locally, you need to store your MongoDB URI in a .env file in the root directory of the project.

Example .env:

```
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/family_tree
```
Replace <username>, <password> with your actual MongoDB connection information.

### 4. Run the app
```
python app.py
```
Open your browser and navigate to http://localhost:5000 to use the app.

# 🤝 Contributing

Pull requests are welcome! If you want to improve features or fix bugs, feel free to fork the repo and make a PR.