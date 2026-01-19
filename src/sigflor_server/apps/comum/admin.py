from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (
    PessoaFisica, PessoaJuridica, Empresa, Cliente, Endereco, Contato,
    Documento, Anexo, Deficiencia, Filial,
    PessoaFisicaEndereco, PessoaFisicaContato, PessoaFisicaDocumento,
    PessoaJuridicaEndereco, PessoaJuridicaContato, PessoaJuridicaDocumento,
    FilialEndereco, FilialContato, Projeto
)

# --- Mixin para ocultar modelos do Menu Principal ---
class HiddenAdmin(admin.ModelAdmin):
    """
    Este modelo não aparecerá no menu lateral do Admin,
    mas ainda será acessível via Popups (Add/Edit) de outros modelos.
    """
    def has_module_permission(self, request):
        return False

# ============ Inlines (Mantidos para uso nos Popups) ============ #

class DeficienciaInline(admin.TabularInline):
    model = Deficiencia
    extra = 0
    fields = ['nome', 'tipo', 'cid', 'grau', 'congenita']

class AnexoInline(GenericTabularInline):
    model = Anexo
    extra = 0
    fields = ('arquivo', 'nome_original', 'descricao')
    readonly_fields = ('tamanho_formatado', 'mimetype',)

# --- Inlines Pessoa Física ---
class PessoaFisicaEnderecoInline(admin.TabularInline):
    model = PessoaFisicaEndereco
    extra = 0
    raw_id_fields = ('endereco',)

class PessoaFisicaContatoInline(admin.TabularInline):
    model = PessoaFisicaContato
    extra = 0
    raw_id_fields = ('contato',)

class PessoaFisicaDocumentoInline(admin.TabularInline):
    model = PessoaFisicaDocumento
    extra = 0
    raw_id_fields = ('documento',)

# --- Inlines Pessoa Jurídica ---
class PessoaJuridicaEnderecoInline(admin.TabularInline):
    model = PessoaJuridicaEndereco
    extra = 0
    raw_id_fields = ('endereco',)

class PessoaJuridicaContatoInline(admin.TabularInline):
    model = PessoaJuridicaContato
    extra = 0
    raw_id_fields = ('contato',)

class PessoaJuridicaDocumentoInline(admin.TabularInline):
    model = PessoaJuridicaDocumento
    extra = 0
    raw_id_fields = ('documento',)

# --- Inlines Filial ---
class FilialEnderecoInline(admin.TabularInline):
    model = FilialEndereco
    extra = 0
    raw_id_fields = ('endereco',)

class FilialContatoInline(admin.TabularInline):
    model = FilialContato
    extra = 0
    raw_id_fields = ('contato',)


# ============ Entidades "Filhas" (Ocultas do Menu) ============ #

@admin.register(PessoaFisica)
class PessoaFisicaAdmin(HiddenAdmin):
    search_fields = ['nome_completo', 'cpf', 'rg']
    # inlines = [DeficienciaInline, PessoaFisicaEnderecoInline, PessoaFisicaContatoInline, PessoaFisicaDocumentoInline]
    # Fieldsets mantidos para o Popup ser completo
    fieldsets = (
        ('Dados Pessoais', {'fields': ('nome_completo', 'cpf', 'rg', 'orgao_emissor', 'data_nascimento')}),
        ('Informações', {'fields': ('sexo', 'estado_civil', 'nacionalidade', 'naturalidade', 'possui_deficiencia')}),
    )

@admin.register(PessoaJuridica)
class PessoaJuridicaAdmin(HiddenAdmin):
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']
    inlines = [PessoaJuridicaEnderecoInline, PessoaJuridicaContatoInline, PessoaJuridicaDocumentoInline, AnexoInline]
    fieldsets = (
        ('Dados Principais', {'fields': ('razao_social', 'nome_fantasia', 'cnpj', 'inscricao_estadual')}),
        ('Situação', {'fields': ('situacao_cadastral', 'data_abertura')}),
    )

# Entidades de base também ocultas, acessíveis apenas via inlines das Pessoas
@admin.register(Endereco)
class EnderecoAdmin(HiddenAdmin):
    search_fields = ['logradouro', 'cep', 'cidade']

@admin.register(Contato)
class ContatoAdmin(HiddenAdmin):
    search_fields = ['valor']

@admin.register(Documento)
class DocumentoAdmin(HiddenAdmin):
    search_fields = ['descricao', 'tipo']

@admin.register(Deficiencia)
class DeficienciaAdmin(HiddenAdmin):
    pass

@admin.register(Anexo)
class AnexoAdmin(HiddenAdmin):
    pass


# ============ Entidades "Pai" (Visíveis no Menu) ============ #

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['get_razao_social', 'get_cnpj', 'ativa']
    search_fields = ['pessoa_juridica__razao_social', 'pessoa_juridica__cnpj']
    # O usuário clica no "+" deste campo para abrir o formulário completo da PJ (com endereços)
    raw_id_fields = ['pessoa_juridica'] 
    
    def get_razao_social(self, obj): return obj.pessoa_juridica.razao_social
    get_razao_social.short_description = 'Razão Social'
    
    def get_cnpj(self, obj): return obj.pessoa_juridica.cnpj_formatado
    get_cnpj.short_description = 'CNPJ'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['get_razao_social', 'get_cnpj', 'ativo']
    search_fields = ['pessoa_juridica__razao_social']
    # Gestão centralizada aqui
    raw_id_fields = ['pessoa_juridica', 'empresa_gestora']

    def get_razao_social(self, obj): return obj.pessoa_juridica.razao_social
    get_razao_social.short_description = 'Razão Social'

    def get_cnpj(self, obj): return obj.pessoa_juridica.cnpj_formatado
    get_cnpj.short_description = 'CNPJ'

@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_interno', 'status', 'empresa']
    search_fields = ['nome', 'codigo_interno']
    raw_id_fields = ['empresa']
    # Filial tem inlines diretos, pois usa tabela de vínculo própria
    inlines = [FilialEnderecoInline, FilialContatoInline]

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'descricao', 'status', 'cliente', 'empresa', 'filial']
    search_fields = ['numero', 'descricao']
    raw_id_fields = ['cliente', 'empresa', 'filial']