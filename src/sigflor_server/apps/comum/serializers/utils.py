
from rest_framework import serializers

class SoftDeleteListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        try:
            data = data.filter(deleted_at__isnull=True)
        except AttributeError:
            pass
            
        return super().to_representation(data)