from rest_framework import serializers
from django.contrib.auth.models import Permission

class PermissaoSerializer(serializers.ModelSerializer):
    modulo = serializers.CharField(source='content_type.app_label', read_only=True)
    entidade = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Permission
        fields = [
            'id', 
            'name',
            'codename',
            'modulo',
            'entidade',
        ]