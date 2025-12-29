"""
Unit tests for authentication module.
"""

import pytest
import tempfile
from pathlib import Path

from src.database.db_manager import DatabaseManager
from src.auth.auth_manager import AuthManager


@pytest.fixture
def db_manager():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    manager = DatabaseManager(db_path)
    yield manager
    
    # Cleanup
    db_path.unlink()


@pytest.fixture
def auth_manager(db_manager):
    """Create auth manager with test database."""
    return AuthManager(db_manager)


def test_register_user(auth_manager):
    """Test user registration."""
    success, message = auth_manager.register("testuser", "password123")
    assert success is True
    assert "成功" in message


def test_register_duplicate_user(auth_manager):
    """Test registering duplicate username."""
    auth_manager.register("testuser", "password123")
    success, message = auth_manager.register("testuser", "password456")
    assert success is False
    assert "已存在" in message


def test_register_short_password(auth_manager):
    """Test registering with short password."""
    success, message = auth_manager.register("testuser", "12345")
    assert success is False
    assert "长度" in message


def test_login_success(auth_manager):
    """Test successful login."""
    auth_manager.register("testuser", "password123")
    success, message = auth_manager.login("testuser", "password123")
    assert success is True
    assert "成功" in message
    assert auth_manager.is_authenticated()


def test_login_wrong_password(auth_manager):
    """Test login with wrong password."""
    auth_manager.register("testuser", "password123")
    success, message = auth_manager.login("testuser", "wrongpassword")
    assert success is False
    assert not auth_manager.is_authenticated()


def test_login_nonexistent_user(auth_manager):
    """Test login with nonexistent user."""
    success, message = auth_manager.login("nonexistent", "password123")
    assert success is False


def test_logout(auth_manager):
    """Test logout."""
    auth_manager.register("testuser", "password123")
    auth_manager.login("testuser", "password123")
    assert auth_manager.is_authenticated()
    
    auth_manager.logout()
    assert not auth_manager.is_authenticated()


def test_get_current_user(auth_manager):
    """Test getting current user."""
    auth_manager.register("testuser", "password123")
    auth_manager.login("testuser", "password123")
    
    user = auth_manager.get_current_user()
    assert user is not None
    assert user['username'] == "testuser"
    assert 'password_hash' not in user  # Should not expose password hash
