from rest_framework import serializers

from apps.autenticacao.serializers import UsuarioResumoSerializer
from ..models import Contato, PessoaFisicaContato, PessoaJuridicaContato, FilialContato
from ..models.enums import TipoContato


class ContatoSerializer(serializers.ModelSerializer):

    valor_formatado = serializers.ReadOnlyField()
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

    class Meta:
        model = Contato
        fields = [
            'id',
            'tipo',
            'valor',
            'valor_formatado',
            'tem_whatsapp',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'valor_formatado', 'created_at', 'updated_at']


# ==============================================================================
# 1. PESSOA FÍSICA (Vínculos)
# ==============================================================================

class PessoaFisicaContatoSerializer(serializers.ModelSerializer):

    contato = ContatoSerializer(read_only=True)
    contato_id = serializers.UUIDField(write_only=True, required=False)
    tem_whatsapp = serializers.BooleanField(source='contato.tem_whatsapp', read_only=True)
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

    class Meta:
        model = PessoaFisicaContato
        fields = [
            'id',
            'contato',
            'contato_id',
            'principal',
            'contato_emergencia',
            'tem_whatsapp',
            'updated_by',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'contato', 'created_at', 'updated_at']


class PessoaFisicaContatoListSerializer(serializers.ModelSerializer):

    contato = ContatoSerializer(read_only=True)

    class Meta:
        model = PessoaFisicaContato
        fields = [
            'id',
            'contato',
            'principal',
            'contato_emergencia',
        ]


class PessoaFisicaContatoNestedSerializer(PessoaFisicaContatoSerializer):
    
    id = serializers.UUIDField(required=False)
    tipo = serializers.ChoiceField(choices=TipoContato.choices, required=True)
    valor = serializers.CharField(required=True)
    tem_whatsapp = serializers.BooleanField(required=False)

    class Meta(PessoaFisicaContatoSerializer.Meta):
        fields = PessoaFisicaContatoSerializer.Meta.fields + ['tipo', 'valor', 'tem_whatsapp']
        read_only_fields = ['created_at', 'updated_at', 'contato']

    def validate(self, data):
        tipo = data.get('tipo')
        if tipo == TipoContato.CELULAR:
            if 'tem_whatsapp' not in data:
                raise serializers.ValidationError({"tem_whatsapp": "Obrigatório para celular."})
        return data


# ==============================================================================
# 2. PESSOA JURÍDICA (Vínculos)
# ==============================================================================

class PessoaJuridicaContatoSerializer(serializers.ModelSerializer):

    contato = ContatoSerializer(read_only=True)
    contato_id = serializers.UUIDField(write_only=True, required=False)
    tem_whatsapp = serializers.BooleanField(source='contato.tem_whatsapp', read_only=True)
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

    class Meta:
        model = PessoaJuridicaContato
        fields = [
            'id',
            'contato',
            'contato_id',
            'principal',
            'tem_whatsapp',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'contato', 'created_at', 'updated_at']


class PessoaJuridicaContatoListSerializer(serializers.ModelSerializer):

    contato = ContatoSerializer(read_only=True)

    class Meta:
        model = PessoaJuridicaContato
        fields = [
            'contato',
            'principal',
        ]


class PessoaJuridicaContatoNestedSerializer(PessoaJuridicaContatoSerializer):

    id = serializers.UUIDField(required=False)
    tipo = serializers.ChoiceField(choices=TipoContato.choices, required=True)
    valor = serializers.CharField(required=True)
    tem_whatsapp = serializers.BooleanField(required=False)

    class Meta(PessoaJuridicaContatoSerializer.Meta):
        fields = PessoaJuridicaContatoSerializer.Meta.fields + ['tipo', 'valor', 'tem_whatsapp']
        read_only_fields = ['created_at', 'updated_at', 'contato']

    def validate(self, data):
        item_id = data.get('id')
        if not item_id:
            erros = {}
            campos_obrigatorios = ['tipo', 'valor'] 
            for campo in campos_obrigatorios:
                if campo not in data:
                    erros[campo] = "Este campo é obrigatório para novos contatos."
            if erros:
                raise serializers.ValidationError(erros)

        tipo = data.get('tipo')
        if tipo == TipoContato.CELULAR:
            if 'tem_whatsapp' not in data:
                raise serializers.ValidationError({"tem_whatsapp": "Obrigatório para celular."})
        return data


# ==============================================================================
# 3. FILIAL (Vínculos)
# ==============================================================================

class FilialContatoSerializer(serializers.ModelSerializer):

    contato = ContatoSerializer(read_only=True)
    contato_id = serializers.UUIDField(write_only=True, required=False)
    tem_whatsapp = serializers.BooleanField(source='contato.tem_whatsapp', read_only=True)
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

    class Meta:
        model = FilialContato
        fields = [
            'id',
            'contato',
            'contato_id',
            'principal',
            'tem_whatsapp',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'contato', 'created_at', 'updated_at']


class FilialContatoListSerializer(serializers.ModelSerializer):

    contato = ContatoSerializer(read_only=True)

    class Meta:
        model = FilialContato
        fields = [
            'contato',
            'principal',
        ]


class FilialContatoNestedSerializer(FilialContatoSerializer):

    id = serializers.UUIDField(required=False)
    tipo = serializers.ChoiceField(choices=TipoContato.choices, required=True)
    valor = serializers.CharField(required=True)
    tem_whatsapp = serializers.BooleanField(required=False)

    class Meta(FilialContatoSerializer.Meta):
        fields = FilialContatoSerializer.Meta.fields + ['tipo', 'valor', 'tem_whatsapp']
        read_only_fields = ['created_at', 'updated_at', 'contato']

    def validate(self, data):
        tipo = data.get('tipo')
        if tipo == TipoContato.CELULAR:
            if 'tem_whatsapp' not in data:
                raise serializers.ValidationError({"tem_whatsapp": "Obrigatório para celular."})
        return data