import importlib
import os
import sqlite3
import tempfile
import unittest

import config
import database.db as db_module
import database.tickets_db as tickets_module


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp.close()
        config.DB_PATH = self.temp.name
        importlib.reload(db_module)
        importlib.reload(tickets_module)
        self.db = tickets_module
        self.db.init_db()

    def tearDown(self):
        try:
            os.unlink(self.temp.name)
        except OSError:
            pass

    def test_init_db_creates_tables(self):
        conn = db_module.get_db()
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in c.fetchall()]
        conn.close()
        self.assertIn("tickets", tables)
        self.assertIn("stats", tables)

    def test_save_and_get_ticket(self):
        self.db.save_ticket(123, 456, "test_user", "RP ЗАЯВКА", "rp", "{}", "2024-01-01T00:00:00")
        ticket = self.db.get_ticket(123)
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket["channel_id"], 123)
        self.assertEqual(ticket["user_id"], 456)
        self.assertEqual(ticket["user_name"], "test_user")
        self.assertEqual(ticket["topic"], "RP ЗАЯВКА")
        self.assertEqual(ticket["type"], "rp")
        self.assertEqual(ticket["status"], "open")

    def test_get_ticket_not_found(self):
        ticket = self.db.get_ticket(99999)
        self.assertIsNone(ticket)

    def test_delete_ticket(self):
        self.db.save_ticket(111, 222, "user", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.db.delete_ticket(111)
        ticket = self.db.get_ticket(111)
        self.assertIsNone(ticket)

    def test_update_ticket_status_accepted(self):
        self.db.save_ticket(100, 200, "u", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.db.update_ticket_status(100, "accepted", 300, "ok")
        ticket = self.db.get_ticket(100)
        self.assertEqual(ticket["status"], "accepted")
        self.assertEqual(ticket["closed_by"], 300)
        self.assertEqual(ticket["reason"], "ok")
        self.assertIsNotNone(ticket["closed_at"])

    def test_update_ticket_status_denied(self):
        self.db.save_ticket(101, 201, "u", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.db.update_ticket_status(101, "denied", 301, "no")
        ticket = self.db.get_ticket(101)
        self.assertEqual(ticket["status"], "denied")

    def test_update_ticket_status_returns_true(self):
        self.db.save_ticket(102, 202, "u", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.assertTrue(self.db.update_ticket_status(102, "accepted", 300, "ok"))

    def test_update_ticket_status_missing_ticket(self):
        self.assertFalse(self.db.update_ticket_status(999, "accepted", 300, "ok"))

    def test_update_ticket_status_twice_returns_false(self):
        self.db.save_ticket(103, 203, "u", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.assertTrue(self.db.update_ticket_status(103, "accepted", 300, "ok"))
        self.assertFalse(self.db.update_ticket_status(103, "denied", 300, "no"))

    def test_update_ticket_status_twice_stats_not_doubled(self):
        self.db.save_ticket(104, 204, "u", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.db.update_ticket_status(104, "accepted", 300, "ok")
        self.db.update_ticket_status(104, "accepted", 300, "ok")

        stats = self.db.get_stats()
        self.assertEqual(stats["accepted"], 1)
        self.assertEqual(stats["denied"], 0)

    def test_update_ticket_status_closed_not_in_stats(self):
        self.db.save_ticket(105, 205, "u", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.assertTrue(self.db.update_ticket_status(105, "closed", 300))

        stats = self.db.get_stats()
        self.assertEqual(stats["accepted"], 0)
        self.assertEqual(stats["denied"], 0)
        self.assertEqual(stats["open"], 0)

    def test_save_ticket_duplicate_channel_raises(self):
        self.db.save_ticket(106, 206, "u", "T", "rp", "{}", "2024-01-01T00:00:00")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.save_ticket(106, 207, "u2", "T", "rp", "{}", "2024-01-01T00:00:00")

    def test_stats_increment(self):
        self.db.save_ticket(1, 10, "a", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.db.update_ticket_status(1, "accepted", 99, "ok")
        self.db.save_ticket(2, 20, "b", "T", "rp", "{}", "2024-01-01T00:00:00")
        self.db.update_ticket_status(2, "denied", 99, "no")

        stats = self.db.get_stats()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["accepted"], 1)
        self.assertEqual(stats["denied"], 1)
        self.assertEqual(stats["open"], 0)
        self.assertEqual(len(stats["weekly"]), 1)

    def test_get_all_tickets_limit(self):
        for i in range(10):
            self.db.save_ticket(i, i, f"user{i}", "T", "rp", "{}", f"2024-01-{i + 1:02d}T00:00:00")
        results = self.db.get_all_tickets(limit=5)
        self.assertEqual(len(results), 5)

    def test_get_all_tickets_order(self):
        self.db.save_ticket(1, 1, "a", "T", "rp", "{}", "2024-01-02T00:00:00")
        self.db.save_ticket(2, 2, "b", "T", "rp", "{}", "2024-01-01T00:00:00")
        results = self.db.get_all_tickets(limit=10)
        self.assertEqual(results[0]["channel_id"], 1)


if __name__ == "__main__":
    unittest.main()
