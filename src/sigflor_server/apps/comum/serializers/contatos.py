from rest_framework import serializers

from ..models import Contato, PessoaFisicaContato, PessoaJuridicaContato, FilialContato


class ContatoSerializer(serializers.ModelSerializer):
    """Serializer para Contato."""

    valor_formatado = serializers.ReadOnlyField()

    class Meta:
        model = Contato
        fields = [
            'id',
            'tipo',
            'valor',
            'valor_formatado',
            'tem_whatsapp',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'valor_formatado', 'created_at', 'updated_at']


class PessoaFisicaContatoSerializer(serializers.ModelSerializer):
    """Serializer para vínculo PessoaFisica-Contato."""

    contato = ContatoSerializer(read_only=True)
    contato_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = PessoaFisicaContato
        fields = [
            'id',
            # 'pessoa_fisica',
            'contato',
            'contato_id',
            'principal',
            'contato_emergencia',
            'tem_whatsapp',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'contato', 'created_at', 'updated_at']


class PessoaFisicaContatoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de contatos de PessoaFisica."""

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
    # Campos do contato para permitir escrita aninhada
    tipo = serializers.ChoiceField(choices=Contato.Tipo.choices, required=True)
    valor = serializers.CharField(required=True)
    tem_whatsapp = serializers.BooleanField(required=False) # Não obrigatório por padrão

    class Meta(PessoaFisicaContatoSerializer.Meta):
        # Adicionamos tem_whatsapp aos campos
        fields = PessoaFisicaContatoSerializer.Meta.fields + ['tipo', 'valor', 'tem_whatsapp']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Validação condicional para WhatsApp."""
        tipo = data.get('tipo')
        
        # Se for CELULAR, exige que o campo tem_whatsapp esteja presente
        if tipo == Contato.Tipo.CELULAR:
            if 'tem_whatsapp' not in data:
                raise serializers.ValidationError({
                    "tem_whatsapp": "Este campo é obrigatório quando o tipo de contato é Celular."
                })
        
        return data


class PessoaJuridicaContatoSerializer(serializers.ModelSerializer):
    """Serializer para vínculo PessoaJuridica-Contato."""

    contato = ContatoSerializer(read_only=True)
    contato_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = PessoaJuridicaContato
        fields = [
            'id',
            # 'pessoa_juridica',
            'contato',
            'contato_id',
            'principal',
            'tem_whatsapp',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'contato', 'created_at', 'updated_at']


class PessoaJuridicaContatoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de contatos de PessoaJuridica."""

    contato = ContatoSerializer(read_only=True)

    class Meta:
        model = PessoaJuridicaContato
        fields = [
            # 'id',
            'contato',
            'principal',
        ]


class PessoaJuridicaContatoNestedSerializer(PessoaJuridicaContatoSerializer):
    id = serializers.UUIDField(required=False)
    tipo = serializers.ChoiceField(choices=Contato.Tipo.choices, required=True)
    valor = serializers.CharField(required=True)
    tem_whatsapp = serializers.BooleanField(required=False)

    class Meta(PessoaJuridicaContatoSerializer.Meta):
        fields = PessoaJuridicaContatoSerializer.Meta.fields + ['tipo', 'valor', 'tem_whatsapp']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Validação condicional para WhatsApp."""
        tipo = data.get('tipo')
        
        if tipo == Contato.Tipo.CELULAR:
            if 'tem_whatsapp' not in data:
                raise serializers.ValidationError({
                    "tem_whatsapp": "Este campo é obrigatório quando o tipo de contato é Celular."
                })
        
        return data


class FilialContatoSerializer(serializers.ModelSerializer):
    """Serializer para vínculo Filial-Contato."""

    contato = ContatoSerializer(read_only=True)
    contato_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = FilialContato
        fields = [
            'id',
            'filial',
            'contato',
            'contato_id',
            'principal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'contato', 'created_at', 'updated_at']


class FilialContatoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de contatos de Filial."""

    contato = ContatoSerializer(read_only=True)

    class Meta:
        model = FilialContato
        fields = [
            'id',
            'contato',
            'principal',
        ]


class FilialContatoNestedSerializer(FilialContatoSerializer):
    id = serializers.UUIDField(required=False)
    tipo = serializers.ChoiceField(choices=Contato.Tipo.choices, required=True)
    valor = serializers.CharField(required=True)
    tem_whatsapp = serializers.BooleanField(required=False)

    class Meta(FilialContatoSerializer.Meta):
        fields = FilialContatoSerializer.Meta.fields + ['tipo', 'valor', 'tem_whatsapp']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Validação condicional para WhatsApp."""
        tipo = data.get('tipo')
        
        if tipo == Contato.Tipo.CELULAR:
            if 'tem_whatsapp' not in data:
                raise serializers.ValidationError({
                    "tem_whatsapp": "Este campo é obrigatório quando o tipo de contato é Celular."
                })
        
        return data