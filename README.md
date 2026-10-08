## Database Setup

Before running the application for the first time, initialize the database:

```bash
python database.py
```

This command creates the SQLite database, initializes the required tables, and creates the default administrator account if it does not already exist.

## Administrator Login

Default administrator credentials for local development and testing:

- **Email:** `admin@luxurywheels.com`
- **Password:** `Luxury123`
- **Role:** `admin`

These credentials are intended for educational and local testing purposes only.

## Running the Application

Start the Flask application:

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.