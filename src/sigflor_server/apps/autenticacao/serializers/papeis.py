from rest_framework import serializers
from django.contrib.auth.models import Permission

from ..models import Papel
from .permissoes import PermissaoSerializer
from apps.autenticacao.models import Usuario


class PapelSerializer(serializers.ModelSerializer):
    permissoes = PermissaoSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.pessoa_fisica.nome_completo', read_only=True)

    class Meta:
        model = Papel
        fields = [
            'id', 
            'nome', 
            'descricao', 
            'permissoes',
            'created_at',
            'created_by_name'
        ]

class PapelCreateSerializer(serializers.ModelSerializer):
    permissoes = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = Papel
        fields = ['nome', 'descricao', 'permissoes']

    def validate_nome(self, value):
        qs = Papel.objects.filter(nome__iexact=value, deleted_at__isnull=True)
        if qs.exists():
            raise serializers.ValidationError("Já existe um papel com este nome.")
        return value

class PapelUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Papel
        fields = ['nome', 'descricao']

    def validate_nome(self, value):
        qs = Papel.objects.filter(nome__iexact=value, deleted_at__isnull=True)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
            
        if qs.exists():
            raise serializers.ValidationError("Já existe um papel com este nome.")
        return value

class PapelPermissoesBatchSerializer(serializers.Serializer):

    permissoes_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=True,
        allow_empty=False,
        error_messages={
            'permissao_nao_existe': 'A permissão com ID {pk_value} não existe.',
            'lista_vazia': 'A lista de permissões não pode estar vazia.'
        }
    )

class PapelUsuariosListSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='pessoa_fisica.nome_completo', read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'nome', 'ativo']