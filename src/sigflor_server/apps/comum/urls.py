from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EmpresaViewSet,
    ClienteViewSet,
    DeficienciaViewSet,
    FilialViewSet,
    ProjetoViewSet,
    EnumsView
)

router = DefaultRouter()

# Cadastros principais
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'clientes', ClienteViewSet, basename='cliente')

# Estrutura organizacional
router.register(r'filiais', FilialViewSet, basename='filial')
router.register(r'projetos', ProjetoViewSet, basename='projeto')



router.register(r'deficiencias', DeficienciaViewSet, basename='deficiencia')

urlpatterns = [
    path('', include(router.urls)),
    path("enums/", EnumsView.as_view(), name="enums")
]
