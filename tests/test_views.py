import pytest
from datetime import date

from django.shortcuts import reverse
from rest_framework.test import APIClient

from map.models import CommunityArea, RestaurantPermit


@pytest.mark.django_db
def test_map_data_view():
    # Create some test community areas
    area1 = CommunityArea.objects.create(name="Beverly", area_id="1")
    area2 = CommunityArea.objects.create(name="Lincoln Park", area_id="2")

    # Test permits for Beverly
    RestaurantPermit.objects.create(
        community_area_id=area1.area_id, issue_date=date(2021, 1, 15)
    )
    RestaurantPermit.objects.create(
        community_area_id=area1.area_id, issue_date=date(2021, 2, 20)
    )

    # Test permits for Lincoln Park
    RestaurantPermit.objects.create(
        community_area_id=area2.area_id, issue_date=date(2021, 3, 10)
    )
    RestaurantPermit.objects.create(
        community_area_id=area2.area_id, issue_date=date(2021, 2, 14)
    )
    RestaurantPermit.objects.create(
        community_area_id=area2.area_id, issue_date=date(2021, 6, 22)
    )

    # Query the map data endpoint
    client = APIClient()
    response = client.get(reverse("map_data"), {"year": 2021})

    # TODO: Complete the test by asserting that the /map-data/ endpoint
    # returns the correct number of permits for Beverly and Lincoln 
    # Park in 2021
    assert response.status_code == 200

    response_data = {item["name"]: item["num_permits"] for item in response.json()}

    assert response_data["Beverly"] == 2
    assert response_data["Lincoln Park"] == 3


@pytest.mark.django_db
def test_map_data_view_invalid_year():
    # Test with invalid year (non-integer)
    client = APIClient()
    response = client.get(reverse("map_data"), {"year": "not_a_number"})
    assert response.status_code == 400

    # Test with year outside valid range (before 2016)
    response = client.get(reverse("map_data"), {"year": 2015})
    assert response.status_code == 400

    # Test with year outside valid range (after 2026)
    response = client.get(reverse("map_data"), {"year": 2027})
    assert response.status_code == 400
