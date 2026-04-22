from rest_framework import serializers

from map.models import CommunityArea, RestaurantPermit


class CommunityAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityArea
        fields = ["name", "area_id", "num_permits"]

    num_permits = serializers.SerializerMethodField()

    def get_num_permits(self, obj):
        """
        Return the number of permits issued in the given year.
        
        The view validates that year is a valid integer before passing it here,
        so we only need to handle the case where no year is provided.
        """
        year = self.context.get("year")
        if year is None:
            return 0
        
        year = int(year)
        return RestaurantPermit.objects.filter(
            community_area_id=str(obj.area_id),
            issue_date__year=year,
        ).count()