"""
Unit tests for BarberAppClient.

These tests use mocked HTTP responses and don't require real credentials.
"""
import base64
import json
from datetime import datetime

import pytest
import responses


# =============================================================================
# MOCK DATA (duplicated from conftest.py for direct import)
# =============================================================================

MOCK_BARBERS = [
    {
        "Id": 1,
        "Nome": "Giovanni",
        "Nascosto": False,
        "MinutiTaglio": 45,
        "MinutiTaglioArr": [45, 15, 15, 15, 30, 45, 30, 30, 60, 30, 45]
    },
    {
        "Id": 2,
        "Nome": "Marco",
        "Nascosto": False,
        "MinutiTaglio": 45,
        "MinutiTaglioArr": [45, 15, 15, 15, 30, 45, 30, 30, 60, 30, 45]
    },
    {
        "Id": 3,
        "Nome": "Hidden",
        "Nascosto": True,
        "MinutiTaglio": 45,
        "MinutiTaglioArr": [45, 15, 15, 15, 30, 45, 30, 30, 60, 30, 45]
    }
]

MOCK_SERVICES = {
    "Nome": [
        "Taglio normale + shampoo",
        "Colore",
        "Sopracciglia",
        "Barba corta",
        "",
        "Taglio pettine e forbice",
        "",
        "",
        "",
        "",
        "Taglio + barba"
    ],
    "Prezzo": [13.0, 0.0, 4.0, 5.0, 0.0, 15.0, 0.0, 0.0, 0.0, 0.0, 18.0],
    "Descrizione": ["", "", "", "", "", "", "", "", "", "", ""]
}

MOCK_SCHEDULE = [
    {
        "Gi": "231225",
        "Pa": "Giovanni",
        "Fe": False,
        "Pr": [
            {"Or": "2312251115", "Sl": 45},
            {"Or": "2312251200", "Sl": 30},
            {"Or": "2312251530", "Sl": 60}
        ]
    },
    {
        "Gi": "231225",
        "Pa": "Marco",
        "Fe": False,
        "Pr": [
            {"Or": "2312251000", "Sl": 45}
        ]
    },
    {
        "Gi": "241225",
        "Pa": "Giovanni",
        "Fe": True,
        "Pr": []
    }
]

MOCK_CONFIRMED_RESERVATIONS = [
    {"Or": "2312251115", "Pa": "Giovanni", "Ti": 0}
]

MOCK_PENDING_RESERVATIONS = [
    {"Or": "241225", "Pa": "Giovanni"}
]


class TestEncoding:
    """Tests for encoding/decoding methods."""
    
    def test_encode_simple_string(self, mock_client):
        """Test base64 encoding."""
        result = mock_client._encode("hello")
        assert result == base64.b64encode(b"hello").decode()
    
    def test_encode_with_special_chars(self, mock_client):
        """Test encoding with special characters."""
        payload = "user/pass/action/"
        result = mock_client._encode(payload)
        # Should be valid base64
        decoded = base64.b64decode(result)
        assert decoded.decode() == payload
    
    def test_decode_empty_string(self, mock_client):
        """Test decoding empty string returns empty."""
        assert mock_client._decode("") == ""
    
    def test_decode_with_padding(self, mock_client):
        """Test decoding handles missing padding."""
        # Base64 without proper padding
        original = "test data"
        encoded = base64.b64encode(original.encode()).decode()
        # Remove padding
        encoded_no_padding = encoded.rstrip("=")
        
        result = mock_client._decode(encoded_no_padding)
        assert result == original
    
    def test_decode_properly_padded(self, mock_client):
        """Test decoding works with proper padding."""
        original = "test data"
        encoded = base64.b64encode(original.encode()).decode()
        
        result = mock_client._decode(encoded)
        assert result == original


class TestPayloadBuilding:
    """Tests for payload construction."""
    
    def test_build_payload_basic(self, mock_client):
        """Test basic payload structure."""
        result = mock_client._build_payload("TestAction")
        expected = "test_shop_id/test_user/test_pass/TestAction/"
        assert result == expected
    
    def test_build_payload_with_args(self, mock_client):
        """Test payload with additional arguments."""
        result = mock_client._build_payload("TestAction", "arg1", 123, "arg3")
        expected = "test_shop_id/test_user/test_pass/TestAction/arg1/123/arg3/"
        assert result == expected
    
    def test_build_payload_empty_args(self, mock_client):
        """Test payload handles empty string args."""
        result = mock_client._build_payload("Action", "", "value", "")
        expected = "test_shop_id/test_user/test_pass/Action//value//"
        assert result == expected


class TestDateFormatting:
    """Tests for date/time formatting and parsing."""
    
    def test_format_datetime(self, mock_client):
        """Test datetime formatting for API (DDMMYYHHmm)."""
        dt = datetime(2025, 12, 24, 11, 15)
        result = mock_client.format_datetime(dt)
        assert result == "2412251115"
    
    def test_format_date(self, mock_client):
        """Test date formatting for API (DDMMYY)."""
        dt = datetime(2025, 12, 24)
        result = mock_client.format_date(dt)
        assert result == "241225"
    
    def test_parse_datetime(self, mock_client):
        """Test parsing datetime from API format."""
        result = mock_client.parse_datetime("2412251115")
        expected = datetime(2025, 12, 24, 11, 15)
        assert result == expected
    
    def test_parse_date(self, mock_client):
        """Test parsing date from API format."""
        result = mock_client.parse_date("241225")
        expected = datetime(2025, 12, 24)
        assert result == expected
    
    def test_format_and_parse_roundtrip(self, mock_client):
        """Test that format and parse are inverse operations."""
        dt = datetime(2025, 6, 15, 9, 30)
        formatted = mock_client.format_datetime(dt)
        parsed = mock_client.parse_datetime(formatted)
        assert parsed == dt


class TestHelperMethods:
    """Tests for helper methods that process cached data."""
    
    def test_get_service_name(self, mock_client):
        """Test getting service name by ID."""
        mock_client._services = MOCK_SERVICES
        assert mock_client.get_service_name(0) == "Taglio normale + shampoo"
        assert mock_client.get_service_name(10) == "Taglio + barba"
    
    def test_get_service_name_invalid_id(self, mock_client):
        """Test fallback for invalid service ID."""
        mock_client._services = MOCK_SERVICES
        result = mock_client.get_service_name(999)
        assert result == "Servizio #999"
    
    def test_get_service_price(self, mock_client):
        """Test getting service price by ID."""
        mock_client._services = MOCK_SERVICES
        assert mock_client.get_service_price(0) == 13.0
        assert mock_client.get_service_price(10) == 18.0
    
    def test_get_service_price_invalid_id(self, mock_client):
        """Test fallback price for invalid ID."""
        mock_client._services = MOCK_SERVICES
        result = mock_client.get_service_price(999)
        assert result == 0.0
    
    def test_get_service_duration(self, mock_client):
        """Test getting service duration for specific barber."""
        mock_client._barbers = MOCK_BARBERS
        # Giovanni has service 0 = 45 min, service 2 = 15 min
        assert mock_client.get_service_duration("Giovanni", 0) == 45
        assert mock_client.get_service_duration("Giovanni", 2) == 15
    
    def test_get_service_duration_unknown_barber(self, mock_client):
        """Test fallback duration for unknown barber."""
        mock_client._barbers = MOCK_BARBERS
        result = mock_client.get_service_duration("Unknown", 0)
        assert result == 45  # Default fallback


class TestAvailableSlots:
    """Tests for slot availability calculation."""
    
    def test_get_available_slots_for_barber(self, mock_client):
        """Test filtering schedule by barber."""
        mock_client._schedule = MOCK_SCHEDULE
        
        slots = mock_client.get_available_slots_for_barber("Giovanni")
        # Should get only Giovanni's non-holiday slots
        assert len(slots) == 1
        assert slots[0]["Gi"] == "231225"
    
    def test_get_available_slots_excludes_holidays(self, mock_client):
        """Test that holidays (Fe=True) are excluded."""
        mock_client._schedule = MOCK_SCHEDULE
        
        slots = mock_client.get_available_slots_for_barber("Giovanni")
        # 24/12 is marked as holiday
        dates = [s["Gi"] for s in slots]
        assert "241225" not in dates
    
    def test_calculate_available_slots(self, mock_client):
        """Test calculating time slots for a specific date."""
        mock_client._schedule = MOCK_SCHEDULE
        mock_client._barbers = MOCK_BARBERS
        
        # Service 0 = 45 min duration
        slots = mock_client.calculate_available_slots("231225", "Giovanni", 0)
        
        # Should filter to slots with duration >= 45
        times = [t for t, d in slots]
        assert "11:15" in times  # 45 min slot
        assert "15:30" in times  # 60 min slot
        # 12:00 has only 30 min, should be excluded
        assert "12:00" not in times
    
    def test_calculate_available_slots_shorter_service(self, mock_client):
        """Test that shorter services see more available slots."""
        mock_client._schedule = MOCK_SCHEDULE
        mock_client._barbers = MOCK_BARBERS
        
        # Service 2 = 15 min duration
        slots = mock_client.calculate_available_slots("231225", "Giovanni", 2)
        
        # All slots should be available (all >= 15 min)
        times = [t for t, d in slots]
        assert "11:15" in times
        assert "12:00" in times
        assert "15:30" in times
    
    def test_calculate_available_slots_no_slots(self, mock_client):
        """Test empty result for date with no slots."""
        mock_client._schedule = MOCK_SCHEDULE
        mock_client._barbers = MOCK_BARBERS
        
        # 24/12 is a holiday with no slots
        slots = mock_client.calculate_available_slots("241225", "Giovanni", 0)
        assert slots == []


class TestWorkingHours:
    """Tests for working hours logic."""
    
    def test_monday_closed(self, mock_client):
        """Monday should be closed."""
        hours = mock_client.get_working_hours(0)  # 0 = Monday
        assert hours == []
    
    def test_sunday_closed(self, mock_client):
        """Sunday should be closed."""
        hours = mock_client.get_working_hours(6)  # 6 = Sunday
        assert hours == []
    
    def test_saturday_hours(self, mock_client):
        """Saturday has continuous hours."""
        hours = mock_client.get_working_hours(5)  # 5 = Saturday
        assert len(hours) == 1
        start, end = hours[0]
        assert start == 8 * 60 + 30  # 8:30
        assert end == 18 * 60  # 18:00
    
    def test_weekday_hours(self, mock_client):
        """Weekdays (Tue-Fri) have split hours."""
        for weekday in [1, 2, 3, 4]:  # Tue-Fri
            hours = mock_client.get_working_hours(weekday)
            assert len(hours) == 2
            # Morning: 8:30-13:00
            assert hours[0] == (8 * 60 + 30, 13 * 60)
            # Afternoon: 15:00-20:00
            assert hours[1] == (15 * 60, 20 * 60)


class TestAPICalls:
    """Tests for API request methods with mocked HTTP."""
    
    @responses.activate
    def test_get_barbers(self, mock_client):
        """Test fetching barbers list."""
        # Prepare mocked response
        response_data = base64.b64encode(json.dumps(MOCK_BARBERS).encode()).decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.get_barbers()
        
        assert len(result) == 3
        assert result[0]["Nome"] == "Giovanni"
    
    @responses.activate
    def test_get_services(self, mock_client):
        """Test fetching services list."""
        response_data = base64.b64encode(json.dumps(MOCK_SERVICES).encode()).decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.get_services()
        
        assert "Nome" in result
        assert "Prezzo" in result
        assert result["Nome"][0] == "Taglio normale + shampoo"
    
    @responses.activate
    def test_get_barbers_caches_result(self, mock_client):
        """Test that barbers are cached after first call."""
        response_data = base64.b64encode(json.dumps(MOCK_BARBERS).encode()).decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        # First call - makes HTTP request
        result1 = mock_client.get_barbers()
        # Second call - should use cache
        result2 = mock_client.get_barbers()
        
        assert result1 == result2
        # Only one HTTP request should have been made
        assert len(responses.calls) == 1
    
    @responses.activate
    def test_book_success(self, mock_client):
        """Test successful booking."""
        response_data = base64.b64encode(b"OK").decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.book("2412251115", 10, "Giovanni")
        
        assert result is True
    
    @responses.activate
    def test_book_failure(self, mock_client):
        """Test failed booking."""
        response_data = base64.b64encode(b"ERROR: Slot not available").decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.book("2412251115", 10, "Giovanni")
        
        assert result is False
    
    @responses.activate
    def test_cancel_success(self, mock_client):
        """Test successful cancellation."""
        response_data = base64.b64encode(b"OK").decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.cancel("2412251115", 10, "Giovanni", 18.0)
        
        assert result is True
    
    @responses.activate
    def test_join_queue_success(self, mock_client):
        """Test joining queue."""
        response_data = base64.b64encode(b"OK").decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.join_queue("241225", "Giovanni", 0)
        
        assert result is True
    
    @responses.activate
    def test_leave_queue_success(self, mock_client):
        """Test leaving queue."""
        response_data = base64.b64encode(b"OK").decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.leave_queue("241225")
        
        assert result is True
    
    @responses.activate
    def test_get_confirmed_reservations(self, mock_client):
        """Test fetching confirmed reservations."""
        response_data = base64.b64encode(
            json.dumps(MOCK_CONFIRMED_RESERVATIONS).encode()
        ).decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.get_confirmed_reservations()
        
        assert len(result) == 1
        assert result[0]["Pa"] == "Giovanni"
    
    @responses.activate
    def test_get_pending_reservations(self, mock_client):
        """Test fetching pending reservations."""
        response_data = base64.b64encode(
            json.dumps(MOCK_PENDING_RESERVATIONS).encode()
        ).decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client.get_pending_reservations()
        
        assert len(result) == 1
        assert result[0]["Pa"] == "Giovanni"
    
    @responses.activate
    def test_request_json_empty_response(self, mock_client):
        """Test handling of empty API response."""
        response_data = base64.b64encode(b"").decode()
        responses.add(
            responses.POST,
            mock_client.BASE_URL,
            body=response_data,
            status=200
        )
        
        result = mock_client._request_json("SomeAction")
        
        assert result == []
