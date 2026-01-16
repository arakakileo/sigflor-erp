from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CargoViewSet,
    CargoDocumentoViewSet,
    FuncionarioViewSet,
    DependenteViewSet,
    EquipeViewSet,
    EquipeFuncionarioViewSet,
)

router = DefaultRouter()
router.register(r'cargos', CargoViewSet, basename='cargo')
router.register(r'cargo-documentos', CargoDocumentoViewSet, basename='cargo-documento')
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionario')
router.register(r'dependentes', DependenteViewSet, basename='dependente')
router.register(r'equipes', EquipeViewSet, basename='equipe')
router.register(r'equipe-funcionarios', EquipeFuncionarioViewSet, basename='equipe-funcionario')

urlpatterns = [
    path('', include(router.urls)),
]
