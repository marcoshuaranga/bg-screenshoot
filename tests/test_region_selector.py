"""Tests for region_selector.py"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.region_selector import RegionSelector


class TestRegionSelector:
    """Test RegionSelector class - Limited to non-GUI logic"""

    def test_initialization(self):
        """Test RegionSelector initialization"""
        selector = RegionSelector()

        assert selector.root is None
        assert selector.canvas is None
        assert selector.start_x is None
        assert selector.start_y is None
        assert selector.rect is None
        assert selector.region is None

    def test_cancel_method(self):
        """Test cancel method sets region to None"""
        selector = RegionSelector()
        selector.region = (100, 100, 200, 200)

        # Mock root to avoid actual GUI destruction
        selector.root = Mock()
        selector._cancel()

        assert selector.region is None
        selector.root.destroy.assert_called_once()

    def test_select_fullscreen_method(self):
        """Test select_fullscreen method sets region to None"""
        selector = RegionSelector()
        selector.region = (100, 100, 200, 200)

        # Mock root to avoid actual GUI destruction
        selector.root = Mock()
        selector._select_fullscreen()

        assert selector.region is None  # None means fullscreen
        selector.root.destroy.assert_called_once()

    def test_on_press_sets_coordinates(self):
        """Test _on_press sets start coordinates"""
        selector = RegionSelector()
        selector.canvas = MagicMock()

        event = Mock()
        event.x = 150
        event.y = 200

        selector._on_press(event)

        assert selector.start_x == 150
        assert selector.start_y == 200
        assert selector.rect is not None  # Rectangle created

    def test_on_release_valid_region(self):
        """Test _on_release with valid region"""
        selector = RegionSelector()
        selector.root = Mock()
        selector.rect = True
        selector.start_x = 100
        selector.start_y = 150

        event = Mock()
        event.x = 500
        event.y = 450

        selector._on_release(event)

        # Result should be set (x, y, width, height)
        assert selector.region == (100, 150, 400, 300)
        selector.root.destroy.assert_called_once()

    def test_on_release_too_small_cancels(self):
        """Test _on_release with region too small"""
        selector = RegionSelector()
        selector.root = Mock()
        selector.rect = True
        selector.start_x = 100
        selector.start_y = 150

        event = Mock()
        event.x = 105  # Only 5 pixels wide
        event.y = 155

        selector._on_release(event)

        # Should cancel (too small)
        assert selector.region is None
        selector.root.destroy.assert_called_once()

    def test_on_release_inverted_coordinates(self):
        """Test _on_release handles inverted drag (right-to-left, bottom-to-top)"""
        selector = RegionSelector()
        selector.root = Mock()
        selector.rect = True
        selector.start_x = 500
        selector.start_y = 400

        event = Mock()
        event.x = 100  # Dragged left
        event.y = 150  # Dragged up

        selector._on_release(event)

        # Should normalize coordinates
        assert selector.region == (100, 150, 400, 250)
        selector.root.destroy.assert_called_once()

    @pytest.mark.skip(reason="Requires full GUI initialization with tkinter.mainloop()")
    def test_select_region_integration(self):
        """Integration test for select_region - requires manual interaction"""
        # This would require actual GUI interaction and is better tested manually
        pass
