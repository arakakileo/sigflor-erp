from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import (
    PessoaJuridica, SituacaoCadastral, Endereco, Contato, Documento, Anexo,
    PessoaJuridicaEndereco, PessoaJuridicaContato, PessoaJuridicaDocumento
)
from ..validators import validar_cnpj

from .enderecos import PessoaJuridicaEnderecoSerializer, PessoaJuridicaEnderecoListSerializer
from .contatos import PessoaJuridicaContatoSerializer, PessoaJuridicaContatoListSerializer
from .documentos import PessoaJuridicaDocumentoSerializer, PessoaJuridicaDocumentoListSerializer
from .anexos import AnexoSerializer, AnexoNestedSerializer


class PessoaJuridicaListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens (sem dados aninhados)."""
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
    """Serializer para leitura de Pessoa Jurídica com dados completos."""

    cnpj_formatado = serializers.ReadOnlyField()
    situacao_cadastral_display = serializers.CharField(
        source='get_situacao_cadastral_display', read_only=True
    )

    # Campos aninhados para exibição completa
    enderecos = PessoaJuridicaEnderecoListSerializer(many=True, read_only=True, source='enderecos_vinculados')
    contatos = PessoaJuridicaContatoListSerializer(many=True, read_only=True, source='contatos_vinculados')
    documentos = PessoaJuridicaDocumentoListSerializer(many=True, read_only=True, source='documentos_vinculados')
    anexos = AnexoSerializer(many=True, read_only=True) # Anexos usa GFK por exceção

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
        """Remove formatação do CNPJ."""
        return ''.join(filter(str.isdigit, value))


class PessoaJuridicaCreateSerializer(serializers.Serializer):
    """Serializer para criação de Pessoa Jurídica com dados aninhados."""

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

    enderecos = PessoaJuridicaEnderecoSerializer(many=True, required=False, allow_empty=True, source='enderecos_vinculados')
    contatos = PessoaJuridicaContatoSerializer(many=True, required=False, allow_empty=True, source='contatos_vinculados')
    documentos = PessoaJuridicaDocumentoSerializer(many=True, required=False, allow_empty=True, source='documentos_vinculados')
    anexos = AnexoNestedSerializer(many=True, required=False, allow_empty=True)

    def validate_cnpj(self, value):
        """Remove formatação do CNPJ e valida."""
        cleaned_value = ''.join(filter(str.isdigit, value))
        try:
            validar_cnpj(cleaned_value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return cleaned_value

    def create(self, validated_data):
        enderecos_data = validated_data.pop('enderecos_vinculados', [])
        contatos_data = validated_data.pop('contatos_vinculados', [])
        documentos_data = validated_data.pop('documentos_vinculados', [])
        anexos_data = validated_data.pop('anexos_vinculados', [])

        pessoa_juridica = PessoaJuridica.objects.create(**validated_data)

        # Criar endereços vinculados
        for endereco_data in enderecos_data:
            endereco_id = endereco_data.pop('endereco_id', None)
            if endereco_id:
                endereco = Endereco.objects.get(id=endereco_id)
            else:
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
            PessoaJuridicaEndereco.objects.create(pessoa_juridica=pessoa_juridica, endereco=endereco, **endereco_data)

        # Criar contatos vinculados
        for contato_data in contatos_data:
            contato_id = contato_data.pop('contato_id', None)
            if contato_id:
                contato = Contato.objects.get(id=contato_id)
            else:
                contato = Contato.objects.create(
                    tipo=contato_data.pop('tipo'),
                    valor=contato_data.pop('valor'),
                    tem_whatsapp=contato_data.pop('tem_whatsapp', False)
                )
            PessoaJuridicaContato.objects.create(pessoa_juridica=pessoa_juridica, contato=contato, **contato_data)

        # Criar documentos vinculados
        for documento_data in documentos_data:
            documento_id = documento_data.pop('documento_id', None)
            if documento_id:
                documento = Documento.objects.get(id=documento_id)
            else:
                documento = Documento.objects.create(
                    tipo=documento_data.pop('tipo'),
                    descricao=documento_data.pop('descricao', None),
                    data_emissao=documento_data.pop('data_emissao', None),
                    data_validade=documento_data.pop('data_validade', None),
                )
            PessoaJuridicaDocumento.objects.create(pessoa_juridica=pessoa_juridica, documento=documento, **documento_data)

        # Para anexos, a lógica de GFK é mantida
        for anexo_data in anexos_data:
            Anexo.objects.create(object_id=pessoa_juridica.id, content_type_name='pessoajuridica', **anexo_data)

        return pessoa_juridica


class PessoaJuridicaUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de Pessoa Jurídica com dados aninhados."""

    razao_social = serializers.CharField(max_length=200, required=False)
    nome_fantasia = serializers.CharField(max_length=200, required=False, allow_blank=True)
    inscricao_estadual = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_abertura = serializers.DateField(required=False, allow_null=True)
    situacao_cadastral = serializers.ChoiceField(
        choices=SituacaoCadastral.choices,
        required=False
    )
    observacoes = serializers.CharField(required=False, allow_blank=True)

    enderecos = PessoaJuridicaEnderecoSerializer(many=True, required=False, allow_empty=True, source='enderecos_vinculados')
    contatos = PessoaJuridicaContatoSerializer(many=True, required=False, allow_empty=True, source='contatos_vinculados')
    documentos = PessoaJuridicaDocumentoSerializer(many=True, required=False, allow_empty=True, source='documentos_vinculados')
    anexos = AnexoNestedSerializer(many=True, required=False, allow_empty=True)

    def update(self, instance, validated_data):
        enderecos_data = validated_data.pop('enderecos_vinculados', [])
        contatos_data = validated_data.pop('contatos_vinculados', [])
        documentos_data = validated_data.pop('documentos_vinculados', [])
        anexos_data = validated_data.pop('anexos_vinculados', [])

        # Atualiza campos diretos da PessoaJuridica
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Lógica de atualização para endereços aninhados
        for endereco_data in enderecos_data:
            endereco_id = endereco_data.pop('id', None)
            if endereco_id:
                # Tenta atualizar um endereço existente
                try:
                    endereco_vinculo = PessoaJuridicaEndereco.objects.get(id=endereco_id, pessoa_juridica=instance)
                    endereco = endereco_vinculo.endereco
                    for attr, value in endereco_data.items():
                        setattr(endereco, attr, value)
                    endereco.save()
                    # Atualiza os dados do vínculo (tipo, principal)
                    for attr, value in endereco_data.items():
                        if hasattr(endereco_vinculo, attr):
                            setattr(endereco_vinculo, attr, value)
                    endereco_vinculo.save()
                except PessoaJuridicaEndereco.DoesNotExist:
                    # Se o ID do vínculo não existe, pode-se optar por criar um novo ou levantar um erro
                    pass # ou raise serializers.ValidationError("Vínculo de endereço não encontrado")
            else:
                # Cria um novo endereço e vínculo (lógica similar ao método create)
                # É importante ter certeza de que o serializador de escrita lida com a criação/vínculo ou um ID existente
                # Para simplificação, assumimos que se não há ID, é para criar um novo.
                new_endereco_id = endereco_data.pop('endereco_id', None)
                if new_endereco_id:
                    endereco_obj = Endereco.objects.get(id=new_endereco_id)
                else:
                    endereco_obj = Endereco.objects.create(
                        logradouro=endereco_data.pop('logradouro'),
                        numero=endereco_data.pop('numero', None),
                        complemento=endereco_data.pop('complemento', None),
                        bairro=endereco_data.pop('bairro', None),
                        cidade=endereco_data.pop('cidade'),
                        estado=endereco_data.pop('estado'),
                        cep=endereco_data.pop('cep'),
                        pais=endereco_data.pop('pais', 'Brasil')
                    )
                PessoaJuridicaEndereco.objects.create(pessoa_juridica=instance, endereco=endereco_obj, **endereco_data)

        # Lógica de atualização para contatos aninhados
        for contato_data in contatos_data:
            contato_id = contato_data.pop('id', None)
            if contato_id:
                try:
                    contato_vinculo = PessoaJuridicaContato.objects.get(id=contato_id, pessoa_juridica=instance)
                    contato = contato_vinculo.contato
                    for attr, value in contato_data.items():
                        setattr(contato, attr, value)
                    contato.save()
                    for attr, value in contato_data.items():
                        if hasattr(contato_vinculo, attr):
                            setattr(contato_vinculo, attr, value)
                    contato_vinculo.save()
                except PessoaJuridicaContato.DoesNotExist:
                    pass
            else:
                new_contato_id = contato_data.pop('contato_id', None)
                if new_contato_id:
                    contato_obj = Contato.objects.get(id=new_contato_id)
                else:
                    contato_obj = Contato.objects.create(
                        tipo=contato_data.pop('tipo'),
                        valor=contato_data.pop('valor'),
                        tem_whatsapp=contato_data.pop('tem_whatsapp', False)
                    )
                PessoaJuridicaContato.objects.create(pessoa_juridica=instance, contato=contato_obj, **contato_data)

        # Lógica de atualização para documentos aninhados
        for documento_data in documentos_data:
            documento_id = documento_data.pop('id', None)
            if documento_id:
                try:
                    documento_vinculo = PessoaJuridicaDocumento.objects.get(id=documento_id, pessoa_juridica=instance)
                    documento = documento_vinculo.documento
                    for attr, value in documento_data.items():
                        setattr(documento, attr, value)
                    documento.save()
                    for attr, value in documento_data.items():
                        if hasattr(documento_vinculo, attr):
                            setattr(documento_vinculo, attr, value)
                    documento_vinculo.save()
                except PessoaJuridicaDocumento.DoesNotExist:
                    pass
            else:
                new_documento_id = documento_data.pop('documento_id', None)
                if new_documento_id:
                    documento_obj = Documento.objects.get(id=new_documento_id)
                else:
                    documento_obj = Documento.objects.create(
                        tipo=documento_data.pop('tipo'),
                        descricao=documento_data.pop('descricao', None),
                        data_emissao=documento_data.pop('data_emissao', None),
                        data_validade=documento_data.pop('data_validade', None),
                    )
                PessoaJuridicaDocumento.objects.create(pessoa_juridica=instance, documento=documento_obj, **documento_data)

        # Para anexos, a lógica de GFK é mantida
        for anexo_data in anexos_data:
            anexo_id = anexo_data.pop('id', None)
            if anexo_id:
                try:
                    anexo = Anexo.objects.get(id=anexo_id, object_id=instance.id, content_type_name='pessoajuridica')
                    for attr, value in anexo_data.items():
                        setattr(anexo, attr, value)
                    anexo.save()
                except Anexo.DoesNotExist:
                    pass
            else:
                Anexo.objects.create(object_id=instance.id, content_type_name='pessoajuridica', **anexo_data)

        return instance