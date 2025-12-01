from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.comum.validators import validar_cpf

from ..models import (
    PessoaFisica, Endereco, Contato, Documento, Anexo,
    PessoaFisicaEndereco, PessoaFisicaContato, PessoaFisicaDocumento
)

from .enderecos import PessoaFisicaEnderecoNestedSerializer, PessoaFisicaEnderecoListSerializer
from .contatos import PessoaFisicaContatoNestedSerializer, PessoaFisicaContatoListSerializer
from .documentos import PessoaFisicaDocumentoNestedSerializer, PessoaFisicaDocumentoListSerializer
from .anexos import AnexoSerializer, AnexoNestedSerializer


class PessoaFisicaSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Pessoa Física (GET)."""

    cpf_formatado = serializers.ReadOnlyField()

    # Campos aninhados para exibição completa
    enderecos = PessoaFisicaEnderecoListSerializer(many=True, read_only=True, source='enderecos_vinculados')
    contatos = PessoaFisicaContatoListSerializer(many=True, read_only=True, source='contatos_vinculados')
    documentos = PessoaFisicaDocumentoListSerializer(many=True, read_only=True, source='documentos_vinculados')
    anexos = AnexoSerializer(many=True, read_only=True) # Anexos usa GFK por exceção

    class Meta:
            model = PessoaFisica
            fields = '__all__' # (Resumido para brevidade, mantenha seus campos)

class PessoaFisicaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de Pessoa Física com dados aninhados (POST/PUT).
    """

    enderecos = PessoaFisicaEnderecoNestedSerializer(
        many=True, required=False, allow_empty=True, source='enderecos_vinculados'
    )
    contatos = PessoaFisicaContatoNestedSerializer(
        many=True, required=False, allow_empty=True, source='contatos_vinculados'
    )
    documentos = PessoaFisicaDocumentoNestedSerializer(
        many=True, required=False, allow_empty=True, source='documentos_vinculados'
    )
    anexos = AnexoNestedSerializer(
        many=True, required=False, allow_empty=True, source='anexos_vinculados' # Se houver source
    )

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

    def create(self, validated_data):
        enderecos_data = validated_data.pop('enderecos_vinculados', [])
        contatos_data = validated_data.pop('contatos_vinculados', [])
        documentos_data = validated_data.pop('documentos_vinculados', [])
        anexos_data = validated_data.pop('anexos_vinculados', []) # Manter para GFK se necessário

        pessoa_fisica = PessoaFisica.objects.create(**validated_data)

        # Criar endereços vinculados
        for endereco_data in enderecos_data:
            endereco_id = endereco_data.pop('endereco_id', None)
            if endereco_id:
                # Vínculo a um endereço existente
                endereco = Endereco.objects.get(id=endereco_id)
            else:
                # Criação de um novo endereço
                endereco = Endereco.objects.create(
                    logradouro=endereco_data.pop('logradouro'),
                    numero=endereco_data.pop('numero', None),
                    complemento=endereco_data.pop('complemento', None),
                    bairro=endereco_data.pop('bairro', None),
                    cidade=endereco_data.pop('cidade'),
                    estado=endereco_data.pop('estado'),
                    cep=endereco_data.pop('cep'),
                    pais=endereco_data.pop('pais', 'Brasil')
                )
            PessoaFisicaEndereco.objects.create(pessoa_fisica=pessoa_fisica, endereco=endereco, **endereco_data)

        # Criar contatos vinculados
        for contato_data in contatos_data:
            contato_id = contato_data.pop('contato_id', None)
            if contato_id:
                # Vínculo a um contato existente
                contato = Contato.objects.get(id=contato_id)
            else:
                # Criação de um novo contato
                contato = Contato.objects.create(
                    tipo=contato_data.pop('tipo'),
                    valor=contato_data.pop('valor'),
                    tem_whatsapp=contato_data.pop('tem_whatsapp', False)
                )
            PessoaFisicaContato.objects.create(pessoa_fisica=pessoa_fisica, contato=contato, **contato_data)

        # Criar documentos vinculados
        for documento_data in documentos_data:
            documento_id = documento_data.pop('documento_id', None)
            if documento_id:
                # Vínculo a um documento existente
                documento = Documento.objects.get(id=documento_id)
            else:
                # Criação de um novo documento
                # Supondo que 'arquivo' é tratado separadamente ou o DocumentoCreateSerializer cuida disso
                documento = Documento.objects.create(
                    tipo=documento_data.pop('tipo'),
                    descricao=documento_data.pop('descricao', None),
                    data_emissao=documento_data.pop('data_emissao', None),
                    data_validade=documento_data.pop('data_validade', None),
                    # 'arquivo', 'nome_original', 'mimetype', 'tamanho' seriam tratados aqui se fosse um upload direto
                )
            PessoaFisicaDocumento.objects.create(pessoa_fisica=pessoa_fisica, documento=documento, **documento_data)

        # Para anexos, a lógica de GFK deve ser mantida, se houver.
        # Este é um exemplo simplificado, a implementação real pode exigir FileField ou ImageField.
        for anexo_data in anexos_data:
            Anexo.objects.create(object_id=pessoa_fisica.id, content_type_name='pessoafisica', **anexo_data)

        return pessoa_fisica

    def update(self, instance, validated_data):
        # Implementar a lógica de atualização para os campos aninhados
        # Esta parte é mais complexa e envolveria identificar quais itens foram adicionados/removidos/modificados
        # Para o escopo atual, focaremos principalmente na criação.

        # Exemplo básico para campos diretos da PessoaFisica
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
