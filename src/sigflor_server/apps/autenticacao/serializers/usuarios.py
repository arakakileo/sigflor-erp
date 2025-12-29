from rest_framework import serializers
from django.contrib.auth.models import Permission 
from apps.autenticacao.models import Usuario, Papel
from apps.comum.models import Filial

class UsuarioListSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='first_name', read_only=True)
    sobrenome = serializers.CharField(source='last_name', read_only=True)
    
    lista_papeis = serializers.SlugRelatedField(
        source='papeis',
        many=True, 
        read_only=True, 
        slug_field='nome'
    )
    
    lista_filiais = serializers.SlugRelatedField(
        source='allowed_filiais', 
        many=True, 
        read_only=True, 
        slug_field='nome'
    )

    lista_permissoes_diretas = serializers.SlugRelatedField(
        source='permissoes_diretas',
        many=True,
        read_only=True,
        slug_field='name'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'username', 
            'email', 
            'nome', 
            'sobrenome',
            'ativo', 
            'lista_papeis', 
            'lista_filiais', 
            'lista_permissoes_diretas',
            'last_login'
        ]

class UsuarioCreateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='first_name', required=True)
    sobrenome = serializers.CharField(source='last_name', required=False)
    
    senha = serializers.CharField(
        source='password', 
        write_only=True, 
        required=True 
    )

    lista_papeis_ids = serializers.PrimaryKeyRelatedField(
        source='papeis',
        many=True, 
        queryset=Papel.objects.filter(deleted_at__isnull=True),
        required=False
    )
    
    lista_filiais_ids = serializers.PrimaryKeyRelatedField(
        source='allowed_filiais',
        many=True,
        queryset=Filial.objects.all(),
        required=False
    )

    lista_permissoes_diretas_ids = serializers.PrimaryKeyRelatedField(
        source='permissoes_diretas',
        many=True,
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 
            'email', 
            'nome', 
            'sobrenome', 
            'senha',
            'lista_papeis_ids', 
            'lista_filiais_ids', 
            'lista_permissoes_diretas_ids',
            'ativo'
        ]

class UsuarioUpdateSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='first_name', required=False)
    
    sobrenome = serializers.CharField(source='last_name', required=False)

    lista_papeis_ids = serializers.PrimaryKeyRelatedField(
        source='papeis',
        many=True, 
        queryset=Papel.objects.filter(deleted_at__isnull=True),
        required=False
    )
    
    lista_filiais_ids = serializers.PrimaryKeyRelatedField(
        source='allowed_filiais',
        many=True,
        queryset=Filial.objects.all(),
        required=False
    )

    lista_permissoes_diretas_ids = serializers.PrimaryKeyRelatedField(
        source='permissoes_diretas',
        many=True,
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 
            'email', 
            'nome', 
            'sobrenome',
            'lista_papeis_ids', 
            'lista_filiais_ids', 
            'lista_permissoes_diretas_ids',
            'ativo'
        ]

class UsuarioRedefinirSenhaSerializer(serializers.Serializer):
    nova_senha = serializers.CharField(required=True, min_length=6)

class UsuarioAlterarMinhaSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(required=True)
    nova_senha = serializers.CharField(required=True, min_length=6)
    confirmacao_senha = serializers.CharField(required=True)

    def validate(self, dados):
        nova_senha = dados.get('nova_senha')
        confirmacao = dados.get('confirmacao_senha')

        if nova_senha != confirmacao:
            raise serializers.ValidationError({"nova_senha": "A nova senha e a confirmação não conferem."})
        
        return dados