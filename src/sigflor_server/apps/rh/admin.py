# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    Cargo, Funcionario, Dependente, CargoDocumento, Equipe, EquipeFuncionario
)


# ============ Inlines para RH ============ #

class CargoDocumentoInline(admin.TabularInline):
    """Define quais documentos são obrigatórios para o cargo diretamente na tela do Cargo."""
    model = CargoDocumento
    extra = 0
    fields = ['documento_tipo', 'obrigatorio', 'condicional']
    raw_id_fields = [] 


class DependenteInline(admin.TabularInline):
    """Gestão rápida de dependentes dentro do cadastro do funcionário."""
    model = Dependente
    extra = 0
    fields = [
        'pessoa_fisica', # Link para a pessoa física do dependente
        'parentesco',
        'dependencia_irrf',
        'ativo',
    ]
    raw_id_fields = ['pessoa_fisica']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


class EquipeFuncionarioInline(admin.TabularInline):
    """Lista os membros dentro do cadastro da Equipe."""
    model = EquipeFuncionario
    extra = 0
    fields = ['funcionario', 'data_entrada', 'data_saida']
    raw_id_fields = ['funcionario']


# ============ Cargo ============ #

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'salario_base',
        'cbo',
        'nivel',
        'ativo',
        'funcionarios_count',
        'tem_risco',
        'created_at',
    ]
    list_filter = [
        'ativo',
        'nivel',
        'risco_fisico', # Filtros para encontrar cargos perigosos (SST)
        'risco_biologico',
        'risco_quimico',
        'risco_ergonomico',
        'risco_mecanico',
        'created_at',
    ]
    search_fields = [
        'nome',
        'cbo',
        'descricao',
    ]
    readonly_fields = [
        'id',
        'funcionarios_count',
        'tem_risco',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    ordering = ['nome']
    inlines = [CargoDocumentoInline] # Configura documentos exigidos aqui

    fieldsets = (
        ('Dados do Cargo', {
            'fields': ('nome', 'salario_base', 'cbo', 'nivel')
        }),
        ('Riscos Ocupacionais', {
            'fields': ('risco_fisico', 'risco_biologico', 'risco_quimico', 'risco_ergonomico', 'risco_mecanico'),
            'classes': ('collapse',) # Escondido por padrão para limpar a tela
        }),
        ('Descricao', {
            'fields': ('descricao',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo', 'funcionarios_count', 'tem_risco')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Funcionario ============ #

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = [
        'matricula',
        'nome',
        'cpf_formatado',
        'cargo_nome',
        'status',
        'tem_dependente',
        'tipo_contrato',
        'data_admissao',
        'empresa_nome',
        'is_ativo',
    ]
    list_filter = [
        'status',
        'cargo',
        'tem_dependente',
        'tipo_contrato',
        'empresa',
        'created_at',
    ]
    search_fields = [
        'matricula',
        'pessoa_fisica__nome_completo', # Busca pelo nome da PF
        'pessoa_fisica__cpf',
        'cargo__nome',
        'empresa__pessoa_juridica__razao_social',
    ]
    readonly_fields = [
        'id',
        'matricula',
        'tem_dependente',
        'is_ativo',
        'nome',
        'cpf_formatado',
        'cargo_nome',
        'empresa_nome',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    # Raw ID fields são vitais aqui para evitar carregar milhares de PFs no dropdown
    raw_id_fields = ['pessoa_fisica', 'cargo', 'empresa',]
    ordering = ['pessoa_fisica__nome_completo']
    inlines = [DependenteInline]

    fieldsets = (
        ('Identificacao', {
            'fields': ('id', 'matricula', 'pessoa_fisica')
        }),
        ('Dados Profissionais', {
            'fields': ('cargo', 'empresa',)
        }),
        ('Contrato', {
            'fields': (
                'tipo_contrato',
                'data_admissao',
                'data_demissao',
                'salario_nominal',
            )
        }),
        ('Dados Físicos e Adicionais', {
            'fields': ('peso_corporal', 'altura', 'indicacao', 'cidade_atual'),
            'classes': ('collapse',)
        }),
        ('Status e Dependentes', {
            'fields': ('status', 'tem_dependente', 'is_ativo')
        }),
        ('Vestimenta / EPI', {
            'fields': ('tamanho_camisa', 'tamanho_calca', 'tamanho_calcado'),
            'classes': ('collapse',)
        }),
        ('Dados Bancários', {
            'fields': ('banco', 'agencia', 'conta_corrente', 'tipo_conta', 'chave_pix'),
            'classes': ('collapse',)
        }),
        ('Documentos Trabalhistas', {
            'fields': ('ctps_numero', 'ctps_serie', 'ctps_uf', 'pis_pasep'),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

# ============ CargoDocumento ============ #

@admin.register(CargoDocumento)
class CargoDocumentoAdmin(admin.ModelAdmin):
    list_display = [
        'cargo',
        'documento_tipo',
        'obrigatorio',
        'condicional',
        'created_at',
    ]
    list_filter = [
        'obrigatorio',
        'documento_tipo',
        'created_at',
    ]
    search_fields = [
        'cargo__nome',
        'documento_tipo',
        'condicional',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['cargo']
    ordering = ['cargo__nome', 'documento_tipo']

    fieldsets = (
        ('Vínculo', {
            'fields': ('cargo',)
        }),
        ('Documento', {
            'fields': ('documento_tipo', 'obrigatorio', 'condicional')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Dependente ============ #

@admin.register(Dependente)
class DependenteAdmin(admin.ModelAdmin):
    list_display = [
        'nome_completo',
        'cpf_formatado',
        'parentesco',
        'funcionario',
        'ativo',
        'dependencia_irrf',
        'created_at',
    ]
    list_filter = [
        'parentesco',
        'ativo',
        'dependencia_irrf',
        'created_at',
    ]
    search_fields = [
        'pessoa_fisica__nome_completo',
        'pessoa_fisica__cpf',
        'funcionario__pessoa_fisica__nome_completo',
        'funcionario__matricula',
    ]
    readonly_fields = [
        'id',
        'nome_completo',
        'cpf_formatado',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['funcionario', 'pessoa_fisica']
    ordering = ['pessoa_fisica__nome_completo']

    fieldsets = (
        ('Vínculo', {
            'fields': ('funcionario', 'pessoa_fisica')
        }),
        ('Dados do Dependente', {
            'fields': ('parentesco', 'dependencia_irrf', 'ativo')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Equipe ============ #

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'tipo_equipe',
        'projeto',
        'lider',
        'coordenador',
        'ativa',
        'membros_count',
        'created_at',
    ]
    list_filter = [
        'tipo_equipe',
        'ativa',
        'projeto',
        'created_at',
    ]
    search_fields = [
        'nome',
        'projeto__descricao',
        'lider__pessoa_fisica__nome_completo',
        'coordenador__pessoa_fisica__nome_completo',
    ]
    readonly_fields = [
        'id',
        'membros_count',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['projeto', 'lider', 'coordenador']
    ordering = ['nome']
    inlines = [EquipeFuncionarioInline]

    fieldsets = (
        ('Dados da Equipe', {
            'fields': ('nome', 'tipo_equipe', 'projeto')
        }),
        ('Liderança', {
            'fields': ('lider', 'coordenador')
        }),
        ('Status', {
            'fields': ('ativa', 'membros_count')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ EquipeFuncionario ============ #

@admin.register(EquipeFuncionario)
class EquipeFuncionarioAdmin(admin.ModelAdmin):
    list_display = [
        'equipe',
        'funcionario',
        'data_entrada',
        'data_saida',
        'created_at',
    ]
    list_filter = [
        'data_entrada',
        'data_saida',
        'created_at',
    ]
    search_fields = [
        'equipe__nome',
        'funcionario__pessoa_fisica__nome_completo',
        'funcionario__matricula',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['equipe', 'funcionario']
    ordering = ['-data_entrada', 'equipe__nome']

    fieldsets = (
        ('Vínculo', {
            'fields': ('equipe', 'funcionario')
        }),
        ('Período', {
            'fields': ('data_entrada', 'data_saida')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )