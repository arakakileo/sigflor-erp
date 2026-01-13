from rest_framework import serializers

from ..models import Projeto


class ProjetoListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Projeto
        fields = [
            'id',
            'numero',
            'descricao',
            'cliente',
            'cliente_nome',
            'empresa',
            'empresa_nome',
            'filial',
            'filial_nome',
            'status',
            'status_display',
            'data_inicio',
            'data_fim',
        ]

class ProjetoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_ativo = serializers.ReadOnlyField()

    class Meta:
        model = Projeto
        fields = [
            'id',
            'numero',
            'descricao',
            'cliente',
            'cliente_nome',
            'empresa',
            'empresa_nome',
            'filial',
            'filial_nome',
            'data_inicio',
            'data_fim',
            'status',
            'status_display',
            'is_ativo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'numero', 'empresa', 'cliente_nome', 'empresa_nome',
            'filial_nome', 'status_display', 'is_ativo',
            'created_at', 'updated_at'
        ]

class ProjetoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = [
            'descricao',
            'cliente',
            'filial',
            'data_inicio',
            'data_fim',
            'status',
        ]
    
    def validate(self, data):
        if data.get('data_fim') and data.get('data_inicio') and data['data_fim'] < data['data_inicio']:
            raise serializers.ValidationError({"data_fim": "Data de término anterior ao início."})
        return data

class ProjetoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = [
            'descricao',
            'filial',
            'data_inicio',
            'data_fim'
        ]

    def validate(self, data):
        inicio = data.get('data_inicio', self.instance.data_inicio if self.instance else None)
        fim = data.get('data_fim', self.instance.data_fim if self.instance else None)

        if fim and inicio and fim < inicio:
            raise serializers.ValidationError({"data_fim": "Data de término anterior ao início."})
        
        if 'status' in self.initial_data or 'status' in self.initial_data:
            raise serializers.ValidationError({
                "status": "Para alterar status de projetos use as rotas específicas de ativação/desativação."
            })
        
        return data

class ProjetoSelecaoSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='descricao', read_only=True)
    display = serializers.SerializerMethodField()

    class Meta:
        model = Projeto
        fields = ['id', 'label', 'numero', 'display']

    def get_display(self, obj):
        return f"{obj.numero} - {obj.descricao}"