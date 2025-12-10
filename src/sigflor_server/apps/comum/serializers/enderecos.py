from rest_framework import serializers

from ..models import PessoaFisicaEndereco, PessoaJuridicaEndereco, FilialEndereco, Endereco
from ..models.enums import UF, TipoEndereco


class EnderecoSerializer(serializers.ModelSerializer):
    """Serializer para Endereco."""

    cep_formatado = serializers.ReadOnlyField()
    endereco_completo = serializers.ReadOnlyField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    # Aceita CEP com máscara na entrada (9 chars), limpa para 8
    cep = serializers.CharField(max_length=9)

    class Meta:
        model = Endereco
        fields = [
            'id',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'estado',
            'estado_display',
            'cep',
            'cep_formatado',
            'pais',
            'endereco_completo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'cep_formatado', 'endereco_completo', 'estado_display',
            'created_at', 'updated_at'
        ]

    def validate_cep(self, value):
        """Remove formatação do CEP e valida se restam 8 dígitos."""
        limpo = ''.join(filter(str.isdigit, value))
        if len(limpo) != 8:
            raise serializers.ValidationError("O CEP deve conter 8 dígitos numéricos.")
        return limpo

class EnderecoCreateSerializer(serializers.Serializer):
    """Serializer para criação de endereço com vínculo."""

    logradouro = serializers.CharField(max_length=255)
    numero = serializers.CharField(max_length=20, required=False, allow_blank=True)
    complemento = serializers.CharField(max_length=100, required=False, allow_blank=True)
    bairro = serializers.CharField(max_length=100, required=False, allow_blank=True)
    cidade = serializers.CharField(max_length=100)
    estado = serializers.ChoiceField(choices=UF.choices)
    cep = serializers.CharField(max_length=9)
    pais = serializers.CharField(max_length=50, default='Brasil')
    tipo = serializers.ChoiceField(choices=TipoEndereco.choices, default=TipoEndereco.RESIDENCIAL)
    principal = serializers.BooleanField(default=False)

    def validate_cep(self, value):
        """Remove formatação do CEP e valida se restam 8 dígitos."""
        limpo = ''.join(filter(str.isdigit, value))
        if len(limpo) != 8:
            raise serializers.ValidationError("O CEP deve conter 8 dígitos numéricos.")
        return limpo

class PessoaFisicaEnderecoSerializer(serializers.ModelSerializer):

    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = PessoaFisicaEndereco
        fields = [
            'id',
            'pessoa_fisica',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'endereco', 'tipo_display', 'created_at', 'updated_at']

class PessoaFisicaEnderecoListSerializer(serializers.ModelSerializer):

    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = PessoaFisicaEndereco
        fields = [
            'id',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
        ]

class PessoaFisicaEnderecoNestedSerializer(PessoaFisicaEnderecoSerializer):
    id = serializers.UUIDField(required=False)
    logradouro = serializers.CharField(required=True)
    cidade = serializers.CharField(required=False)
    estado = serializers.CharField(required=False)
    cep = serializers.CharField(required=False)
    bairro = serializers.CharField(required=False)
    numero = serializers.CharField(required=False)
    complemento = serializers.CharField(required=False)
    pais = serializers.CharField(required=False)

    class Meta(PessoaFisicaEnderecoSerializer.Meta):
        fields = [
            'id',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_at',
            'updated_at',
            'logradouro',
            'cidade',
            'estado',
            'cep',
            'bairro',
            'numero',
            'complemento',
            'pais',
        ]
        read_only_fields = ['created_at', 'updated_at']

class PessoaJuridicaEnderecoSerializer(serializers.ModelSerializer):
    """Serializer para vínculo PessoaJuridica-Endereco."""

    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = PessoaJuridicaEndereco
        fields = [
            'id',
            'pessoa_juridica',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'endereco', 'tipo_display', 'created_at', 'updated_at']

class PessoaJuridicaEnderecoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de endereços de PessoaJuridica."""

    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = PessoaJuridicaEndereco
        fields = [
            # 'id',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
        ]

class PessoaJuridicaEnderecoNestedSerializer(PessoaJuridicaEnderecoSerializer):
    id = serializers.UUIDField(required=False)
    logradouro = serializers.CharField(required=True)
    cidade = serializers.CharField(required=False)
    estado = serializers.CharField(required=False)
    cep = serializers.CharField(required=False)
    bairro = serializers.CharField(required=False)
    numero = serializers.CharField(required=False)
    complemento = serializers.CharField(required=False)
    pais = serializers.CharField(required=False)

    class Meta(PessoaJuridicaEnderecoSerializer.Meta):
        fields = [
            'id',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_at',
            'updated_at',
            'logradouro',
            'cidade',
            'estado',
            'cep',
            'bairro',
            'numero',
            'complemento',
            'pais',
        ]
        read_only_fields = ['created_at', 'updated_at']

class FilialEnderecoSerializer(serializers.ModelSerializer):

    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = FilialEndereco
        fields = [
            'filial',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['endereco', 'tipo_display', 'created_at', 'updated_at']

class FilialEnderecoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de endereços de Filial."""

    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = FilialEndereco
        fields = [
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
        ]

class FilialEnderecoNestedSerializer(FilialEnderecoSerializer):
    id = serializers.UUIDField(required=False)
    logradouro = serializers.CharField(required=False)
    cidade = serializers.CharField(required=False)
    estado = serializers.CharField(required=False)
    cep = serializers.CharField(required=False)
    bairro = serializers.CharField(required=False)
    numero = serializers.CharField(required=False)
    complemento = serializers.CharField(required=False)
    pais = serializers.CharField(required=False)

    class Meta(FilialEnderecoSerializer.Meta):
        fields = [
            'id',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_at',
            'updated_at',
            'logradouro',
            'cidade',
            'estado',
            'cep',
            'bairro',
            'numero',
            'complemento',
            'pais',
        ]
        read_only_fields = ['created_at', 'updated_at']