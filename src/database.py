import sqlite3
import os
from datetime import datetime
import uuid


class Database:
    def __init__(self, db_path="car_qr.db"):
        self.db_path = db_path
        self.initialize_db()

    def initialize_db(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create QR codes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS qr_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    qr_uuid VARCHAR(36) UNIQUE NOT NULL,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    claimed BOOLEAN DEFAULT FALSE,
                    batch_id VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'active',
                    file_path VARCHAR(255),
                    sticker_path VARCHAR(255),
                    redirect_url VARCHAR(255)
                )
            """
            )

            # Create claims table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    qr_uuid VARCHAR(36),
                    claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_phone VARCHAR(15),
                    masked_number VARCHAR(15),
                    FOREIGN KEY (qr_uuid) REFERENCES qr_codes(qr_uuid)
                )
            """
            )

            conn.commit()

    def create_qr_record(
        self, batch_id=None, file_path=None, sticker_path=None, qr_uuid=None
    ):
        """Create a new QR code record"""
        if qr_uuid is None:
            qr_uuid = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO qr_codes (qr_uuid, batch_id, file_path, sticker_path)
                VALUES (?, ?, ?, ?)
            """,
                (qr_uuid, batch_id, file_path, sticker_path),
            )
            conn.commit()
            return qr_uuid

    def get_qr_details(self, qr_uuid):
        """Get QR code details"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM qr_codes WHERE qr_uuid = ?", (qr_uuid,))
            return cursor.fetchone()

    def claim_qr(self, qr_uuid, user_phone, masked_number):
        """Claim a QR code and update its redirect URL"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if QR is already claimed
            cursor.execute("SELECT claimed FROM qr_codes WHERE qr_uuid = ?", (qr_uuid,))
            result = cursor.fetchone()
            if result and result[0]:
                return False, "QR code already claimed"

            # Update QR status, redirect URL and create claim record
            contact_url = f"www.sticqr.docpulp.com/contact/{qr_uuid}"
            cursor.execute(
                """
                UPDATE qr_codes 
                SET claimed = TRUE, redirect_url = ? 
                WHERE qr_uuid = ?
            """,
                (contact_url, qr_uuid),
            )

            cursor.execute(
                """
                INSERT INTO claims (qr_uuid, user_phone, masked_number)
                VALUES (?, ?, ?)
            """,
                (qr_uuid, user_phone, masked_number),
            )

            conn.commit()
            return True, "QR code claimed successfully"

    def get_redirect_url(self, qr_uuid):
        """Get the current redirect URL for a QR code based on its claim status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT claimed, redirect_url 
                FROM qr_codes 
                WHERE qr_uuid = ?
            """,
                (qr_uuid,),
            )
            result = cursor.fetchone()

            if not result:
                return None

            claimed, redirect_url = result
            if claimed and redirect_url:
                return redirect_url
            else:
                return f"www.sticqr.docpulp.com/claim/{qr_uuid}"

    def get_batch_qrs(self, batch_id):
        """Get all QR codes in a batch"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM qr_codes WHERE batch_id = ?", (batch_id,))
            return cursor.fetchall()
