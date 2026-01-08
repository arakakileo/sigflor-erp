from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import PessoaJuridica
from ..models.enums import SituacaoCadastral
from ..validators import validar_cnpj

from .enderecos import PessoaJuridicaEnderecoNestedSerializer, PessoaJuridicaEnderecoSerializer
from .contatos import PessoaJuridicaContatoNestedSerializer, PessoaJuridicaContatoListSerializer
from .documentos import PessoaJuridicaDocumentoNestedSerializer, PessoaJuridicaDocumentoListSerializer
from .anexos import AnexoSerializer, AnexoNestedSerializer


class PessoaJuridicaListSerializer(serializers.ModelSerializer):
    cnpj_formatado = serializers.ReadOnlyField()
    situacao_cadastral_display = serializers.CharField(
        source='get_situacao_cadastral_display', read_only=True
    )

    class Meta:
        model = PessoaJuridica
        fields = [
            'id',
            'razao_social',
            'nome_fantasia',
            'cnpj_formatado',
            'situacao_cadastral',
            'situacao_cadastral_display',
        ]

class PessoaJuridicaSerializer(serializers.ModelSerializer):

    cnpj_formatado = serializers.ReadOnlyField()
    situacao_cadastral_display = serializers.CharField(
        source='get_situacao_cadastral_display', read_only=True
    )
    enderecos = PessoaJuridicaEnderecoSerializer(many=True, read_only=True, source='enderecos_vinculados')
    contatos = PessoaJuridicaContatoListSerializer(many=True, read_only=True, source='contatos_vinculados')
    documentos = PessoaJuridicaDocumentoListSerializer(many=True, read_only=True, source='documentos_vinculados')
    anexos = AnexoSerializer(many=True, read_only=True)

    class Meta:
        model = PessoaJuridica
        fields = [
            'id',
            'razao_social',
            'nome_fantasia',
            'cnpj',
            'cnpj_formatado',
            'inscricao_estadual',
            'data_abertura',
            'situacao_cadastral',
            'situacao_cadastral_display',
            'observacoes',
            'enderecos',
            'contatos',
            'documentos',
            'anexos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'cnpj_formatado', 'situacao_cadastral_display',
            'created_at', 'updated_at'
        ]

    def validate_cnpj(self, value):
        return ''.join(filter(str.isdigit, value))

class PessoaJuridicaCreateSerializer(serializers.Serializer):

    razao_social = serializers.CharField(max_length=200)
    nome_fantasia = serializers.CharField(max_length=200, required=False, allow_blank=True)
    cnpj = serializers.CharField(max_length=18)
    inscricao_estadual = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_abertura = serializers.DateField(required=False, allow_null=True)
    situacao_cadastral = serializers.ChoiceField(
        choices=SituacaoCadastral.choices,
        default=SituacaoCadastral.ATIVA,
        required=False
    )
    observacoes = serializers.CharField(required=False, allow_blank=True)

    enderecos = PessoaJuridicaEnderecoNestedSerializer(many=True, required=True, allow_empty=False)
    contatos = PessoaJuridicaContatoNestedSerializer(many=True, required=True, allow_empty=False)
    documentos = PessoaJuridicaDocumentoNestedSerializer(many=True, required=True, allow_empty=True)
    anexos = AnexoNestedSerializer(many=True, required=False, allow_empty=True)

    def validate_cnpj(self, value):
        cleaned_value = ''.join(filter(str.isdigit, value))
        try:
            validar_cnpj(cleaned_value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return cleaned_value

class PessoaJuridicaUpdateSerializer(serializers.Serializer):

    razao_social = serializers.CharField(max_length=200, required=False)
    nome_fantasia = serializers.CharField(max_length=200, required=False, allow_blank=True)
    inscricao_estadual = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_abertura = serializers.DateField(required=False, allow_null=True)
    situacao_cadastral = serializers.ChoiceField(
        choices=SituacaoCadastral.choices,
        required=False
    )
    observacoes = serializers.CharField(required=False, allow_blank=True)

    enderecos = PessoaJuridicaEnderecoNestedSerializer(
        many=True, required=False, allow_empty=True, source='enderecos_vinculados'
    )
    contatos = PessoaJuridicaContatoNestedSerializer(
        many=True, required=False, allow_empty=True, source='contatos_vinculados'
    )
    documentos = PessoaJuridicaDocumentoNestedSerializer(
        many=True, required=False, allow_empty=True, source='documentos_vinculados'
    )
    anexos = AnexoNestedSerializer(
        many=True, required=False, allow_empty=True
    )