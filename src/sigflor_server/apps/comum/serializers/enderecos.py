from rest_framework import serializers

from apps.autenticacao.serializers import UsuarioResumoSerializer
from ..models import PessoaFisicaEndereco, PessoaJuridicaEndereco, FilialEndereco, Endereco
from ..models.enums import UF, TipoEndereco
from .utils import SoftDeleteListSerializer

class EnderecoSerializer(serializers.ModelSerializer):

    cep_formatado = serializers.ReadOnlyField()
    endereco_completo = serializers.ReadOnlyField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cep = serializers.CharField(max_length=9)
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

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
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'cep_formatado', 'endereco_completo', 'estado_display',
            'created_at', 'updated_at'
        ]

    def validate_cep(self, value):
        limpo = ''.join(filter(str.isdigit, value))
        if len(limpo) != 8:
            raise serializers.ValidationError("O CEP deve conter 8 dígitos numéricos.")
        return limpo

class EnderecoCreateSerializer(serializers.Serializer):

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
        limpo = ''.join(filter(str.isdigit, value))
        if len(limpo) != 8:
            raise serializers.ValidationError("O CEP deve conter 8 dígitos numéricos.")
        return limpo

# ==============================================================================
# 1. PESSOA FÍSICA (Vínculos)
# ==============================================================================

class PessoaFisicaEnderecoSerializer(serializers.ModelSerializer):

    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

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
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'endereco', 'tipo_display', 'created_at', 'updated_at']
        list_serializer_class = SoftDeleteListSerializer

class PessoaFisicaEnderecoNestedSerializer(PessoaFisicaEnderecoSerializer):
    id = serializers.UUIDField(required=False)
    logradouro = serializers.CharField(required=True)
    cidade = serializers.CharField(required=True)
    cep = serializers.CharField(required=True)
    bairro = serializers.CharField(required=True)
    numero = serializers.CharField(required=True)
    pais = serializers.CharField(required=True)
    estado = serializers.ChoiceField(
        choices=UF.choices,
        required=True
    )
    tipo = serializers.ChoiceField(
        choices=TipoEndereco.choices,
        default=TipoEndereco.RESIDENCIAL
    )
    complemento = serializers.CharField(required=False, allow_blank=True)

    class Meta(PessoaFisicaEnderecoSerializer.Meta):
        fields = [
            'id',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_at',
            'updated_at',
            'logradouro', 'cidade', 'estado', 'cep', 
            'bairro', 'numero', 'complemento', 'pais',
        ]
        read_only_fields = ['created_at', 'updated_at', 'endereco', 'tipo_display']

# ==============================================================================
# 2. PESSOA JURÍDICA (Vínculos)
# ==============================================================================

class PessoaJuridicaEnderecoSerializer(serializers.ModelSerializer):
    endereco = EnderecoSerializer()
    tipo_display = serializers.CharField(source='get_tipo_display')
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

    class Meta:
        model = PessoaJuridicaEndereco
        fields = [
            'id',
            'endereco',
            'tipo',
            'tipo_display',
            'principal',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'endereco', 'tipo_display', 'created_at', 'updated_at', 'created_by', 'updated_by']
        list_serializer_class = SoftDeleteListSerializer

class PessoaJuridicaEnderecoNestedSerializer(PessoaJuridicaEnderecoSerializer):
    id = serializers.UUIDField(required=False)
    logradouro = serializers.CharField()
    cidade = serializers.CharField()
    estado = serializers.ChoiceField(
        choices=UF.choices
    )
    cep = serializers.CharField()
    bairro = serializers.CharField()
    numero = serializers.CharField()
    complemento = serializers.CharField(required=False, allow_blank=True)
    pais = serializers.CharField()
    tipo = serializers.ChoiceField(
        choices=TipoEndereco.choices,
        default=TipoEndereco.RESIDENCIAL
    )

    class Meta(PessoaJuridicaEnderecoSerializer.Meta):
        fields = [
            'id',
            'tipo',
            'principal',
            'logradouro',
            'cidade', 
            'estado', 
            'cep',
            'bairro', 
            'numero', 
            'complemento', 
            'pais',
        ]

    def validate(self, attrs):
        item_id = attrs.get('id')
        if not item_id:
            erros = {}
            campos_obrigatorios = ['logradouro', 'cidade', 'estado', 'cep', 'pais']
            for campo in campos_obrigatorios:
                if campo not in attrs:
                    erros[campo] = "Este campo é obrigatório para cadastrar um novo endereço."
            if erros:
                raise serializers.ValidationError(erros)
        return attrs
# ==============================================================================
# 3. FILIAL (Vínculos)
# ==============================================================================

class FilialEnderecoSerializer(serializers.ModelSerializer):
    endereco = EnderecoSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

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
            'logradouro', 'cidade', 'estado', 'cep',
            'bairro', 'numero', 'complemento', 'pais',
        ]
        read_only_fields = ['created_at', 'updated_at']