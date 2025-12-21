"""
Integration tests for BarberAppClient.

These tests hit the real API and require credentials.
Tests are automatically skipped if credentials are not set.

To run integration tests:
    set BARBER_ID=your_shop_id
    set USERNAME=your_username
    set PASSWORD=your_password
    pytest tests/test_integration.py -v
"""
import pytest


class TestIntegrationAPI:
    """Integration tests that hit the real API."""
    
    def test_connection(self, real_client):
        """Test that we can connect to the API."""
        # Just calling init should work
        result = real_client.init()
        assert result is not None
    
    def test_get_barbers_returns_list(self, real_client):
        """Test that barbers endpoint returns valid data."""
        barbers = real_client.get_barbers()
        
        assert isinstance(barbers, list)
        assert len(barbers) > 0
        
        # Each barber should have required fields
        for barber in barbers:
            assert "Nome" in barber
            assert "Id" in barber
    
    def test_get_services_returns_dict(self, real_client):
        """Test that services endpoint returns valid structure."""
        services = real_client.get_services()
        
        assert isinstance(services, dict)
        assert "Nome" in services
        assert "Prezzo" in services
        assert len(services["Nome"]) > 0
    
    def test_get_schedule_returns_list(self, real_client):
        """Test that schedule endpoint returns data."""
        schedule = real_client.get_schedule()
        
        assert isinstance(schedule, list)
        # Schedule might be empty on some days
    
    def test_get_reservations(self, real_client):
        """Test fetching reservations doesn't error."""
        confirmed = real_client.get_confirmed_reservations()
        pending = real_client.get_pending_reservations()
        
        # Both should be lists (possibly empty)
        assert isinstance(confirmed, list)
        assert isinstance(pending, list)
    
    def test_service_name_lookup(self, real_client):
        """Test service name lookup with real data."""
        services = real_client.get_services()
        
        # Get first non-empty service
        for i, name in enumerate(services["Nome"]):
            if name:
                result = real_client.get_service_name(i)
                assert result == name
                break
    
    def test_calculate_slots_for_available_day(self, real_client):
        """Test slot calculation with real schedule."""
        barbers = real_client.get_barbers()
        
        # Find first non-hidden barber
        barber_name = None
        for b in barbers:
            if not b.get("Nascosto", False):
                barber_name = b["Nome"]
                break
        
        if barber_name:
            days = real_client.get_available_slots_for_barber(barber_name)
            
            if days:
                # Calculate slots for first available day
                date_str = days[0]["Gi"]
                slots = real_client.calculate_available_slots(date_str, barber_name, 0)
                
                # Slots should be list of tuples
                assert isinstance(slots, list)
                for slot in slots:
                    assert len(slot) == 2
                    time_str, duration = slot
                    assert ":" in time_str
                    assert isinstance(duration, int)
