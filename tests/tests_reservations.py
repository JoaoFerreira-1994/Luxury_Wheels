
import unittest
from unittest.mock import patch

from models import create_reservation


class TestReservations(unittest.TestCase):
    @patch("models.find_client")
    def test_client_not_found(self, mock_find_client):

        """Tests reservation creation with an invalid client."""

        mock_find_client.return_value = None

        result = create_reservation(
            client_id=999,
            vehicle_id=1,
            payment_method_id=1,
            start_date="2026-10-10",
            end_date="2026-10-15"
        )

        self.assertEqual(
            result,
            {"error": "Client not found."}
        )

        
    @patch("models.find_client")
    @patch("models.find_vehicle")
    def test_vehicle_not_found(self, mock_find_vehicle, mock_find_client):
        
        """Tests reservation creation with an invalid vehicle."""

        mock_find_client.return_value = {"id": 1}
        mock_find_vehicle.return_value = None

        result = create_reservation(
            client_id=1,
            vehicle_id=999,
            payment_method_id=1,
            start_date="2026-10-10",
            end_date="2026-10-15"
        )

        self.assertEqual(
            result,
            {"error": "Vehicle not found."}
        )


    
    @patch("models.find_client")
    @patch("models.find_vehicle")
    @patch("models.find_payment_method")
    def test_payment_method_not_found(
        self,
        mock_find_payment_method,
        mock_find_vehicle,
        mock_find_client
    ):
        """Tests reservation creation with an invalid payment method."""

        mock_find_client.return_value = {"id": 1}
        mock_find_vehicle.return_value = {"id": 1}
        mock_find_payment_method.return_value = None

        result = create_reservation(
            client_id=1,
            vehicle_id=1,
            payment_method_id=999,
            start_date="2026-10-16",
            end_date="2026-10-20"
        )

        self.assertEqual(
            result,
            {"error": "Payment method not found."}
        )

    
    @patch("models.find_client")
    @patch("models.find_vehicle")
    @patch("models.find_payment_method")
    def test_invalid_date_format(
        self,
        mock_find_payment_method,
        mock_find_vehicle,
        mock_find_client
    ):
        """Tests reservation creation with an invalid date format."""

        mock_find_client.return_value = {"id": 1}
        mock_find_vehicle.return_value = {"id": 1}
        mock_find_payment_method.return_value = {"id": 1}

        result = create_reservation(
            client_id=1,
            vehicle_id=1,
            payment_method_id=1,
            start_date="16/10/2026",
            end_date="20/10/2026"
        )

        self.assertEqual(
            result,
            {"error": "Invalid date format. Use YYYY-MM-DD."}
        )


    @patch("models.find_client")
    @patch("models.find_vehicle")
    @patch("models.find_payment_method")
    def test_invalid_date_range(
        self,
        mock_find_payment_method,
        mock_find_vehicle,
        mock_find_client
    ):
        """Tests reservation creation with an invalid date range."""

        mock_find_client.return_value = {"id": 1}
        mock_find_vehicle.return_value = {"id": 1}
        mock_find_payment_method.return_value = {"id": 1}

        result = create_reservation(
            client_id=1,
            vehicle_id=1,
            payment_method_id=1,
            start_date="2026-10-20",
            end_date="2026-10-16"
        )

        self.assertEqual(
            result,
            {"error": "End date must be after start date."}
        )


    @patch("models.find_client")
    @patch("models.find_vehicle")
    @patch("models.find_payment_method")
    def test_vehicle_under_maintenance(
        self,
        mock_find_payment_method,
        mock_find_vehicle,
        mock_find_client
    ):
        """Tests reservation creation for a vehicle under maintenance."""

        mock_find_client.return_value = {"id": 1}

        mock_find_vehicle.return_value = {
            "id": 1,
            "status": "maintenance",
            "daily_price": 100.00
        }

        mock_find_payment_method.return_value = {"id": 1}

        result = create_reservation(
            client_id=1,
            vehicle_id=1,
            payment_method_id=1,
            start_date="2026-10-16",
            end_date="2026-10-20"
        )

        self.assertEqual(
            result,
            {"error": "Vehicle is under maintenance."}
        )


    @patch("models.find_client")
    @patch("models.find_vehicle")
    @patch("models.find_payment_method")
    @patch("models.connect")
    def test_overlapping_reservation(
        self,
        mock_connect,
        mock_find_payment_method,
        mock_find_vehicle,
        mock_find_client
    ):
        """Tests reservation creation with overlapping dates."""

        mock_find_client.return_value = {"id": 1}

        mock_find_vehicle.return_value = {
            "id": 1,
            "status": "available",
            "daily_price": 100.00
        }

        mock_find_payment_method.return_value = {"id": 1}

        mock_conn = mock_connect.return_value

        mock_conn.execute.return_value.fetchone.return_value = {
            "id": 5
        }

        result = create_reservation(
            client_id=1,
            vehicle_id=1,
            payment_method_id=1,
            start_date="2026-10-18",
            end_date="2026-10-22"
        )

        self.assertEqual(
            result,
            {"error": "Vehicle is already reserved for these dates."}
        )

        mock_conn.close.assert_called_once()

    
    @patch("models.find_client")
    @patch("models.find_vehicle")
    @patch("models.find_payment_method")
    @patch("models.connect")
    def test_create_reservation_success(
        self,
        mock_connect,
        mock_find_payment_method,
        mock_find_vehicle,
        mock_find_client
    ):
        """Tests successful reservation creation and total price."""

        mock_find_client.return_value = {"id": 1}

        mock_find_vehicle.return_value = {
            "id": 1,
            "status": "available",
            "daily_price": 100.00
        }

        mock_find_payment_method.return_value = {"id": 1}

        mock_conn = mock_connect.return_value

        # No overlapping reservations
        mock_conn.execute.return_value.fetchone.return_value = None

        # Simulate the new reservation ID
        mock_conn.execute.return_value.lastrowid = 10

        result = create_reservation(
            client_id=1,
            vehicle_id=1,
            payment_method_id=1,
            start_date="2026-10-16",
            end_date="2026-10-20"
        )

        self.assertEqual(
            result,
            {
                "id": 10,
                "total_price": 400.00
            }
        )

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


    @patch("models.find_client")
    @patch("models.find_vehicle")
    @patch("models.find_payment_method")
    @patch("models.connect")
    def test_create_reservation_success(
        self,
        mock_connect,
        mock_find_payment_method,
        mock_find_vehicle,
        mock_find_client
    ):
        """Tests successful reservation creation and total price."""

        mock_find_client.return_value = {"id": 1}

        mock_find_vehicle.return_value = {
            "id": 1,
            "status": "available",
            "daily_price": 100.00
        }

        mock_find_payment_method.return_value = {"id": 1}

        mock_conn = mock_connect.return_value

        # No overlapping reservations
        mock_conn.execute.return_value.fetchone.return_value = None

        # Simulate the new reservation ID
        mock_conn.execute.return_value.lastrowid = 10

        result = create_reservation(
            client_id=1,
            vehicle_id=1,
            payment_method_id=1,
            start_date="2026-10-16",
            end_date="2026-10-20"
        )

        self.assertEqual(
            result,
            {
                "id": 10,
                "total_price": 400.00
            }
        )

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
