from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EmpresaViewSet,
    ClienteViewSet,
    EnderecoViewSet,
    ContatoViewSet,
    DocumentoViewSet,
    AnexoViewSet,
    DeficienciaViewSet,
    FilialViewSet,
    ProjetoViewSet,
    ExameViewSet,
)

router = DefaultRouter()

# Cadastros principais
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'clientes', ClienteViewSet, basename='cliente')

# Estrutura organizacional
router.register(r'filiais', FilialViewSet, basename='filial')
router.register(r'projetos', ProjetoViewSet, basename='projeto')

# Entidades genericas (polimorficas)
# router.register(r'enderecos', EnderecoViewSet, basename='endereco')
# router.register(r'contatos', ContatoViewSet, basename='contato')
# router.register(r'documentos', DocumentoViewSet, basename='documento')
# router.register(r'anexos', AnexoViewSet, basename='anexo')
# router.register(r'deficiencias', DeficienciaViewSet, basename='deficiencia')
# router.register(r'exames', ExameViewSet, basename='exame')

urlpatterns = [
    path('', include(router.urls)),
]
