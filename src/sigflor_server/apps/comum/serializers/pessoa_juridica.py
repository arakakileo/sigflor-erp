from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import PessoaJuridica

from .enderecos import EnderecoSerializer, EnderecoNestedSerializer
from .contatos import ContatoSerializer, ContatoNestedSerializer
from .documentos import DocumentoSerializer, DocumentoNestedSerializer
from .anexos import AnexoSerializer, AnexoNestedSerializer
from apps.comum.validators import validar_cnpj


class PessoaJuridicaListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens (sem dados aninhados)."""
    cnpj_formatado = serializers.ReadOnlyField()

    class Meta:
        model = PessoaJuridica
        fields = [
            'id', 'razao_social', 'nome_fantasia', 'cnpj_formatado', 
            'situacao_cadastral'
        ]

class PessoaJuridicaSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Pessoa Jurídica com dados completos."""

    cnpj_formatado = serializers.ReadOnlyField()

    # Adicionamos os campos aninhados (Read Only para GET)
    enderecos = EnderecoSerializer(many=True, read_only=True)
    contatos = ContatoSerializer(many=True, read_only=True)
    documentos = DocumentoSerializer(many=True, read_only=True)
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
            'inscricao_municipal',
            'porte',
            'natureza_juridica',
            'data_abertura',
            'atividade_principal',
            'atividades_secundarias',
            'situacao_cadastral',
            'observacoes',
            'enderecos',
            'contatos',
            'documentos',
            'anexos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'cnpj_formatado', 'created_at', 'updated_at']

    def validate_cnpj(self, value):
        """Remove formatação do CNPJ."""
        return ''.join(filter(str.isdigit, value))

class PessoaJuridicaCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de Pessoa Jurídica com dados aninhados."""

    enderecos = EnderecoNestedSerializer(many=True, required=True, allow_empty=True)
    contatos = ContatoNestedSerializer(many=True, required=True, allow_empty=True)
    documentos = DocumentoNestedSerializer(many=True, required=True, allow_empty=True)
    anexos = AnexoNestedSerializer(many=True, required=True, allow_empty=True)

    class Meta:
        model = PessoaJuridica
        fields = [
            'razao_social', 
            'nome_fantasia', 
            'cnpj',
            'inscricao_estadual', 
            'inscricao_municipal', 
            'porte',
            'natureza_juridica', 
            'data_abertura', 
            'atividade_principal',
            'atividades_secundarias', 
            'situacao_cadastral', 
            'observacoes',
            'enderecos', 
            'contatos', 
            'documentos', 
            'anexos'
        ]
        extra_kwargs = {
                    'cnpj': {
                        'max_length': 18,
                        'validators': []
                    }
                }

    def validate_cnpj(self, value):
            cleaned_value = ''.join(filter(str.isdigit, value))
            try:
                validar_cnpj(cleaned_value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.messages)
            return cleaned_value
