from app import app, init_db

print("Initializing database from main.py...")
init_db()
print("Starting application from main.py...")
app.run(host='0.0.0.0', port=8080, debug=True)