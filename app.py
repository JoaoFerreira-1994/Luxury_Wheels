from flask import Flask, jsonify, request, session, render_template, redirect, url_for, Response

from models import list_vehicles, find_vehicle, create_vehicle, update_vehicle, delete_vehicle, vehicle_has_reservations
from models import list_clients, find_client, create_client, update_client, delete_client, client_has_reservations
from models import list_payment_methods, find_payment_method, create_payment_method, update_payment_method, delete_payment_method, payment_method_has_reservations
from models import list_reservations, find_reservation, create_reservation, update_reservation, get_reservation_details, delete_reservation
from models import authenticate_user
from models import get_rented_vehicles, get_latest_clients, get_available_vehicles_by_category, get_monthly_reservations_summary, get_upcoming_revisions, get_upcoming_inspections, get_revision_alerts

import csv
import io
import logging
import sqlite3

app = Flask(__name__)

# -------------------- LOGGING CONFIGURATION --------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="luxury_wheels.log",
    encoding="utf-8"
)

app.secret_key = "luxury-wheels-secret-key"


# ----------------------------------------------------------------------------- LOGIN ----------------------------------------------------------------

@app.route("/login-page", methods=["POST"])
def login_page():

    """Authenticates a user from the login form."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = authenticate_user(email, password)

    if not user:
        logging.warning("Failed login attempt.")
        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_role"] = user["role"]

    logging.info("User logged in successfully.")

    return redirect(url_for("dashboard_page"))


@app.route("/logout", methods=["POST"])
def logout():
    """Logs out the current user."""

    session.clear()

    return jsonify({
        "message": "Logout successful."
    }), 200


@app.route("/login", methods=["POST"])
def login():

    """Authenticates a user."""

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing data."}), 400

    required_fields = [
        "email",
        "password"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}."}), 400

    user = authenticate_user(
        data["email"],
        data["password"]
    )

    if not user: return jsonify({"error": "Invalid email or password."}), 401

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_role"] = user["role"]

    return jsonify({
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200

# ----------------------------------------------------------------------------- LOGOUT ----------------------------------------------------------------

@app.route("/logout-page", methods=["GET"])
def logout_page():

    """Logs out the current user and returns to the login page."""

    logging.info("User logged out.")

    session.clear()

    return redirect(url_for("home"))

# ----------------------------------------------------------------------------- CLIENTS ----------------------------------------------------------------

@app.route("/clients-page", methods=["GET"])
def clients_page():
    """Displays the clients management page."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    clients = list_clients()

    return render_template(
        "clients.html",
        user_name=session["user_name"],
        clients=clients
    )

@app.route("/clients/add", methods=["GET", "POST"])
def add_client_page():

    """Displays the form and creates a new client."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        try:
            client_id = create_client(
                request.form.get("name"),
                request.form.get("nif"),
                request.form.get("email"),
                request.form.get("phone"),
                request.form.get("address")
            )

            logging.info(
                "Client created successfully. ID: %s",
                client_id
            )

            return redirect(url_for("clients_page"))

        except sqlite3.IntegrityError:
            logging.warning(
                "Client creation failed. Duplicate NIF."
            )

    return render_template(
        "client_form.html",
        user_name=session["user_name"]
    )

@app.route("/clients/delete/<int:client_id>", methods=["POST"])
def delete_client_page(client_id):

    """Deletes a client if there are no associated reservations."""

    if "user_id" not in session: return redirect(url_for("home"))

    client = find_client(client_id)

    if not client:
        logging.warning(
            "Client deletion failed. ID: %s - Client not found.",
            client_id
        )

        return redirect(url_for(
            "clients_page",
            error="Client not found."
        ))

    if client_has_reservations(client_id):
        return redirect(url_for(
            "clients_page",
            error="Client cannot be deleted because they have associated reservations."
        ))

    delete_client(client_id)

    logging.info(
        "Client deleted successfully. ID: %s",
        client_id
    )

    return redirect(url_for("clients_page"))


@app.route("/clients/edit/<int:client_id>", methods=["GET", "POST"])
def edit_client_page(client_id):
    """Displays the form and updates an existing client."""

    if "user_id" not in session: return redirect(url_for("home"))

    client = find_client(client_id)

    if not client:
        logging.warning(
            "Client update failed. ID: %s - Client not found.",
            client_id
        )

        return redirect(url_for("clients_page"))

    if request.method == "POST":

        try:
            update_client(
                client_id,
                request.form.get("name"),
                request.form.get("nif"),
                request.form.get("email"),
                request.form.get("phone"),
                request.form.get("address")
            )

            logging.info(
                "Client updated successfully. ID: %s",
                client_id
            )

            return redirect(url_for("clients_page"))

        except sqlite3.IntegrityError:
            logging.warning(
                "Client update failed. ID: %s - Database integrity constraint.",
                client_id
            )

            return render_template(
                "client_form.html",
                user_name=session["user_name"],
                client=dict(request.form),
                error="A client with this NIF already exists."
            ), 400

    return render_template(
        "client_form.html",
        user_name=session["user_name"],
        client=client
    )



@app.route("/clients", methods=["GET"])
def get_clients():
    """Returns all clients."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    clients = list_clients()

    return jsonify(clients), 200


@app.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    """Returns a client by its ID."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    client = find_client(client_id)

    if not client:
        return jsonify({"error": "Client not found."}), 404

    return jsonify(client), 200


@app.route("/clients", methods=["POST"])
def add_client():
    """Creates a new client."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing data."}), 400

    required_fields = [
        "name",
        "nif"
    ]

    for field in required_fields:
        if field not in data:

            logging.warning(
                "Client creation failed. Missing field: %s",
                field
            )

            return jsonify({
                "error": f"Missing field: {field}."
            }), 400

    client_id = create_client(
        data["name"],
        data["nif"],
        data.get("email"),
        data.get("phone"),
        data.get("address")
    )

    logging.info(
        "Client created successfully. ID: %s",
        client_id
    )

    return jsonify({
        "message": "Client created successfully.",
        "id": client_id
    }), 201


@app.route("/clients/<int:client_id>", methods=["PUT"])
def edit_client(client_id):
    """Updates an existing client."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    client = find_client(client_id)

    if not client:
        return jsonify({"error": "Client not found."}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing data."}), 400

    required_fields = [
        "name",
        "nif"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}."}), 400

    update_client(
        client_id,
        data["name"],
        data["nif"],
        data.get("email"),
        data.get("phone"),
        data.get("address")
    )

    return jsonify({
        "message": "Client updated successfully."
    }), 200


@app.route("/clients/<int:client_id>", methods=["DELETE"])
def remove_client(client_id):
    """Deletes an existing client."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    client = find_client(client_id)

    if not client:
        return jsonify({"error": "Client not found."}), 404

    delete_client(client_id)

    return jsonify({
        "message": "Client deleted successfully."
    }), 200

@app.route("/clients/export/csv", methods=["GET"])
def export_clients_csv():

    """Exports all clients to a CSV file."""

    if "user_id" not in session: return redirect(url_for("home"))

    clients = list_clients()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "ID",
        "Name",
        "NIF",
        "Email",
        "Phone",
        "Address",
        "Created At"
    ])

    for client in clients:
        writer.writerow([
            client["id"],
            client["name"],
            client["nif"],
            client["email"],
            client["phone"],
            client["address"],
            client["created_at"]
        ])

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=clients.csv"
        }
    )



# ----------------------------------------------------------------------------- VEHICLES ----------------------------------------------------------------


@app.route("/vehicles-page", methods=["GET"])
def vehicles_page():

    """Displays the vehicles management page."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    vehicles = list_vehicles()

    return render_template(
        "vehicles.html",
        user_name=session["user_name"],
        vehicles=vehicles
    )


@app.route("/vehicles/delete/<int:vehicle_id>", methods=["POST"])
def delete_vehicle_page(vehicle_id):

    """Deletes a vehicle if there are no associated reservations."""

    if "user_id" not in session: return redirect(url_for("home"))

    vehicle = find_vehicle(vehicle_id)
    
    if not vehicle:
        logging.warning(
            "Vehicle deletion failed. ID: %s - Vehicle not found.",
            vehicle_id
        )

        return redirect(url_for(
            "vehicles_page",
            error="Vehicle not found."
        ))
    
    if vehicle_has_reservations(vehicle_id):
        return redirect(url_for(
            "vehicles_page",
            error="Vehicle cannot be deleted because it has associated reservations."
        ))

    delete_vehicle(vehicle_id)

    logging.info(
        "Vehicle deleted successfully. ID: %s",
        vehicle_id
    )

    return redirect(url_for("vehicles_page"))


@app.route("/vehicles/edit/<int:vehicle_id>", methods=["GET", "POST"])
def edit_vehicle_page(vehicle_id):
    """Displays the form and updates an existing vehicle."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    vehicle = find_vehicle(vehicle_id)

    if not vehicle:
        logging.warning(
            "Vehicle update failed. ID: %s - Vehicle not found.",
            vehicle_id
        )

        return redirect(url_for("vehicles_page"))

    if request.method == "POST":

        update_vehicle(
            vehicle_id,
            request.form.get("brand"),
            request.form.get("model"),
            request.form.get("license_plate"),
            request.form.get("category"),
            request.form.get("transmission"),
            request.form.get("vehicle_type"),
            request.form.get("capacity"),
            request.form.get("image_path"),
            request.form.get("daily_price"),
            request.form.get("last_revision_date"),
            request.form.get("next_revision_date"),
            request.form.get("last_inspection_date"),
            request.form.get("next_inspection_date"),
            request.form.get("status")
        )

        logging.info(
            "Vehicle updated successfully. ID: %s - License Plate: %s",
            vehicle_id,
            request.form.get("license_plate")
        )

        return redirect(url_for("vehicles_page"))

    return render_template(
        "vehicle_form.html",
        user_name=session["user_name"],
        vehicle=vehicle
    )

@app.route("/vehicles/add", methods=["GET", "POST"])
def add_vehicle_page():

    """Displays the form and creates a new vehicle."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        brand = request.form.get("brand")
        model = request.form.get("model")
        license_plate = request.form.get("license_plate")
        category = request.form.get("category")
        transmission = request.form.get("transmission")
        vehicle_type = request.form.get("vehicle_type")
        capacity = request.form.get("capacity")
        image_path = request.form.get("image_path")
        daily_price = request.form.get("daily_price")
        last_revision_date = request.form.get("last_revision_date")
        next_revision_date = request.form.get("next_revision_date")
        last_inspection_date = request.form.get("last_inspection_date")
        next_inspection_date = request.form.get("next_inspection_date")
        status = request.form.get("status")

        create_vehicle(
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

        logging.info(
            "Vehicle created successfully. Brand: %s - Model: %s - License Plate: %s",
            brand,
            model,
            license_plate
        )

        return redirect(url_for("vehicles_page"))

    return render_template(
        "vehicle_form.html",
        user_name=session["user_name"]
    )

@app.route("/vehicles", methods=["GET"])
def get_vehicles():

    """Returns all vehicles."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    vehicles = list_vehicles()

    return jsonify(vehicles), 200


@app.route("/vehicles/<int:vehicle_id>", methods=["GET"])
def get_vehicle(vehicle_id):

    """Returns a vehicle by its ID."""

    if "user_id" not in session:
            return jsonify({"error": "Authentication required."}), 401

    vehicle = find_vehicle(vehicle_id)
    if not vehicle: return jsonify({"error": "Vehicle not found."}), 404

    return jsonify(vehicle), 200


@app.route("/vehicles", methods=["POST"])
def add_vehicle():

    """Creates a new vehicle."""

    if "user_id" not in session:
            return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True)

    if not data: return jsonify({"error": "Missing data."}), 400

    required_fields = [
        "brand",
        "model",
        "license_plate",
        "category",
        "transmission",
        "vehicle_type",
        "capacity",
        "daily_price",
        "status"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}."}), 400
        
    #Campos obrigatórios usam data os campos não obrigatórios usam .get para poderam retornar None
    vehicle_id = create_vehicle(
        data["brand"],
        data["model"],
        data["license_plate"],
        data["category"],
        data["transmission"],
        data["vehicle_type"],
        data["capacity"],
        data.get("image_path"),
        data["daily_price"],
        data.get("last_revision_date"),
        data.get("next_revision_date"),
        data.get("last_inspection_date"),
        data.get("next_inspection_date"),
        data["status"]
    )

    return jsonify({
        "message": "Vehicle created successfully.",
        "id": vehicle_id
    }), 201


@app.route("/vehicles/<int:vehicle_id>", methods=["PUT"])
def edit_vehicle(vehicle_id):

    """Updates an existing vehicle."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    vehicle = find_vehicle(vehicle_id)

    if not vehicle:
        return jsonify({"error": "Vehicle not found."}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing data."}), 400

    required_fields = [
        "brand",
        "model",
        "license_plate",
        "category",
        "transmission",
        "vehicle_type",
        "capacity",
        "daily_price",
        "status"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}."}), 400

    update_vehicle(
        vehicle_id,
        data["brand"],
        data["model"],
        data["license_plate"],
        data["category"],
        data["transmission"],
        data["vehicle_type"],
        data["capacity"],
        data.get("image_path"),
        data["daily_price"],
        data.get("last_revision_date"),
        data.get("next_revision_date"),
        data.get("last_inspection_date"),
        data.get("next_inspection_date"),
        data["status"]
    )

    return jsonify({"message": "Vehicle updated successfully."}), 200


@app.route("/vehicles/<int:vehicle_id>", methods=["DELETE"])
def remove_vehicle(vehicle_id):

    """Deletes an existing vehicle."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    vehicle = find_vehicle(vehicle_id)

    if not vehicle:
        return jsonify({"Error": "Vehicle not found."}), 404

    delete_vehicle(vehicle_id)

    return jsonify({"message": "Vehicle deleted successfully."}), 200


@app.route("/vehicles/export/csv", methods=["GET"])
def export_vehicles_csv():

    """Exports all vehicles to a CSV file."""

    if "user_id" not in session: return redirect(url_for("home"))

    vehicles = list_vehicles()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "ID",
        "Brand",
        "Model",
        "License Plate",
        "Category",
        "Transmission",
        "Vehicle Type",
        "Capacity",
        "Daily Price",
        "Status"
    ])

    for vehicle in vehicles:
        writer.writerow([
            vehicle["id"],
            vehicle["brand"],
            vehicle["model"],
            vehicle["license_plate"],
            vehicle["category"],
            vehicle["transmission"],
            vehicle["vehicle_type"],
            vehicle["capacity"],
            vehicle["daily_price"],
            vehicle["status"]
        ])

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=vehicles.csv"
        }
    )

    
# ----------------------------------------------------------------------------- PAYMENT METHODS ----------------------------------------------------------------


@app.route("/payment-methods/delete/<int:payment_method_id>", methods=["POST"])
def delete_payment_method_page(payment_method_id):

    """Deletes a payment method if there are no associated reservations."""

    if "user_id" not in session: return redirect(url_for("home"))

    payment_method = find_payment_method(payment_method_id)

    if not payment_method:
        logging.warning(
            "Payment method deletion failed. ID: %s - Payment method not found.",
            payment_method_id
        )

        return redirect(url_for(
            "payment_methods_page",
            error="Payment method not found."
        ))

    if payment_method_has_reservations(payment_method_id):
        logging.warning(
            "Payment method deletion failed. ID: %s - Associated reservations exist.",
            payment_method_id
        )

        return redirect(url_for(
            "payment_methods_page",
            error="Payment method cannot be deleted because it has associated reservations."
        ))

    delete_payment_method(payment_method_id)

    logging.info(
        "Payment method deleted successfully. ID: %s",
        payment_method_id
    )

    return redirect(url_for("payment_methods_page"))


@app.route("/payment-methods/add", methods=["GET", "POST"])
def add_payment_method_page():

    """Displays the form and creates a new payment method."""

    if "user_id" not in session: return redirect(url_for("home"))

    if request.method == "POST":

        name = request.form.get("name")

        try:
            create_payment_method(name)

            logging.info(
                "Payment method created successfully. Name: %s",
                name
            )

            return redirect(url_for("payment_methods_page"))

        except sqlite3.IntegrityError:
            logging.warning(
                "Payment method creation failed. Database integrity constraint."
            )

            return render_template(
                "payment_method_form.html",
                user_name=session["user_name"],
                error="Payment method already exists."
            ), 400

    return render_template(
        "payment_method_form.html",
        user_name=session["user_name"]
    )



@app.route("/payment-methods/edit/<int:payment_method_id>", methods=["GET", "POST"])
def edit_payment_method_page(payment_method_id):

    """Displays the form and updates an existing payment method."""

    if "user_id" not in session: return redirect(url_for("home"))

    payment_method = find_payment_method(payment_method_id)

    if not payment_method:
        logging.warning(
            "Payment method update failed. ID: %s - Payment method not found.",
            payment_method_id
        )

        return redirect(url_for("payment_methods_page"))

    if request.method == "POST":

        name = request.form.get("name")

        try:
            update_payment_method(payment_method_id, name)

            logging.info(
                "Payment method updated successfully. ID: %s - Name: %s",
                payment_method_id,
                name
            )

            return redirect(url_for("payment_methods_page"))

        except sqlite3.IntegrityError:
            logging.warning(
                "Payment method update failed. ID: %s - Database integrity constraint.",
                payment_method_id
            )

            return render_template(
                "payment_method_form.html",
                user_name=session["user_name"],
                payment_method={"id": payment_method_id, "name": name},
                error="Payment method already exists."
            ), 400

    return render_template(
        "payment_method_form.html",
        user_name=session["user_name"],
        payment_method=payment_method
    )


@app.route("/payment-methods-page", methods=["GET"])
def payment_methods_page():

    """Displays the payment methods management page."""

    if "user_id" not in session: return redirect(url_for("home"))

    payment_methods = list_payment_methods()

    return render_template(
        "payment_methods.html",
        user_name=session["user_name"],
        payment_methods=payment_methods
    )

@app.route("/payment-methods", methods=["GET"])
def get_payment_methods():

    """Returns all payment methods."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    payment_methods = list_payment_methods()

    return jsonify(payment_methods), 200


@app.route("/payment-methods/<int:payment_method_id>", methods=["GET"])
def get_payment_method(payment_method_id):

    """Returns a payment method by its ID."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    payment_method = find_payment_method(payment_method_id)
    if not payment_method:
        return jsonify({"error": "Payment method not found."}), 404

    return jsonify(payment_method), 200


@app.route("/payment-methods", methods=["POST"])
def add_payment_method():

    """Creates a new payment method."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing data."}), 400

    if "name" not in data:
        return jsonify({"error": "Missing field: name."}), 400

    payment_method_id = create_payment_method(data["name"])

    return jsonify({
        "message": "Payment method created successfully.",
        "id": payment_method_id
    }), 201


@app.route("/payment-methods/<int:payment_method_id>", methods=["PUT"])
def edit_payment_method(payment_method_id):

    """Updates an existing payment method."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    payment_method = find_payment_method(payment_method_id)

    if not payment_method:
        return jsonify({"error": "Payment method not found."}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing data."}), 400

    if "name" not in data:
        return jsonify({"error": "Missing field: name."}), 400

    update_payment_method(
        payment_method_id,
        data["name"]
    )

    return jsonify({
        "message": "Payment method updated successfully."
    }), 200


@app.route("/payment-methods/<int:payment_method_id>", methods=["DELETE"])
def remove_payment_method(payment_method_id):
    
    """Deletes an existing payment method."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    payment_method = find_payment_method(payment_method_id)

    if not payment_method:
        return jsonify({"error": "Payment method not found."}), 404

    delete_payment_method(payment_method_id)

    return jsonify({
        "message": "Payment method deleted successfully."
    }), 200


@app.route("/payment-methods/export/csv", methods=["GET"])
def export_payment_methods_csv():
    """Exports all payment methods to a CSV file."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    payment_methods = list_payment_methods()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "ID",
        "Name"
    ])

    for payment_method in payment_methods:
        writer.writerow([
            payment_method["id"],
            payment_method["name"]
        ])

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=payment_methods.csv"
        }
    )



# ----------------------------------------------------------------------------- RESERVATIONS ----------------------------------------------------------------

@app.route("/reservations", methods=["GET"])
def get_reservations():

    """Returns all reservations."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    reservations = list_reservations()

    return jsonify(reservations), 200


@app.route("/reservations/<int:reservation_id>", methods=["GET"])
def get_reservation(reservation_id):

    """Returns a reservation by its ID."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    reservation = get_reservation_details(reservation_id)

    if not reservation:
        return jsonify({"error": "Reservation not found."}), 404

    return jsonify(reservation), 200


@app.route("/reservations", methods=["POST"])
def add_reservation():

    """Creates a new reservation."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Missing data."}), 400

    required_fields = [
        "client_id",
        "vehicle_id",
        "payment_method_id",
        "start_date",
        "end_date"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}."}), 400

    result = create_reservation(
        data["client_id"],
        data["vehicle_id"],
        data["payment_method_id"],
        data["start_date"],
        data["end_date"]
    )

    if "error" in result:
        return jsonify(result), 400

    return jsonify({
        "message": "Reservation created successfully.",
        "id": result["id"],
        "total_price": result["total_price"]
    }), 201

@app.route("/reservations/<int:reservation_id>", methods=["DELETE"])
def remove_reservation(reservation_id):
    
    """Deletes an existing reservation."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    reservation = find_reservation(reservation_id)

    if not reservation:
        return jsonify({"error": "Reservation not found."}), 404

    delete_reservation(reservation_id)

    return jsonify({
        "message": "Reservation deleted successfully."
    }), 200


@app.route("/reservations/<int:reservation_id>", methods=["PUT"])
def edit_reservation(reservation_id):

    """Updates an existing reservation."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    reservation = find_reservation(reservation_id)

    if not reservation: return jsonify({"error": "Reservation not found."}), 404

    data = request.get_json(silent=True)

    if not data: return jsonify({"error": "Missing data."}), 400

    required_fields = [
        "client_id",
        "vehicle_id",
        "payment_method_id",
        "start_date",
        "end_date"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}."}), 400

    result = update_reservation(
        reservation_id,
        data["client_id"],
        data["vehicle_id"],
        data["payment_method_id"],
        data["start_date"],
        data["end_date"]
    )

    if "error" in result: return jsonify(result), 400

    return jsonify({
        "message": "Reservation updated successfully.",
        "total_price": result["total_price"]
    }), 200


@app.route("/reservations-page", methods=["GET"])
def reservations_page():

    """Displays the reservations management page."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    reservations = list_reservations()

    return render_template(
        "reservations.html",
        user_name=session["user_name"],
        reservations=reservations
    )

@app.route("/reservations/add", methods=["GET", "POST"])
def add_reservation_page():

    """Displays the form and creates a new reservation."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        client_id = int(request.form.get("client_id"))
        vehicle_id = int(request.form.get("vehicle_id"))
        payment_method_id = int(request.form.get("payment_method_id"))
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        result = create_reservation(
            client_id,
            vehicle_id,
            payment_method_id,
            start_date,
            end_date
        )

        if "error" in result:
            logging.warning(
                "Reservation creation failed: %s",
                result["error"]
            )

            return redirect(url_for(
                "reservations_page",
                error=result["error"]
            ))

        logging.info(
            "Reservation created successfully. ID: %s",
            result["id"]
        )

        return redirect(url_for("reservations_page"))

    return render_template(
        "reservation_form.html",
        user_name=session["user_name"],
        clients=list_clients(),
        vehicles=list_vehicles(),
        payment_methods=list_payment_methods()
    )

@app.route("/reservations/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation_page(reservation_id):

    """Displays the form and updates an existing reservation."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    reservation = find_reservation(reservation_id)

    if not reservation:
        return redirect(url_for("reservations_page"))

    if request.method == "POST":

        result = update_reservation(
            reservation_id,
            int(request.form.get("client_id")),
            int(request.form.get("vehicle_id")),
            int(request.form.get("payment_method_id")),
            request.form.get("start_date"),
            request.form.get("end_date")
        )

        if "error" in result:
            logging.warning(
                "Reservation update failed. ID: %s - Error: %s",
                reservation_id,
                result["error"]
            )

            return redirect(url_for(
                "reservations_page",
                error=result["error"]
            ))

        logging.info(
            "Reservation updated successfully. ID: %s",
            reservation_id
        )

        return redirect(url_for("reservations_page"))

    return render_template(
        "reservation_form.html",
        user_name=session["user_name"],
        reservation=reservation,
        clients=list_clients(),
        vehicles=list_vehicles(),
        payment_methods=list_payment_methods()
    )

@app.route("/reservations/delete/<int:reservation_id>", methods=["POST"])
def delete_reservation_page(reservation_id):

    """Deletes a reservation from the management page."""

    if "user_id" not in session: return redirect(url_for("home"))

    reservation = find_reservation(reservation_id)

    if not reservation:
        logging.warning(
            "Reservation deletion failed. ID: %s - Reservation not found.",
            reservation_id
        )

        return redirect(url_for(
            "reservations_page",
            error="Reservation not found."
        ))

    delete_reservation(reservation_id)

    logging.info(
        "Reservation deleted successfully. ID: %s",
        reservation_id
    )

    return redirect(url_for("reservations_page"))


@app.route("/reservations/export/csv", methods=["GET"])
def export_reservations_csv():
    """Exports all reservations to a CSV file."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    reservations = list_reservations()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "ID",
        "Client",
        "Vehicle",
        "Payment Method",
        "Start Date",
        "End Date",
        "Daily Price",
        "Total Price",
        "Status",
        "Created At"
    ])

    for reservation in reservations:
        writer.writerow([
            reservation["id"],
            reservation["client"],
            reservation["vehicle"],
            reservation["payment_method"],
            reservation["start_date"],
            reservation["end_date"],
            reservation["daily_price"],
            reservation["total_price"],
            reservation["status"],
            reservation["created_at"]
        ])

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=reservations.csv"
        }
    )

# ----------------------------------------------------------------------------- DASHBOARD ----------------------------------------------------------------

@app.route("/dashboard", methods=["GET"])
def get_dashboard():
    """Returns all dashboard information."""

    if "user_id" not in session:
        return jsonify({"error": "Authentication required."}), 401

    dashboard = {
        "rented_vehicles": get_rented_vehicles(),
        "latest_clients": get_latest_clients(),
        "available_vehicles_by_category": get_available_vehicles_by_category(),
        "monthly_summary": get_monthly_reservations_summary(),
        "upcoming_revisions": get_upcoming_revisions(),
        "upcoming_inspections": get_upcoming_inspections(),
        "revision_alerts": get_revision_alerts()
    }

    return jsonify(dashboard), 200

@app.route("/", methods=["GET"])
def home():

    """Displays the login page."""

    return render_template("login.html")


@app.route("/session", methods=["GET"])
def check_session():

    """Returns the current logged-in user."""

    if "user_id" not in session:
        return jsonify({
            "error": "User not logged in."
        }), 401

    return jsonify({
        "user_id": session["user_id"],
        "user_name": session["user_name"],
        "user_role": session["user_role"]
    }), 200


@app.route("/dashboard-page", methods=["GET"])
def dashboard_page():

    """Displays the dashboard page."""

    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        monthly_summary=get_monthly_reservations_summary(),
        rented_vehicles=get_rented_vehicles(),
        latest_clients=get_latest_clients(),
        available_vehicles=get_available_vehicles_by_category(),
        upcoming_revisions=get_upcoming_revisions(),
        upcoming_inspections=get_upcoming_inspections(),
        revision_alerts=get_revision_alerts()
    )






if __name__ == "__main__":
    app.run(debug=True)