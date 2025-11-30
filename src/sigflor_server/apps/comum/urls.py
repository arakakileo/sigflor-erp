from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EmpresaCNPJViewSet,
    ContratanteViewSet,
    UsuarioViewSet,
    PermissaoViewSet,
    PapelViewSet,
    EnderecoViewSet,
    ContatoViewSet,
    DocumentoViewSet,
    AnexoViewSet,
    DeficienciaViewSet,
    FilialViewSet,
    ContratoViewSet,
    ProjetoViewSet,
    ExameViewSet,
)

router = DefaultRouter()

# Cadastros principais
router.register(r'empresas-cnpj', EmpresaCNPJViewSet, basename='empresa-cnpj')
router.register(r'contratantes', ContratanteViewSet, basename='contratante')

# Usuários e permissões
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'permissoes', PermissaoViewSet, basename='permissao')
router.register(r'papeis', PapelViewSet, basename='papel')

# Estrutura organizacional
router.register(r'filiais', FilialViewSet, basename='filial')
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'projetos', ProjetoViewSet, basename='projeto')

# Entidades genericas (polimorficas)
router.register(r'enderecos', EnderecoViewSet, basename='endereco')
router.register(r'contatos', ContatoViewSet, basename='contato')
router.register(r'documentos', DocumentoViewSet, basename='documento')
router.register(r'anexos', AnexoViewSet, basename='anexo')
router.register(r'deficiencias', DeficienciaViewSet, basename='deficiencia')
router.register(r'exames', ExameViewSet, basename='exame')

urlpatterns = [
    path('', include(router.urls)),
]
