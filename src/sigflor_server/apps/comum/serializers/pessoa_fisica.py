from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.comum.validators import validar_cpf

from ..models import PessoaFisica
# Importar tanto os serializers de Leitura quanto os Nested
from .enderecos import EnderecoSerializer, EnderecoNestedSerializer
from .contatos import ContatoSerializer, ContatoNestedSerializer
from .documentos import DocumentoSerializer, DocumentoNestedSerializer
from .anexos import AnexoSerializer, AnexoNestedSerializer


class PessoaFisicaSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Pessoa Física (GET)."""

    cpf_formatado = serializers.ReadOnlyField()

    # Campos aninhados para exibição completa
    enderecos = EnderecoSerializer(many=True, read_only=True)
    contatos = ContatoSerializer(many=True, read_only=True)
    documentos = DocumentoSerializer(many=True, read_only=True)
    anexos = AnexoSerializer(many=True, read_only=True)

    class Meta:
        model = PessoaFisica
        fields = [
            'id', 
            'nome_completo', 
            'cpf', 
            'cpf_formatado', 
            'rg', 
            'orgao_emissor',
            'data_nascimento', 
            'sexo', 
            'estado_civil', 
            'nacionalidade',
            'naturalidade', 
            'possui_deficiencia', 
            'observacoes',
            'enderecos', 
            'contatos', 
            'documentos', 
            'anexos',
            'created_at', 
            'updated_at',
        ]
        read_only_fields = ['id', 'cpf_formatado', 'created_at', 'updated_at']


class PessoaFisicaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de Pessoa Física com dados aninhados (POST/PUT).
    """
    
    enderecos = EnderecoNestedSerializer(many=True, required=True, allow_empty=True)
    contatos = ContatoNestedSerializer(many=True, required=True, allow_empty=True)
    documentos = DocumentoNestedSerializer(many=True, required=True, allow_empty=True)
    anexos = AnexoNestedSerializer(many=True, required=True, allow_empty=True)

    class Meta:
        model = PessoaFisica
        fields = [
            'nome_completo', 'cpf', 'rg', 'orgao_emissor', 'data_nascimento',
            'sexo', 'estado_civil', 'nacionalidade', 'naturalidade', 'observacoes',
            'enderecos', 'contatos', 'documentos', 'anexos'
        ]
        extra_kwargs = {
            'cpf': {
                'max_length': 14,
                'validators': [] # Desativa validação automática na entrada bruta
            }
        }

    def validate_cpf(self, value):
        """Remove formatação do CPF e valida manualmente."""
        cleaned_value = ''.join(filter(str.isdigit, value))
        
        try:
            validar_cpf(cleaned_value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
            
        return cleaned_value