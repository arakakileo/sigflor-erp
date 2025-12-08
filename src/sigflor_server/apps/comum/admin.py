# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline # Re-importar para AnexoInline

from .models import (
    PessoaFisica,
    PessoaJuridica,
    Empresa,
    Cliente,
    Endereco,
    Contato,
    Documento,
    Anexo,
    Deficiencia,
    Filial,
    PessoaFisicaEndereco, PessoaFisicaContato, PessoaFisicaDocumento,
    PessoaJuridicaEndereco, PessoaJuridicaContato, PessoaJuridicaDocumento
)


# ============ Deficiencia Inline (Movido para antes de PessoaFisicaAdmin) ============ #

class DeficienciaInline(admin.TabularInline):
    """Inline para exibir deficiencias no formulario de pessoa fisica."""
    model = Deficiencia
    extra = 0
    fields = ['nome', 'tipo', 'cid', 'grau', 'congenita']
    readonly_fields = []

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


# ============ Anexo Inline (Movido para antes de PessoaJuridicaAdmin) ============ #

class AnexoInline(GenericTabularInline):
    model = Anexo
    extra = 0
    fields = ('arquivo', 'nome_original', 'descricao')
    readonly_fields = ('tamanho_formatado', 'mimetype',) # Corrigido para AnexoInline


# ============ Inlines Específicos para Pessoa Física ============ #

class PessoaFisicaEnderecoInline(admin.TabularInline):
    model = PessoaFisicaEndereco
    extra = 0
    fields = ('endereco', 'tipo', 'principal')
    raw_id_fields = ('endereco',)

class PessoaFisicaContatoInline(admin.TabularInline):
    model = PessoaFisicaContato
    extra = 0
    fields = ('contato', 'principal', 'contato_emergencia')
    raw_id_fields = ('contato',)

class PessoaFisicaDocumentoInline(admin.TabularInline):
    model = PessoaFisicaDocumento
    extra = 0
    fields = ('documento',)
    raw_id_fields = ('documento',)


# ============ Inlines Específicos para Pessoa Jurídica ============ #

class PessoaJuridicaEnderecoInline(admin.TabularInline):
    model = PessoaJuridicaEndereco
    extra = 0
    fields = ('endereco', 'tipo', 'principal')
    raw_id_fields = ('endereco',)

class PessoaJuridicaContatoInline(admin.TabularInline):
    model = PessoaJuridicaContato
    extra = 0
    fields = ('contato', 'principal')
    raw_id_fields = ('contato',)

class PessoaJuridicaDocumentoInline(admin.TabularInline):
    model = PessoaJuridicaDocumento
    extra = 0
    fields = ('documento',)
    raw_id_fields = ('documento',)


# ============ Pessoa Fisica ============ #

@admin.register(PessoaFisica)
class PessoaFisicaAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf_formatado', 'data_nascimento', 'sexo', 'possui_deficiencia', 'created_at']
    list_filter = ['sexo', 'estado_civil', 'possui_deficiencia', 'created_at']
    search_fields = ['nome_completo', 'cpf', 'rg']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['nome_completo']
    inlines = [DeficienciaInline, PessoaFisicaEnderecoInline, PessoaFisicaContatoInline, PessoaFisicaDocumentoInline]

    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'rg', 'orgao_emissor', 'data_nascimento')
        }),
        ('Informacoes Adicionais', {
            'fields': ('sexo', 'estado_civil', 'nacionalidade', 'naturalidade')
        }),
        ('Deficiencia', {
            'fields': ('possui_deficiencia',)
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Pessoa Juridica ============ #

@admin.register(PessoaJuridica)
class PessoaJuridicaAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'nome_fantasia', 'cnpj_formatado', 'situacao_cadastral']
    list_filter = ['situacao_cadastral', 'created_at']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['razao_social']
    inlines = [PessoaJuridicaEnderecoInline, PessoaJuridicaContatoInline, PessoaJuridicaDocumentoInline, AnexoInline]

    fieldsets = (
        ('Dados Principais', {
            'fields': ('razao_social', 'nome_fantasia', 'cnpj')
        }),
        ('Inscricoes', {
            'fields': ('inscricao_estadual',)
        }),
        ('Classificacao', {
            'fields': ('situacao_cadastral', 'data_abertura')
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Empresa CNPJ ============ #

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['get_razao_social', 'get_cnpj', 'ativa', 'created_at']
    list_filter = ['ativa', 'created_at']
    search_fields = ['pessoa_juridica__razao_social', 'pessoa_juridica__cnpj']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    raw_id_fields = ['pessoa_juridica']
    ordering = ['pessoa_juridica__razao_social']
    # Inlines para Empresa devem vir da PessoaJuridicaAdmin
    # inlines = [EnderecoInline, ContatoInline, DocumentoInline, AnexoInline] # Removido conforme plano

    fieldsets = (
        ('Dados da Empresa', {
            'fields': ('pessoa_juridica', 'descricao')
        }),
        ('Status', {
            'fields': ('ativa',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_razao_social(self, obj):
        return obj.pessoa_juridica.razao_social
    get_razao_social.short_description = 'Razao Social'
    get_razao_social.admin_order_field = 'pessoa_juridica__razao_social'

    def get_cnpj(self, obj):
        return obj.pessoa_juridica.cnpj_formatado
    get_cnpj.short_description = 'CNPJ'


# ============ Cliente ============ #

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['get_razao_social', 'get_cnpj', 'ativo', 'created_at']
    list_filter = ['ativo', 'created_at']
    search_fields = ['pessoa_juridica__razao_social', 'pessoa_juridica__cnpj', 'pessoa_juridica__nome_fantasia']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    raw_id_fields = ['pessoa_juridica']
    ordering = ['pessoa_juridica__razao_social']
    # Inlines para Cliente devem vir da PessoaJuridicaAdmin
    # inlines = [EnderecoInline, ContatoInline, DocumentoInline, AnexoInline] # Removido conforme plano

    fieldsets = (
        ('Dados do Cliente', {
            'fields': ('pessoa_juridica', 'descricao')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_razao_social(self, obj):
        return obj.pessoa_juridica.razao_social
    get_razao_social.short_description = 'Razao Social'
    get_razao_social.admin_order_field = 'pessoa_juridica__razao_social'

    def get_cnpj(self, obj):
        return obj.pessoa_juridica.cnpj_formatado
    get_cnpj.short_description = 'CNPJ'


# ============ Endereco ============ #

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ['logradouro', 'numero', 'cidade', 'estado', 'cep_formatado']
    list_filter = ['estado', 'created_at']
    search_fields = ['logradouro', 'bairro', 'cidade', 'cep']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Endereco', {
            'fields': ('logradouro', 'numero', 'complemento', 'bairro')
        }),
        ('Localizacao', {
            'fields': ('cidade', 'estado', 'cep', 'pais')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Contato ============ #

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'valor']
    list_filter = ['tipo', 'created_at']
    search_fields = ['valor']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Dados do Contato', {
            'fields': ('tipo', 'valor')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Documento ============ #

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'descricao', 'data_validade', 'vencido']
    list_filter = ['tipo', 'created_at']
    search_fields = ['tipo', 'descricao']
    readonly_fields = ['id', 'vencido', 'nome_original', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Dados do Documento', {
            'fields': ('tipo', 'descricao', 'arquivo', 'nome_original')
        }),
        ('Validade', {
            'fields': ('data_emissao', 'data_validade', 'vencido')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Deficiencia ============ #

# A classe DeficienciaInline foi movida para o topo do arquivo para evitar NameError.


@admin.register(Deficiencia)
class DeficienciaAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'get_pessoa_nome',
        'tipo',
        'cid',
        'grau',
        'congenita',
        'created_at',
    ]
    list_filter = [
        'tipo',
        'congenita',
        'created_at',
    ]
    search_fields = [
        'nome',
        'cid',
        'pessoa_fisica__nome_completo',
        'pessoa_fisica__cpf',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['pessoa_fisica']
    ordering = ['pessoa_fisica__nome_completo', 'nome']

    fieldsets = (
        ('Vinculo', {
            'fields': ('id', 'pessoa_fisica')
        }),
        ('Dados da Deficiencia', {
            'fields': ('nome', 'tipo', 'cid', 'grau')
        }),
        ('Informacoes Adicionais', {
            'fields': ('congenita',)
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_pessoa_nome(self, obj):
        return obj.pessoa_fisica.nome_completo
    get_pessoa_nome.short_description = 'Pessoa'
    get_pessoa_nome.admin_order_field = 'pessoa_fisica__nome_completo'


# ============ Filial ============ #

@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_interno', 'status', 'get_empresa_nome', 'is_ativa', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['nome', 'codigo_interno', 'empresa__pessoa_juridica__razao_social']
    readonly_fields = ['id', 'is_ativa', 'created_at', 'updated_at', 'deleted_at']
    raw_id_fields = ['empresa']
    ordering = ['nome']

    fieldsets = (
        ('Dados da Filial', {
            'fields': ('nome', 'codigo_interno', 'descricao')
        }),
        ('Vinculo', {
            'fields': ('empresa',)
        }),
        ('Status', {
            'fields': ('status', 'is_ativa')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_empresa_nome(self, obj):
        return obj.empresa_nome
    get_empresa_nome.short_description = 'Empresa'
    get_empresa_nome.admin_order_field = 'empresa__pessoa_juridica__razao_social'