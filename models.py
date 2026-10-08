from database import connect
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash


# ----------------------------------------------------------------------------- USERS ----------------------------------------------------------------

def create_user(name, email, password, role):

    """Creates a new user and returns the generated ID."""

    conn = connect()
    password_hash = generate_password_hash(password)

    cursor = conn.execute("""
        INSERT INTO users (
            name,
            email,
            password,
            role
        )
        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        password_hash,
        role
    ))

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return user_id


def find_user_by_email(email):

    """Returns a user by email."""

    conn = connect()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if user: return dict(user)

    return None


def authenticate_user(email, password):

    """Authenticates a user using email and password."""

    user = find_user_by_email(email)

    if not user: return None
    if not check_password_hash(user["password"], password): return None

    return user


# ----------------------------------------------------------------------------- VEHICLES ----------------------------------------------------------------

def list_vehicles():

    """Returns all vehicles."""

    conn = connect()
    vehicles = conn.execute("SELECT * FROM vehicles").fetchall()
    conn.close()

    return [dict(vehicle) for vehicle in vehicles]


def create_vehicle(brand, model, license_plate, category, transmission,
                   vehicle_type, capacity, image_path, daily_price,
                   last_revision_date, next_revision_date,
                   last_inspection_date, next_inspection_date, status):

    """Creates a new vehicle and returns the ID."""

    conn = connect()
    cursor = conn.execute("""
        INSERT INTO vehicles (
            brand,
            model,
            license_plate,
            category,
            transmission,
            vehicle_type,
            capacity,
            image_path,
            daily_price,
            last_revision_date,
            next_revision_date,
            last_inspection_date,
            next_inspection_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        brand,
        model,
        license_plate,
        category,
        transmission,
        vehicle_type,
        capacity,
        image_path,
        daily_price,
        last_revision_date,
        next_revision_date,
        last_inspection_date,
        next_inspection_date,
        status
    ))

    conn.commit()
    vehicle_id = cursor.lastrowid
    conn.close()

    return vehicle_id


def find_vehicle(vehicle_id):

    """Returns a vehicle by its ID."""

    conn = connect()
    vehicle = conn.execute(
        "SELECT * FROM vehicles WHERE id = ?",
        (vehicle_id,)
    ).fetchone()

    conn.close()
    if vehicle: return dict(vehicle)

    return None


def update_vehicle(vehicle_id, brand, model, license_plate, category,
                   transmission, vehicle_type, capacity, image_path,
                   daily_price, last_revision_date, next_revision_date,
                   last_inspection_date, next_inspection_date, status):
    
    """Updates a vehicle."""

    conn = connect()
    cursor = conn.execute("""
        UPDATE vehicles
        SET brand = ?,
            model = ?,
            license_plate = ?,
            category = ?,
            transmission = ?,
            vehicle_type = ?,
            capacity = ?,
            image_path = ?,
            daily_price = ?,
            last_revision_date = ?,
            next_revision_date = ?,
            last_inspection_date = ?,
            next_inspection_date = ?,
            status = ?
        WHERE id = ?
    """, (
        brand,
        model,
        license_plate,
        category,
        transmission,
        vehicle_type,
        capacity,
        image_path,
        daily_price,
        last_revision_date,
        next_revision_date,
        last_inspection_date,
        next_inspection_date,
        status,
        vehicle_id
    ))

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return affected_rows


def delete_vehicle(vehicle_id):

    """Deletes a vehicle."""

    conn = connect()
    cursor = conn.execute(
        "DELETE FROM vehicles WHERE id = ?",
        (vehicle_id,)
    )

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return affected_rows

def vehicle_has_reservations(vehicle_id):
    """Checks if a vehicle has associated reservations."""

    conn = connect()

    reservation = conn.execute(
        "SELECT id FROM reservations WHERE vehicle_id = ? LIMIT 1",
        (vehicle_id,)
    ).fetchone()

    conn.close()

    return reservation is not None


# ----------------------------------------------------------------------------- CLIENTS ----------------------------------------------------------------

def list_clients():

    """Returns all clients."""

    conn = connect()
    clients = conn.execute(
        "SELECT * FROM clients"
    ).fetchall()

    conn.close()

    return [dict(client) for client in clients]


def find_client(client_id):

    """Returns a client by its ID."""

    conn = connect()
    client = conn.execute(
        "SELECT * FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    conn.close()

    if client:
        return dict(client)

    return None

def create_client(name, nif, email, phone, address):

    """Creates a new client."""

    conn = connect()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.execute("""
        INSERT INTO clients (
            name,
            nif,
            email,
            phone,
            address,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        nif,
        email,
        phone,
        address,
        created_at
    ))

    conn.commit()
    client_id = cursor.lastrowid
    conn.close()

    return client_id

def update_client(client_id, name, nif, email, phone, address):

    """Updates a client"""

    conn = connect()
    cursor = conn.execute("""
        UPDATE clients
        SET name = ?,
            nif = ?,
            email = ?,
            phone = ?,
            address = ?
        WHERE id = ?
    """, (
        name,
        nif,
        email,
        phone,
        address,
        client_id
    ))

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return affected_rows

def delete_client(client_id):
    """Deletes a client and returns the number of affected rows."""

    conn = connect()
    cursor = conn.execute(
        "DELETE FROM clients WHERE id = ?",
        (client_id,)
    )

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return affected_rows

def client_has_reservations(client_id):
    """Checks if a client has associated reservations."""

    conn = connect()

    reservation = conn.execute(
        "SELECT id FROM reservations WHERE client_id = ? LIMIT 1",
        (client_id,)
    ).fetchone()

    conn.close()

    return reservation is not None


# ----------------------------------------------------------------------------- PAYMENT METHODS ----------------------------------------------------------------

def list_payment_methods():

    """Returns all payment methods"""

    conn = connect()
    payment_methods = conn.execute(
        "SELECT * FROM payment_methods"
    ).fetchall()

    conn.close()

    return [dict(payment_method) for payment_method in payment_methods]


def find_payment_method(payment_method_id):

    """Returns a payment method by its ID."""

    conn = connect()

    payment_method = conn.execute(
        "SELECT * FROM payment_methods WHERE id = ?",
        (payment_method_id,)
    ).fetchone()

    conn.close()
    if payment_method:
        return dict(payment_method)

    return None


def create_payment_method(name):

    """Creates a new payment method"""

    conn = connect()
    cursor = conn.execute(
        "INSERT INTO payment_methods (name) VALUES (?)",
        (name,)
    )

    conn.commit()
    payment_method_id = cursor.lastrowid
    conn.close()

    return payment_method_id


def update_payment_method(payment_method_id, name):

    """Updates a payment method."""

    conn = connect()
    cursor = conn.execute(
        "UPDATE payment_methods SET name = ? WHERE id = ?",
        (name, payment_method_id)
    )

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return affected_rows


def delete_payment_method(payment_method_id):
    """Deletes a payment method and returns the number of affected rows."""

    conn = connect()
    cursor = conn.execute(
        "DELETE FROM payment_methods WHERE id = ?",
        (payment_method_id,)
    )

    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()

    return affected_rows

def payment_method_has_reservations(payment_method_id):
    """Checks if a payment method has associated reservations."""

    conn = connect()

    reservation = conn.execute(
        "SELECT id FROM reservations WHERE payment_method_id = ? LIMIT 1",
        (payment_method_id,)
    ).fetchone()

    conn.close()

    return reservation is not None


# ----------------------------------------------------------------------------- RESERVATIONS ----------------------------------------------------------------


def list_reservations():
    """Returns all reservations with related information."""

    conn = connect()

    reservations = conn.execute("""
        SELECT
            reservations.id,
            clients.name AS client,
            vehicles.brand || ' ' || vehicles.model AS vehicle,
            payment_methods.name AS payment_method,
            reservations.start_date,
            reservations.end_date,
            reservations.daily_price,
            reservations.total_price,
            reservations.status,
            reservations.created_at
        FROM reservations
        JOIN clients
            ON reservations.client_id = clients.id
        JOIN vehicles
            ON reservations.vehicle_id = vehicles.id
        JOIN payment_methods
            ON reservations.payment_method_id = payment_methods.id
    """).fetchall()

    conn.close()

    return [dict(reservation) for reservation in reservations]


# Replaces IDs with client, vehicle, and payment method details
def get_reservation_details(reservation_id):
    """Returns a reservation with related information."""

    conn = connect()

    reservation = conn.execute("""
        SELECT
            reservations.id,
            clients.name AS client,
            vehicles.brand || ' ' || vehicles.model AS vehicle,
            payment_methods.name AS payment_method,
            reservations.start_date,
            reservations.end_date,
            reservations.daily_price,
            reservations.total_price,
            reservations.status,
            reservations.created_at
        FROM reservations
        JOIN clients
            ON reservations.client_id = clients.id
        JOIN vehicles
            ON reservations.vehicle_id = vehicles.id
        JOIN payment_methods
            ON reservations.payment_method_id = payment_methods.id
        WHERE reservations.id = ?
    """, (reservation_id,)).fetchone()

    conn.close()

    if reservation:
        return dict(reservation)

    return None


def find_reservation(reservations_id):

    """Returns a reservations by its ID."""

    conn = connect()

    reservations = conn.execute(
        "SELECT * FROM reservations WHERE id = ?",
        (reservations_id,)
    ).fetchone()

    conn.close()
    if reservations:
        return dict(reservations)

    return None


def create_reservation(
    client_id,
    vehicle_id,
    payment_method_id,
    start_date,
    end_date
):
    """Creates a new reservation."""

    client = find_client(client_id)
    if not client: return {"error": "Client not found."}

    vehicle = find_vehicle(vehicle_id)
    if not vehicle: return {"error": "Vehicle not found."}

    payment_method = find_payment_method(payment_method_id)

    if not payment_method: return {"error": "Payment method not found."}

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

    except ValueError: return {"error": "Invalid date format. Use YYYY-MM-DD."}

    if end <= start: return {"error": "End date must be after start date."}

    # Show days until the end of the rental
    rental_days = (end - start).days

    # Vehicle under maintenance can´t be rental
    if vehicle["status"] == "maintenance":return {"error": "Vehicle is under maintenance."}

    conn = connect()

    existing_reservation = conn.execute("""
        SELECT * FROM reservations
        WHERE vehicle_id = ?
        AND status != 'cancelled'
        AND start_date < ?
        AND end_date > ?
    """, (
        vehicle_id,
        end_date,
        start_date
    )).fetchone()

    if existing_reservation:
        conn.close()
        return {"error": "Vehicle is already reserved for these dates."}

    # Fixed value . set when the vehicle is created
    daily_price = vehicle["daily_price"]

    total_price = rental_days * daily_price

    status = "confirmed"

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.execute("""
        INSERT INTO reservations (
            client_id,
            vehicle_id,
            payment_method_id,
            start_date,
            end_date,
            daily_price,
            total_price,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client_id,
        vehicle_id,
        payment_method_id,
        start_date,
        end_date,
        daily_price,
        total_price,
        status,
        created_at
    ))

    conn.commit()

    reservation_id = cursor.lastrowid

    conn.close()

    return {
        "id": reservation_id,
        "total_price": total_price
    }

def delete_reservation(reservation_id):
    """Deletes a reservation and returns the number of affected rows."""

    conn = connect()

    cursor = conn.execute(
        "DELETE FROM reservations WHERE id = ?",
        (reservation_id,)
    )

    conn.commit()

    affected_rows = cursor.rowcount

    conn.close()

    return affected_rows


def update_reservation(
    reservation_id,
    client_id,
    vehicle_id,
    payment_method_id,
    start_date,
    end_date
):
    """Updates an existing reservation."""

    client = find_client(client_id)

    if not client: return {"error": "Client not found."}
    vehicle = find_vehicle(vehicle_id)

    if not vehicle: return {"error": "Vehicle not found."}
    payment_method = find_payment_method(payment_method_id)

    if not payment_method: return {"error": "Payment method not found."}

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

    except ValueError: return {"error": "Invalid date format. Use YYYY-MM-DD."}

    if end <= start: return {"error": "End date must be after start date."}

    rental_days = (end - start).days

    if vehicle["status"] == "maintenance": return {"error": "Vehicle is under maintenance."}

    conn = connect()

    # id != ? -> Ignores the reservation being updated to avoid a conflict with itself 
    existing_reservation = conn.execute("""
        SELECT * FROM reservations
        WHERE vehicle_id = ?
        AND id != ?
        AND status != 'cancelled'
        AND start_date < ?
        AND end_date > ?
    """, (
        vehicle_id,
        reservation_id,
        end_date,
        start_date
    )).fetchone()

    if existing_reservation:
        conn.close()
        return {"error": "Vehicle is already reserved for these dates."}

    daily_price = vehicle["daily_price"]

    total_price = rental_days * daily_price

    cursor = conn.execute("""
        UPDATE reservations
        SET client_id = ?,
            vehicle_id = ?,
            payment_method_id = ?,
            start_date = ?,
            end_date = ?,
            daily_price = ?,
            total_price = ?
        WHERE id = ?
    """, (
        client_id,
        vehicle_id,
        payment_method_id,
        start_date,
        end_date,
        daily_price,
        total_price,
        reservation_id
    ))

    conn.commit()

    affected_rows = cursor.rowcount

    conn.close()

    return {
        "affected_rows": affected_rows,
        "total_price": total_price
    }


# ----------------------------------------------------------------------------- DASHBOARD ----------------------------------------------------------------

def get_rented_vehicles():

    """Returns currently rented vehicles and their remaining rental days."""

    conn = connect()
    today = datetime.now().strftime("%Y-%m-%d")

    reservations = conn.execute("""
        SELECT
            vehicles.brand || ' ' || vehicles.model AS vehicle,
            clients.name AS client,
            reservations.start_date,
            reservations.end_date
        FROM reservations
        JOIN vehicles
            ON reservations.vehicle_id = vehicles.id
        JOIN clients
            ON reservations.client_id = clients.id
        WHERE reservations.status != 'cancelled'
        AND reservations.start_date <= ?
        AND reservations.end_date >= ?
    """, (today, today)).fetchall()

    conn.close()
    rented_vehicles = []

    for reservation in reservations:

        end_date = datetime.strptime(
            reservation["end_date"],
        "%Y-%m-%d"
    )

        remaining_days = (
            end_date - datetime.strptime(today, "%Y-%m-%d")
        ).days

        vehicle = dict(reservation)
        vehicle["remaining_days"] = remaining_days

        rented_vehicles.append(vehicle)

    return rented_vehicles


def get_latest_clients():

    """Returns the latest registered clients."""

    conn = connect()

    clients = conn.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            created_at
        FROM clients
        ORDER BY created_at DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return [dict(client) for client in clients]


def get_available_vehicles_by_category():

    """Returns the number of available vehicles grouped by category."""

    conn = connect()
    vehicles = conn.execute("""
        SELECT
            category,
            COUNT(*) AS total
        FROM vehicles
        WHERE status = 'available'
        GROUP BY category
        ORDER BY category
    """).fetchall()

    conn.close()

    return [dict(vehicle) for vehicle in vehicles]


def get_monthly_reservations_summary():

    """Returns the number of reservations and total revenue for the current month."""

    conn = connect()
    current_month = datetime.now().strftime("%Y-%m")

    summary = conn.execute("""
        SELECT
            COUNT(*) AS total_reservations,
            COALESCE(SUM(total_price), 0) AS total_revenue
        FROM reservations
        WHERE start_date LIKE ?
        AND status != 'cancelled'
    """, (current_month + "%",)).fetchone()

    conn.close()

    return dict(summary)


def get_upcoming_revisions():

    """Returns vehicles with revisions due within the next 15 days."""

    conn = connect()
    today = datetime.now().strftime("%Y-%m-%d")
    limit_date = (
        datetime.now() + timedelta(days=15)
    ).strftime("%Y-%m-%d")

    vehicles = conn.execute("""
        SELECT
            id,
            brand,
            model,
            license_plate,
            next_revision_date
        FROM vehicles
        WHERE next_revision_date BETWEEN ? AND ?
        ORDER BY next_revision_date
    """, (today, limit_date)).fetchall()

    conn.close()

    return [dict(vehicle) for vehicle in vehicles]


def get_upcoming_inspections():

    """Returns vehicles with inspections due within the next 15 days."""

    conn = connect()
    today = datetime.now().strftime("%Y-%m-%d")
    limit_date = (
        datetime.now() + timedelta(days=15)
    ).strftime("%Y-%m-%d")

    vehicles = conn.execute("""
        SELECT
            id,
            brand,
            model,
            license_plate,
            next_inspection_date
        FROM vehicles
        WHERE next_inspection_date BETWEEN ? AND ?
        ORDER BY next_inspection_date
    """, (today, limit_date)).fetchall()

    conn.close()

    return [dict(vehicle) for vehicle in vehicles]


def get_revision_alerts():

    """Returns vehicles with revisions due within the next 5 days."""

    conn = connect()
    today = datetime.now().strftime("%Y-%m-%d")
    alert_date = (
        datetime.now() + timedelta(days=5)
    ).strftime("%Y-%m-%d")

    vehicles = conn.execute("""
        SELECT
            id,
            brand,
            model,
            license_plate,
            next_revision_date
        FROM vehicles
        WHERE next_revision_date BETWEEN ? AND ?
        ORDER BY next_revision_date
    """, (today, alert_date)).fetchall()

    conn.close()

    return [dict(vehicle) for vehicle in vehicles]

if __name__ == "__main__":

    alerts = get_revision_alerts()

    for alert in alerts:
        print(alert)