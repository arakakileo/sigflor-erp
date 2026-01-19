from rest_framework import serializers

from apps.autenticacao.serializers import UsuarioResumoSerializer
from ..models import Filial
from ..serializers.enderecos import FilialEnderecoNestedSerializer, FilialEnderecoSerializer
from ..serializers.contatos import FilialContatoNestedSerializer, FilialContatoSerializer
from ..models.enums import StatusFilial


class FilialListSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.ReadOnlyField()

    class Meta:
        model = Filial
        fields = [
            'id',
            'nome',
            'codigo_interno',
            'status',
            'empresa_nome',
        ]

class FilialSerializer(serializers.ModelSerializer):
    is_ativa = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    enderecos = FilialEnderecoSerializer(many=True, read_only=True, source='enderecos_vinculados')
    contatos = FilialContatoSerializer(many=True, read_only=True, source='contatos_vinculados')
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

    class Meta:
        model = Filial
        fields = [
            'id',
            'nome',
            'enderecos',
            'contatos',
            'codigo_interno',
            'status',
            'descricao',
            'empresa',
            'empresa_nome',
            'is_ativa',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_ativa', 'created_by', 'updated_by', 'created_at', 'updated_at']

class FilialCreateSerializer(serializers.ModelSerializer):
    enderecos = FilialEnderecoNestedSerializer(many=True, required=True, allow_empty=False)
    contatos = FilialContatoNestedSerializer(many=True, required=True, allow_empty=False)

    class Meta:
        model = Filial
        fields = [
            'nome',
            'codigo_interno',
            'status',
            'descricao',
            'empresa',
            'contatos',
            'enderecos',
        ]
        extra_kwargs = {
            'status': {'choices': StatusFilial.choices}
        }

class FilialUpdateSerializer(serializers.ModelSerializer):
    enderecos = FilialEnderecoNestedSerializer(many=True, required=False)
    contatos = FilialContatoNestedSerializer(many=True, required=False)

    class Meta:
        model = Filial
        fields = [
            'nome',
            'codigo_interno',
            'descricao',
            'empresa',
            'contatos',
            'enderecos',
        ]

    def validate(self, attrs):
        if 'status' in self.initial_data:
            raise serializers.ValidationError({
                "status": "Para alterar status de filial use as rotas específicas ativar/desativar/suspender."
            })
        return attrs

class FilialSelecaoSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='nome', read_only=True)
    
    class Meta:
        model = Filial
        fields = ['id', 'label', 'codigo_interno']