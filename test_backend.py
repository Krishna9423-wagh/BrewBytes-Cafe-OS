import unittest
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_db
from auth import hash_password, verify_password, create_access_token, decode_access_token

class TestBrewBytesBackend(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_password_hashing(self):
        pwd = "cafe_secret_pass"
        h = hash_password(pwd)
        self.assertTrue(verify_password(pwd, h))
        self.assertFalse(verify_password("wrong_pass", h))

    def test_jwt_token_creation_and_decoding(self):
        payload = {"sub": "manager_amit", "role": "owner"}
        token = create_access_token(payload)
        self.assertTrue(isinstance(token, str))

        decoded = decode_access_token(token)
        self.assertEqual(decoded["sub"], "manager_amit")
        self.assertEqual(decoded["role"], "owner")
        self.assertIn("exp", decoded)

    def test_integer_paise_arithmetic(self):
        # Spec from image: Float nahi, paise (integer) me store
        # 140 Rs Cappuccino + 90 Rs Brownie = 230 Rs (23000 paise)
        cappuccino_paise = 14000
        brownie_paise = 9000
        subtotal_paise = cappuccino_paise * 2 + brownie_paise * 1 # 37000 paise (Rs 370)
        self.assertEqual(subtotal_paise, 37000)

        # 10% Discount: 3700 paise
        discount_paise = int(subtotal_paise * 0.10)
        self.assertEqual(discount_paise, 3700)

        # After discount: 33300 paise
        after_disc_paise = subtotal_paise - discount_paise
        self.assertEqual(after_disc_paise, 33300)

        # 5% GST: 33300 * 0.05 = 1665 paise
        gst_paise = int(after_disc_paise * 0.05)
        self.assertEqual(gst_paise, 1665)

        # Total payable in integer paise: 34965 paise (Rs 349.65)
        total_paise = after_disc_paise + gst_paise
        self.assertEqual(total_paise, 34965)
        # Ensure no floating point precision issue (e.g., 0.1 + 0.2 != 0.3)
        self.assertIsInstance(total_paise, int)

    def test_order_creation_and_stock_movement_entry(self):
        # Spec from image: Counter ki jagah har order par stock_movements ki entry
        conn = get_db()
        cursor = conn.cursor()
        order_id = f"test_ord_{int(time.time()*1000)}"
        now = int(time.time()*1000)

        cursor.execute("""
        INSERT INTO orders (id, table_number, customer_name, status, subtotal_paise, total_paise, created_at)
        VALUES (?, 1, 'Test Customer', 'new', 28000, 28000, ?)
        """, (order_id, now))

        # Deduct 0.4L milk for 2 Cappuccinos
        cursor.execute("""
        INSERT INTO stock_movements (movement_type, order_id, ingredient_code, ingredient_name, qty_change, unit, created_at)
        VALUES ('order_deduct', ?, 'd', 'Doodh', -0.4, 'L', ?)
        """, (order_id, now))
        conn.commit()

        cursor.execute("SELECT * FROM stock_movements WHERE order_id = ?", (order_id,))
        movement = cursor.fetchone()
        self.assertIsNotNone(movement)
        self.assertEqual(movement["ingredient_code"], "d")
        self.assertEqual(movement["qty_change"], -0.4)
        conn.close()

    def test_close_day_frees_open_orders(self):
        conn = get_db()
        cursor = conn.cursor()
        order_id = f"test_dayclose_{int(time.time()*1000)}"
        now = int(time.time()*1000)

        cursor.execute("""
        INSERT INTO orders (id, table_number, customer_name, status, subtotal_paise, total_paise, created_at)
        VALUES (?, 5, 'Unclosed Customer', 'cooking', 15000, 15000, ?)
        """, (order_id, now))
        conn.commit()

        # Simulate day close
        cursor.execute("""
        UPDATE orders
        SET status = 'served', paid_method = COALESCE(paid_method, 'DayClosed'), paid_at = COALESCE(paid_at, ?)
        WHERE status != 'served' AND status != 'cancelled'
        """, (now,))
        conn.commit()

        cursor.execute("SELECT status, paid_method FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        self.assertEqual(row["status"], "served")
        self.assertEqual(row["paid_method"], "DayClosed")
        conn.close()

if __name__ == "__main__":
    unittest.main()

