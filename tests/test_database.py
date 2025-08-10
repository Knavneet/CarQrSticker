import pytest
import os
from src.database import Database
import sqlite3
import uuid


@pytest.fixture
def temp_db():
    """Create a temporary test database"""
    db_path = "test_car_qr.db"
    db = Database(db_path)
    yield db
    # Cleanup after tests
    if os.path.exists(db_path):
        os.remove(db_path)


def test_database_initialization(temp_db):
    """Test if database is properly initialized with required tables"""
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()

        # Check qr_codes table
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='qr_codes';
        """
        )
        assert cursor.fetchone() is not None

        # Check claims table
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='claims';
        """
        )
        assert cursor.fetchone() is not None


def test_create_qr_record(temp_db):
    """Test creation of QR code records"""
    batch_id = str(uuid.uuid4())
    file_path = "/test/path/qr.png"
    sticker_path = "/test/path/sticker.png"

    # Create QR record
    qr_uuid = temp_db.create_qr_record(
        batch_id=batch_id, file_path=file_path, sticker_path=sticker_path
    )

    # Verify record exists
    qr_details = temp_db.get_qr_details(qr_uuid)
    assert qr_details is not None
    assert qr_details[1] == qr_uuid  # qr_uuid is at index 1
    assert qr_details[4] == batch_id  # batch_id is at index 4
    assert qr_details[6] == file_path  # file_path is at index 6
    assert qr_details[7] == sticker_path  # sticker_path is at index 7


def test_claim_qr(temp_db):
    """Test QR code claiming process"""
    # Create a QR code first
    qr_uuid = temp_db.create_qr_record()
    user_phone = "1234567890"
    masked_number = "9876543210"

    # Test successful claim
    success, message = temp_db.claim_qr(qr_uuid, user_phone, masked_number)
    assert success is True
    assert message == "QR code claimed successfully"

    # Verify claim in database
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()

        # Check QR status
        cursor.execute("SELECT claimed FROM qr_codes WHERE qr_uuid = ?", (qr_uuid,))
        assert cursor.fetchone()[0] == 1  # Should be marked as claimed

        # Check claim record
        cursor.execute(
            "SELECT user_phone, masked_number FROM claims WHERE qr_uuid = ?", (qr_uuid,)
        )
        claim = cursor.fetchone()
        assert claim[0] == user_phone
        assert claim[1] == masked_number


def test_duplicate_claim_prevention(temp_db):
    """Test that a QR code cannot be claimed twice"""
    # Create and claim a QR code
    qr_uuid = temp_db.create_qr_record()
    first_claim = temp_db.claim_qr(qr_uuid, "1234567890", "9876543210")
    assert first_claim[0] is True

    # Try to claim again
    second_claim = temp_db.claim_qr(qr_uuid, "1111111111", "2222222222")
    assert second_claim[0] is False
    assert second_claim[1] == "QR code already claimed"


def test_get_batch_qrs(temp_db):
    """Test retrieving QR codes by batch"""
    batch_id = str(uuid.uuid4())

    # Create multiple QR codes in the same batch
    qr_uuids = []
    for _ in range(3):
        qr_uuid = temp_db.create_qr_record(batch_id=batch_id)
        qr_uuids.append(qr_uuid)

    # Retrieve batch
    batch_qrs = temp_db.get_batch_qrs(batch_id)
    assert len(batch_qrs) == 3

    # Verify all QRs in batch
    batch_uuids = [qr[1] for qr in batch_qrs]  # qr_uuid is at index 1
    for qr_uuid in qr_uuids:
        assert qr_uuid in batch_uuids


def test_qr_status_after_creation(temp_db):
    """Test default values when creating QR code"""
    qr_uuid = temp_db.create_qr_record()
    qr_details = temp_db.get_qr_details(qr_uuid)

    assert qr_details[3] == 0  # claimed should be False (0)
    assert qr_details[5] == "active"  # status should be 'active'


def test_qr_redirect_url_flow(temp_db):
    """Test the dynamic URL redirection flow"""
    # Create new QR code
    qr_uuid = temp_db.create_qr_record()

    # Check initial redirect URL (should be claim URL)
    initial_url = temp_db.get_redirect_url(qr_uuid)
    assert initial_url == f"www.sticqr.docpulp.com/claim/{qr_uuid}"

    # Claim the QR code
    temp_db.claim_qr(qr_uuid, "1234567890", "9876543210")

    # Check redirect URL after claiming (should be contact URL)
    claimed_url = temp_db.get_redirect_url(qr_uuid)
    assert claimed_url == f"www.sticqr.docpulp.com/contact/{qr_uuid}"

    # Verify non-existent QR code returns None
    assert temp_db.get_redirect_url("non-existent-uuid") is None
