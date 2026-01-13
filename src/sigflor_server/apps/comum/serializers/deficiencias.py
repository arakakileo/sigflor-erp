# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Deficiencia, PessoaFisicaDeficiencia
from ..models.enums import TipoDeficiencia, GrauDeficiencia

class DeficienciaSerializer(serializers.ModelSerializer):

    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Deficiencia
        fields = [
            'id',
            'nome',
            'tipo',
            'tipo_display',
            'cid',
            'descricao',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tipo_display']


class DeficienciaSelecaoSerializer(serializers.ModelSerializer):

    label = serializers.SerializerMethodField()

    class Meta:
        model = Deficiencia
        fields = ['id', 'label', 'tipo', 'cid']

    def get_label(self, obj):
        cid_part = f" ({obj.cid})" if obj.cid else ""
        return f"{obj.nome}{cid_part}"


class PessoaFisicaDeficienciaSerializer(serializers.ModelSerializer):

    deficiencia_nome = serializers.CharField(source='deficiencia.nome', read_only=True)
    deficiencia_tipo = serializers.CharField(source='deficiencia.tipo', read_only=True)
    deficiencia_cid = serializers.CharField(source='deficiencia.cid', read_only=True)
    
    tipo_display = serializers.CharField(source='deficiencia.get_tipo_display', read_only=True)
    grau_display = serializers.CharField(source='get_grau_display', read_only=True)

    class Meta:
        model = PessoaFisicaDeficiencia
        fields = [
            'id',
            'deficiencia',
            'deficiencia_nome',
            'deficiencia_tipo',
            'deficiencia_cid', 
            'tipo_display',
            'grau',
            'grau_display',
            'congenita',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PessoaFisicaDeficienciaNestedSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(required=False)
    deficiencia_id = serializers.PrimaryKeyRelatedField(
        queryset=Deficiencia.objects.filter(deleted_at__isnull=True),
        source='deficiencia',
        required=True
    )

    class Meta:
        model = PessoaFisicaDeficiencia
        fields = [
            'id',
            'deficiencia_id',
            'grau',
            'congenita',
            'observacoes',
        ]
        extra_kwargs = {
            'grau': {'choices': GrauDeficiencia.choices, 'required': False},
            'congenita': {'default': False},
        }