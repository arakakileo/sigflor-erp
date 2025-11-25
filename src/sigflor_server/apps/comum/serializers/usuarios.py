from rest_framework import serializers

from ..models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Usuário."""

    nome_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'nome_completo',
            'pessoa_fisica',
            'ativo',
            'is_staff',
            'is_superuser',
            'last_login',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'nome_completo', 'last_login', 'created_at', 'updated_at'
        ]

    def get_nome_completo(self, obj):
        return obj.get_full_name()


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de Usuário."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'pessoa_fisica',
            'ativo',
            'is_staff',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
