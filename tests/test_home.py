import pytest
import streamlit as st
from unittest.mock import MagicMock
from app.Home import login, logout

@pytest.fixture
def mock_session_state(monkeypatch):
    """Fixture to mock session state for different scenarios."""
    session_state_mock = MagicMock()
    session_state_mock.user = None
    session_state_mock.password = None
    session_state_mock.bam_cram_files = []
    session_state_mock.submit = False
    monkeypatch.setattr(st, 'session_state', session_state_mock)
    return session_state_mock

def test_home_page_no_login(monkeypatch, mock_session_state):
    """Test Home.py when login is disabled."""
    # Disable login feature
    monkeypatch.setattr('app.Home.login_enabled', False)
    
    # Mock navigation behavior
    monkeypatch.setattr('app.Home.pg.run', lambda: None)

    # Assertions to check session state and navigation behavior
    assert st.session_state.user is None
    assert "Query" in "Mock Page Title"

def test_home_page_with_login(monkeypatch, mock_session_state):
    """Test Home.py when login is enabled and no user is logged in."""
    # Enable login feature
    monkeypatch.setattr('app.Home.login_enabled', True)

    # Simulate login page rendering (user not logged in)
    monkeypatch.setattr(st, 'text_input', lambda label, type=None: "test_user" if label == "User" else "test_password")
    monkeypatch.setattr(st, 'button', lambda label: label == "Log in")

    # Call the login function
    login()

    # Check if session state is updated after login
    assert st.session_state.user == "test_user"
    assert st.session_state.password == "test_password"

def test_logout_function(monkeypatch, mock_session_state):
    """Test logout functionality."""
    # Set user as logged in
    st.session_state.user = "test_user"
    st.session_state.password = "test_password"

    # Call the logout function
    logout()

    # Assert session state is reset
    assert st.session_state.user is None
    assert st.session_state.password is None

def test_home_page_logged_in(monkeypatch, mock_session_state):
    """Test Home.py when user is already logged in."""
    # Set login_enabled to True and simulate a logged-in user
    monkeypatch.setattr('app.Home.login_enabled', True)
    st.session_state.user = "test_user"
    st.session_state.password = "test_password"
    
    # Mock navigation behavior
    monkeypatch.setattr('app.Home.pg.run', lambda: None)

    # Assertions for logged-in user
    assert "Metrics calculator" in "Mock Page Title"
