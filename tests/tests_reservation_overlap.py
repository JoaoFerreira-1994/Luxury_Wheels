
import unittest
import sqlite3


class TestReservationOverlap(unittest.TestCase):

    def setUp(self):
        """Creates an isolated in-memory database."""

        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

        self.conn.execute("""
            CREATE TABLE reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        self.conn.execute("""
            INSERT INTO reservations (
                vehicle_id, start_date, end_date, status
            )
            VALUES (?, ?, ?, ?)
        """, (1, "2026-10-10", "2026-10-15", "confirmed"))

        self.conn.commit()

    def tearDown(self):
        """Closes the test database."""
        self.conn.close()

    def has_overlap(self, vehicle_id, start_date, end_date):
        """Checks overlapping reservations using the application SQL."""

        result = self.conn.execute("""
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

        return result is not None

    def test_overlapping_dates(self):
        """Tests overlapping reservation dates."""

        self.assertTrue(
            self.has_overlap(1, "2026-10-12", "2026-10-17")
        )

    def test_adjacent_dates(self):
        """Tests reservations with adjacent dates."""

        self.assertFalse(
            self.has_overlap(1, "2026-10-15", "2026-10-20")
        )

    def test_cancelled_reservation(self):
        """Tests that cancelled reservations do not block dates."""

        self.conn.execute("""
            UPDATE reservations
            SET status = 'cancelled'
            WHERE id = 1
        """)

        self.conn.commit()

        self.assertFalse(
            self.has_overlap(1, "2026-10-12", "2026-10-17")
        )


if __name__ == "__main__":
    unittest.main()
