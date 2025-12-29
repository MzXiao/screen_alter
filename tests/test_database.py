"""
Unit tests for database operations.
"""

import pytest
import tempfile
from pathlib import Path

from src.database.db_manager import DatabaseManager


@pytest.fixture
def db_manager():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    manager = DatabaseManager(db_path)
    yield manager
    
    # Cleanup
    db_path.unlink()


def test_database_initialization(db_manager):
    """Test database is initialized correctly."""
    assert db_manager.db_path.exists()


def test_create_user(db_manager):
    """Test creating a user."""
    user_id = db_manager.create_user("testuser", "hashed_password")
    assert user_id is not None
    assert user_id > 0


def test_get_user_by_username(db_manager):
    """Test retrieving user by username."""
    db_manager.create_user("testuser", "hashed_password")
    user = db_manager.get_user_by_username("testuser")
    
    assert user is not None
    assert user['username'] == "testuser"
    assert user['password_hash'] == "hashed_password"


def test_create_duplicate_user(db_manager):
    """Test creating duplicate user returns None."""
    db_manager.create_user("testuser", "hashed_password")
    user_id = db_manager.create_user("testuser", "another_hash")
    assert user_id is None


def test_create_config(db_manager):
    """Test creating user configuration."""
    user_id = db_manager.create_user("testuser", "hashed_password")
    
    success = db_manager.create_or_update_config(
        user_id,
        monitor_interval=60,
        keywords=["test", "keyword"],
        wechat_config={"recipient": "friend"},
        reference_images=["/path/to/image.png"]
    )
    
    assert success is True


def test_get_config(db_manager):
    """Test retrieving user configuration."""
    user_id = db_manager.create_user("testuser", "hashed_password")
    
    db_manager.create_or_update_config(
        user_id,
        monitor_interval=120,
        keywords=["test"],
        wechat_config={"recipient": "friend"}
    )
    
    config = db_manager.get_config(user_id)
    
    assert config is not None
    assert config['monitor_interval'] == 120
    assert config['keywords'] == ["test"]
    assert config['wechat_config'] == {"recipient": "friend"}


def test_update_config(db_manager):
    """Test updating user configuration."""
    user_id = db_manager.create_user("testuser", "hashed_password")
    
    # Create initial config
    db_manager.create_or_update_config(user_id, keywords=["old"])
    
    # Update config
    db_manager.create_or_update_config(user_id, keywords=["new"])
    
    config = db_manager.get_config(user_id)
    assert config['keywords'] == ["new"]


def test_create_alert(db_manager):
    """Test creating an alert."""
    user_id = db_manager.create_user("testuser", "hashed_password")
    
    alert_id = db_manager.create_alert(
        user_id,
        detected_keyword="violation",
        screenshot_path="/path/to/screenshot.png",
        detection_method="ocr",
        alert_sent=True
    )
    
    assert alert_id is not None
    assert alert_id > 0


def test_get_recent_alerts(db_manager):
    """Test retrieving recent alerts."""
    user_id = db_manager.create_user("testuser", "hashed_password")
    
    # Create multiple alerts
    for i in range(5):
        db_manager.create_alert(
            user_id,
            detected_keyword=f"keyword{i}",
            detection_method="ocr"
        )
    
    alerts = db_manager.get_recent_alerts(user_id, limit=3)
    
    assert len(alerts) == 3
    # Should be in descending order by created_at
    assert alerts[0]['detected_keyword'] == "keyword4"


def test_get_alert_stats(db_manager):
    """Test getting alert statistics."""
    user_id = db_manager.create_user("testuser", "hashed_password")
    
    # Create alerts
    db_manager.create_alert(user_id, alert_sent=True)
    db_manager.create_alert(user_id, alert_sent=True)
    db_manager.create_alert(user_id, alert_sent=False)
    
    stats = db_manager.get_alert_stats(user_id, days=7)
    
    assert stats['total_alerts'] == 3
    assert stats['alerts_sent'] == 2
