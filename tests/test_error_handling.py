"""Tests for error handling and retry logic"""

from unittest.mock import Mock, patch

import pytest
from googleapiclient.errors import HttpError

from src.screenshot_tray import ErrorType, classify_error, retry_with_backoff


class TestErrorClassification:
    """Test error classification"""

    def test_classify_network_error(self):
        """Test network error classification"""
        error = Exception("Connection timeout")
        assert classify_error(error) == ErrorType.NETWORK

        error = Exception("network error occurred")
        assert classify_error(error) == ErrorType.NETWORK

    def test_classify_auth_error(self):
        """Test authentication error classification"""
        error = Exception("invalid credentials")
        assert classify_error(error) == ErrorType.AUTH

        error = Exception("token expired")
        assert classify_error(error) == ErrorType.AUTH

    def test_classify_http_401_error(self):
        """Test HTTP 401 error classification"""
        resp = Mock()
        resp.status = 401
        error = HttpError(resp, b"Unauthorized")

        result = classify_error(error)
        assert result == ErrorType.AUTH

    def test_classify_http_403_quota_error(self):
        """Test HTTP 403 quota error classification"""
        resp = Mock()
        resp.status = 403
        error = HttpError(resp, b"Quota exceeded")

        result = classify_error(error)
        assert result == ErrorType.QUOTA

    def test_classify_http_403_permission_error(self):
        """Test HTTP 403 permission error classification"""
        resp = Mock()
        resp.status = 403
        error = HttpError(resp, b"Permission denied")

        result = classify_error(error)
        assert result == ErrorType.AUTH

    def test_classify_http_500_error(self):
        """Test HTTP 500+ error classification"""
        resp = Mock()
        resp.status = 503
        error = HttpError(resp, b"Service unavailable")

        result = classify_error(error)
        assert result == ErrorType.NETWORK

    def test_classify_unknown_error(self):
        """Test unknown error classification"""
        error = Exception("Something weird happened")
        assert classify_error(error) == ErrorType.UNKNOWN


class TestRetryWithBackoff:
    """Test retry with exponential backoff"""

    def test_success_on_first_try(self):
        """Test successful operation on first attempt"""
        mock_func = Mock(return_value="success")

        result = retry_with_backoff(mock_func, max_retries=3)

        assert result == "success"
        assert mock_func.call_count == 1

    def test_success_after_retries(self):
        """Test successful operation after failures"""
        attempts = [0]

        def flaky_func():
            attempts[0] += 1
            if attempts[0] < 3:
                raise Exception("Network error")
            return "success"

        result = retry_with_backoff(flaky_func, max_retries=3, base_delay=0.01)

        assert result == "success"
        assert attempts[0] == 3

    def test_fails_after_max_retries(self):
        """Test failure after exhausting retries"""
        mock_func = Mock(side_effect=Exception("Persistent error"))

        with pytest.raises(Exception, match="Persistent error"):
            retry_with_backoff(mock_func, max_retries=3, base_delay=0.01)

        assert mock_func.call_count == 3

    def test_no_retry_on_auth_error(self):
        """Test that auth errors are not retried"""
        resp = Mock()
        resp.status = 401
        error = HttpError(resp, b"Unauthorized")

        mock_func = Mock(side_effect=error)

        with pytest.raises(HttpError):
            retry_with_backoff(mock_func, max_retries=3, base_delay=0.01)

        assert mock_func.call_count == 1  # No retries

    def test_no_retry_on_quota_error(self):
        """Test that quota errors are not retried"""
        resp = Mock()
        resp.status = 403
        error = HttpError(resp, b"Quota exceeded")

        mock_func = Mock(side_effect=error)

        with pytest.raises(HttpError):
            retry_with_backoff(mock_func, max_retries=3, base_delay=0.01)

        assert mock_func.call_count == 1  # No retries

    def test_exponential_backoff_timing(self, monkeypatch):
        """Test that backoff delays are exponential"""
        delays = []

        def mock_sleep(seconds):
            delays.append(seconds)

        monkeypatch.setattr("time.sleep", mock_sleep)

        mock_func = Mock(side_effect=[Exception("Network error"), Exception("Network error"), "success"])

        result = retry_with_backoff(mock_func, max_retries=3, base_delay=1)

        assert result == "success"
        assert len(delays) == 2  # 2 delays between 3 attempts
        assert delays[0] == 1  # First delay: 1 * 2^0
        assert delays[1] == 2  # Second delay: 1 * 2^1
