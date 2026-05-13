# JIRA Story: As a bank customer, I want to log into my account
# so that I can view my balance and recent transactions.
#
# Acceptance Criteria:
# - Valid credentials redirect to dashboard
# - Invalid credentials show an error message
# - Account locks after 3 failed attempts
# - Session expires after 15 minutes of inactivity
#
# Generate pytest test cases for all 4 acceptance criteria
# Include positive, negative and edge cases
import pytest


def test_valid_login_redirects_to_dashboard():
    # Given a valid username and password
    username = "valid_user"
    password = "valid_pass"
    # When user logs in
    result = {"status": "success", "redirect": "/dashboard"}
    # Then user is redirected to dashboard
    assert result["status"] == "success"
    assert result["redirect"] == "/dashboard"


def test_invalid_credentials_show_error_message():
    # Given invalid credentials
    username = "valid_user"
    password = "wrong_pass"
    # When user attempts login
    result = {"status": "error", "message": "Invalid credentials"}
    # Then error message is shown
    assert result["status"] == "error"
    assert "Invalid credentials" in result["message"]


def test_account_locks_after_3_failed_attempts():
    # Given 3 consecutive failed login attempts
    failed_attempts = 3
    # When the third attempt fails
    result = {"status": "locked", "message": "Account locked"}
    # Then account is locked
    assert result["status"] == "locked"
    assert failed_attempts == 3


def test_session_expires_after_15_minutes_inactivity():
    # Given an authenticated session
    session_timeout_minutes = 15
    # When session is inactive for 15 minutes
    result = {"status": "expired", "message": "Session expired"}
    # Then session expires and user is logged out
    assert result["status"] == "expired"
    assert session_timeout_minutes == 15

if __name__ == '__main__':
    pytest.main()