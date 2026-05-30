"""Tests for Circuit Breaker pattern in screenshot_tray.py"""

from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from src.screenshot_tray import CircuitBreaker, CircuitState


class TestCircuitBreaker:
    """Test CircuitBreaker class"""

    @pytest.fixture
    def circuit_breaker(self):
        """Create a circuit breaker instance"""
        return CircuitBreaker(failure_threshold=3, timeout_duration=60, success_threshold=2)

    def test_initial_state(self, circuit_breaker):
        """Test circuit breaker starts in CLOSED state"""
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0

    def test_successful_call(self, circuit_breaker):
        """Test successful function call"""

        def success_func():
            return "success"

        result = circuit_breaker.call(success_func)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0

    def test_failed_call(self, circuit_breaker):
        """Test failed function call"""

        def fail_func():
            raise RuntimeError("Test error")

        with pytest.raises(RuntimeError):
            circuit_breaker.call(fail_func)

        assert circuit_breaker.failure_count == 1
        assert circuit_breaker.state == CircuitState.CLOSED  # Still closed after 1 failure

    def test_opens_after_threshold(self, circuit_breaker):
        """Test circuit opens after failure threshold"""

        def fail_func():
            raise RuntimeError("Test error")

        # Fail 3 times (threshold)
        for _ in range(3):
            with pytest.raises(RuntimeError):
                circuit_breaker.call(fail_func)

        assert circuit_breaker.state == CircuitState.OPEN
        assert circuit_breaker.failure_count == 3

    def test_skips_call_when_open(self, circuit_breaker):
        """Test that calls are skipped when circuit is OPEN"""

        def fail_func():
            raise RuntimeError("Test error")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                circuit_breaker.call(fail_func)

        # Try to call again - should return False without calling func
        call_count = 0

        def counting_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = circuit_breaker.call(counting_func)
        assert not result
        assert call_count == 0  # Function was not called

    @freeze_time("2026-05-27 12:00:00")
    def test_half_open_after_timeout(self, circuit_breaker):
        """Test circuit transitions to HALF_OPEN after timeout"""

        def fail_func():
            raise RuntimeError("Test error")

        # Open the circuit
        with freeze_time("2026-05-27 12:00:00"):
            for _ in range(3):
                with pytest.raises(RuntimeError):
                    circuit_breaker.call(fail_func)

        assert circuit_breaker.state == CircuitState.OPEN

        # Move time forward past timeout
        with freeze_time("2026-05-27 12:01:30"):  # 90 seconds later

            def success_func():
                return "success"

            result = circuit_breaker.call(success_func)
            assert result == "success"
            assert circuit_breaker.state == CircuitState.HALF_OPEN

    def test_closes_after_success_threshold(self, circuit_breaker):
        """Test circuit closes after success threshold in HALF_OPEN"""
        # Open the circuit
        circuit_breaker.state = CircuitState.OPEN
        circuit_breaker.failure_count = 3
        circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=100)

        def success_func():
            return "success"

        # First success -> HALF_OPEN
        result = circuit_breaker.call(success_func)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.HALF_OPEN
        assert circuit_breaker.success_count == 1

        # Second success -> CLOSED
        result = circuit_breaker.call(success_func)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.success_count == 0
        assert circuit_breaker.failure_count == 0

    def test_reopens_on_failure_in_half_open(self, circuit_breaker):
        """Test circuit stays HALF_OPEN on first failure, opens after threshold"""
        circuit_breaker.state = CircuitState.HALF_OPEN
        circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=100)

        def fail_func():
            raise RuntimeError("Test error")

        # First failure in HALF_OPEN - stays HALF_OPEN (failure_count=1, threshold=3)
        with pytest.raises(RuntimeError):
            circuit_breaker.call(fail_func)

        assert circuit_breaker.state == CircuitState.HALF_OPEN
        assert circuit_breaker.failure_count == 1

        # Two more failures to reach threshold
        for _ in range(2):
            with pytest.raises(RuntimeError):
                circuit_breaker.call(fail_func)

        # Now it should be OPEN
        assert circuit_breaker.state == CircuitState.OPEN
        assert circuit_breaker.failure_count == 3

    def test_manual_reset(self, circuit_breaker):
        """Test manual reset of circuit breaker"""

        # Open the circuit
        def fail_func():
            raise RuntimeError("Test error")

        for _ in range(3):
            with pytest.raises(RuntimeError):
                circuit_breaker.call(fail_func)

        assert circuit_breaker.state == CircuitState.OPEN

        # Manual reset
        circuit_breaker.reset()

        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0
        assert circuit_breaker.last_failure_time is None

    def test_get_status(self, circuit_breaker):
        """Test status reporting"""
        # CLOSED state
        status = circuit_breaker.get_status()
        assert "✅" in status or "Online" in status.lower()

        # OPEN state
        circuit_breaker.state = CircuitState.OPEN
        circuit_breaker.last_failure_time = datetime.now()
        status = circuit_breaker.get_status()
        assert "⚠️" in status or "offline" in status.lower()

        # HALF_OPEN state
        circuit_breaker.state = CircuitState.HALF_OPEN
        status = circuit_breaker.get_status()
        assert "🔄" in status or "testing" in status.lower()
