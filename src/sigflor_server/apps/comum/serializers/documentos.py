from rest_framework import serializers

from ..models import Documento, PessoaFisicaDocumento, PessoaJuridicaDocumento


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para Documento."""

    vencido = serializers.ReadOnlyField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Documento
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'descricao',
            'arquivo',
            'nome_original',
            'mimetype',
            'tamanho',
            'data_emissao',
            'data_validade',
            'vencido',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'nome_original', 'mimetype', 'tamanho', 'vencido',
            'tipo_display', 'created_at', 'updated_at'
        ]


class DocumentoCreateSerializer(serializers.Serializer):
    """Serializer para criação de Documento com upload de arquivo."""

    tipo = serializers.ChoiceField(choices=Documento.Tipo.choices)
    descricao = serializers.CharField(required=False, allow_blank=True)
    arquivo = serializers.FileField()
    data_emissao = serializers.DateField(required=False, allow_null=True)
    data_validade = serializers.DateField(required=False, allow_null=True)
    principal = serializers.BooleanField(default=False)


class PessoaFisicaDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para vínculo PessoaFisica-Documento."""

    documento = DocumentoSerializer(read_only=True)
    documento_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = PessoaFisicaDocumento
        fields = [
            'id',
            'pessoa_fisica',
            'documento',
            'documento_id',
            'principal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'documento', 'created_at', 'updated_at']


class PessoaFisicaDocumentoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de documentos de PessoaFisica."""

    documento = DocumentoSerializer(read_only=True)

    class Meta:
        model = PessoaFisicaDocumento
        fields = [
            'id',
            'documento',
            'principal',
        ]


class PessoaFisicaDocumentoNestedSerializer(PessoaFisicaDocumentoSerializer):
    id = serializers.UUIDField(required=False)
    # Campos do documento
    tipo = serializers.ChoiceField(choices=Documento.Tipo.choices, required=False)
    descricao = serializers.CharField(required=False)

    class Meta(PessoaFisicaDocumentoSerializer.Meta):
        read_only_fields = ['created_at', 'updated_at']


class PessoaJuridicaDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para vínculo PessoaJuridica-Documento."""

    documento = DocumentoSerializer(read_only=True)
    documento_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = PessoaJuridicaDocumento
        fields = [
            'id',
            'pessoa_juridica',
            'documento',
            'documento_id',
            'principal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'documento', 'created_at', 'updated_at']


class PessoaJuridicaDocumentoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de documentos de PessoaJuridica."""

    documento = DocumentoSerializer(read_only=True)

    class Meta:
        model = PessoaJuridicaDocumento
        fields = [
            'id',
            'documento',
            'principal',
        ]


class PessoaJuridicaDocumentoNestedSerializer(PessoaJuridicaDocumentoSerializer):
    id = serializers.UUIDField(required=False)
    tipo = serializers.ChoiceField(choices=Documento.Tipo.choices, required=False)
    descricao = serializers.CharField(required=False)

    class Meta(PessoaJuridicaDocumentoSerializer.Meta):
        read_only_fields = ['created_at', 'updated_at']
