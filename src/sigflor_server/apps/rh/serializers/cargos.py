from rest_framework import serializers

from apps.autenticacao.serializers import UsuarioResumoSerializer
from apps.comum.models.enums import TipoDocumento
from apps.sst.serializers import CargoExameNestedSerializer, CargoExameSerializer
from ..models import Cargo, CargoDocumento
from ..models.enums import NivelCargo


class CargoDocumentoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.ReadOnlyField(source='get_documento_tipo_display')

    class Meta:
        model = CargoDocumento
        fields = [
            'id',
            'documento_tipo',
            'tipo_display',
            'obrigatorio',
            'condicional',
        ]
        read_only_fields = ['id', 'tipo_display',]


class CargoDocumentoNestedSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    documento_tipo = serializers.ChoiceField(choices=TipoDocumento.choices, required=True)
    obrigatorio = serializers.BooleanField(required=True)
    condicional = serializers.CharField(required=False)


    class Meta:
        model = CargoDocumento
        fields = [
            'id',
            'documento_tipo',
            'obrigatorio',
            'condicional',
        ]


class CargoListSerializer(serializers.ModelSerializer):
    funcionarios_count = serializers.ReadOnlyField()
    tem_risco = serializers.ReadOnlyField()

    class Meta:
        model = Cargo
        fields = [
            'id',
            'nome',
            'cbo',
            'nivel',
            'salario_base',
            'ativo',
            'tem_risco',
            'funcionarios_count',
        ]


class CargoSerializer(serializers.ModelSerializer):
    funcionarios_count = serializers.ReadOnlyField()
    tem_risco = serializers.ReadOnlyField()
    documentos_obrigatorios = CargoDocumentoSerializer(
        many=True, 
        read_only=True,
    )
    exames_obrigatorios = CargoExameSerializer(
        many=True, 
        read_only=True,
    )
    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()
    class Meta:
        model = Cargo
        fields = [
            'id',
            'nome',
            'cbo',
            'descricao',
            'salario_base',
            'nivel',
            'risco_fisico',
            'risco_biologico',
            'risco_quimico',
            'risco_ergonomico',
            'risco_acidente',
            'tem_risco',
            'ativo',
            'documentos_obrigatorios',
            'exames_obrigatorios',
            'funcionarios_count',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = [
            'id', 'funcionarios_count', 'tem_risco',
            'created_at', 'created_by' , 'updated_at',
            'updated_by',
        ]


class CargoCreateSerializer(serializers.ModelSerializer):

    documentos_obrigatorios = CargoDocumentoNestedSerializer(many=True, required=True)
    exames_obrigatorios = CargoExameNestedSerializer(many=True, required=True)
    descricao = serializers.CharField(required=True)
    salario_base = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    nivel = serializers.ChoiceField(choices=NivelCargo.choices, required=True)
    risco_fisico = serializers.CharField(required=True, allow_blank=True)
    risco_biologico = serializers.CharField(required=True, allow_blank=True)
    risco_quimico = serializers.CharField(required=True, allow_blank=True)
    risco_ergonomico = serializers.CharField(required=True, allow_blank=True)
    risco_acidente = serializers.CharField(required=True, allow_blank=True)
    
    class Meta:
        model = Cargo
        fields = [
            'nome',
            'cbo',
            'descricao',
            'salario_base',
            'nivel',
            'risco_fisico',
            'risco_biologico',
            'risco_quimico',
            'risco_ergonomico',
            'risco_acidente',
            'ativo',
            'documentos_obrigatorios',
            'exames_obrigatorios'
        ]

    def validate_documentos(self, value):
        tipos_vistos = set()
        for item in value:
            tipo = item.get('documento_tipo')
            if tipo in tipos_vistos:
                raise serializers.ValidationError(
                    f"O documento '{tipo}' foi informado mais de uma vez."
                )
            tipos_vistos.add(tipo)
        return value

    def validate(self, data):
        riscos = [
            'risco_fisico', 'risco_biologico', 'risco_quimico', 
            'risco_ergonomico', 'risco_acidente'
        ]

        for risco in riscos:
            if risco in data and data[risco] == "":
                del data[risco]
        
        return data


class CargoUpdateSerializer(serializers.ModelSerializer):
    documentos_obrigatorios = CargoDocumentoNestedSerializer(many=True, required=False)
    exames_obrigatorios = CargoExameNestedSerializer(many=True, required=False)

    class Meta:
        model = Cargo
        fields = [
            'nome',
            'cbo',
            'descricao',
            'salario_base',
            'nivel',
            'risco_fisico',
            'risco_biologico',
            'risco_quimico',
            'risco_ergonomico',
            'risco_acidente',
            'ativo',
            'documentos_obrigatorios',
            'exames_obrigatorios'
        ]
        extra_kwargs = {
            'nivel': {'choices': NivelCargo.choices},
        }


class CargoSelecaoSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='nome', read_only=True)
    
    class Meta:
        model = Cargo
        fields = ['id', 'label', 'cbo']