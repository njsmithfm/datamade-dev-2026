import os

from django.shortcuts import render
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from map.models import CommunityArea
from map.serializers import CommunityAreaSerializer


class Home(TemplateView):
    template_name = "map/home_page.html"


class MapDataView(APIView):
    def get(self, request):
        year = request.query_params.get("year")
        
        if year is not None:
            try:
                year_int = int(year)
            except ValueError:
                raise ValidationError({"year": "Year must be a valid integer."})
            
            # Check if year is in valid range (2016-2026)
            if year_int < 2016 or year_int > 2026:
                raise ValidationError({"year": "Year must be between 2016 and 2026."})
        
        community_areas = CommunityArea.objects.all()
        serializer = CommunityAreaSerializer(
            community_areas,
            many=True,
            context={"year": year},
        )
        return Response(serializer.data)


def robots_txt(request):
    return render(
        request,
        "map/robots.txt",
        {"ALLOW_CRAWL": True if os.getenv("ALLOW_CRAWL") == "True" else False},
        content_type="text/plain",
    )


def page_not_found(request, exception, template_name="404.html"):
    return render(request, template_name, status=404)


def server_error(request, template_name="500.html"):
    return render(request, template_name, status=500)
