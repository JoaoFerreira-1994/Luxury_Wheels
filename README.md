# Luxury Wheels

**Version:** 1.0.0  
**Status:** Final Release  
**Technology:** Python 3, Flask, SQLite

## About the Project

Luxury Wheels is a vehicle rental management system developed in Python as a final course project.

The application provides a web interface for managing vehicles, clients, reservations, and payment methods. It also includes a REST API, user authentication, a dashboard, CSV exports, and application logging.

## Technologies Used

- Python 3
- Flask 3.1.3
- SQLite
- HTML5 and CSS3
- Bootstrap 5
- Jinja2
- Werkzeug
- Git and GitHub

## Features

### User Authentication
- User login and logout
- Session management
- Password hashing
- Access protection for authenticated users

### Vehicle Management
- Create, view, update, and delete vehicles
- Manage vehicle categories, types, and status
- Track revision and inspection dates
- Prevent deletion of vehicles with associated reservations

### Client Management
- Create, view, update, and delete clients
- Store contact information and NIF
- Prevent duplicate NIF values
- Prevent deletion of clients with associated reservations

### Reservation Management
- Create, view, update, and delete reservations
- Validate reservation dates
- Prevent overlapping reservations
- Prevent reservations for vehicles under maintenance
- Calculate rental prices automatically
- Associate clients, vehicles, and payment methods with reservations

### Payment Method Management
- Create, view, update, and delete payment methods
- Prevent duplicate payment method names
- Prevent deletion of payment methods with associated reservations

### Dashboard
- Rented vehicles and remaining rental days
- Recently registered clients
- Available vehicles by category
- Monthly reservation summaries
- Upcoming revision and inspection alerts

### Additional Features
- REST API with JSON responses
- CSV export for all four management modules
- Application logging
- Error handling and data validation
- Responsive interface using Bootstrap

## Project Structure

```text
Luxury_Wheels/
├── app.py
├── database.py
├── models.py
├── requirements.txt
├── README.md
├── .gitignore
├── luxury_wheels/
│   └── Bruno API test files
├── static/
│   ├── css/
│   └── images/
├── templates/
│   ├── includes/
│   └── HTML templates
└── tests/
    ├── test_reservations.py
    └── test_reservation_overlap.py
```

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Luxury_Wheels
```

Replace `<repository-url>` with the GitHub repository URL.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

Before running the application for the first time, initialize the database:

```bash
python database.py
```

This command:

- Creates the SQLite database
- Initializes the required tables
- Creates the default administrator account if it does not already exist

The database contains five main tables:

- `users`
- `vehicles`
- `clients`
- `payment_methods`
- `reservations`

The database file is excluded from version control.

## Administrator Login

Default administrator credentials for local development and testing:

- **Email:** `admin@luxurywheels.com`
- **Password:** `Luxury123`
- **Role:** `admin`

These credentials are intended for educational and local testing purposes only. They must be changed before using the application in a production environment.

## Running the Application

Start the Flask application:

```bash
python app.py
```

Open the following address in your browser:

http://127.0.0.1:5000

Log in using the administrator credentials.

## Automated Tests

The project includes automated tests using Python's `unittest` framework.

Run all tests with:

```bash
python -m unittest discover -s tests -v
```

The test suite covers:

- Invalid clients, vehicles, and payment methods
- Invalid date formats
- Invalid reservation date ranges
- Vehicles under maintenance
- Overlapping reservations
- Successful reservation creation
- Rental price calculations
- Reservation overlap checks using an in-memory SQLite database

**Test results:** 11 tests passed.

## Logging

The application records important events, including:

- Successful and failed login attempts
- User logout
- Record creation, modification, and deletion
- Validation failures
- Database integrity errors

Logs are stored in `luxury_wheels.log`.

The log file is excluded from version control.
