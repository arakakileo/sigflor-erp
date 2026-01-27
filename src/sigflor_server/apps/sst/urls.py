from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExameViewSet, 
    ASOViewSet, 
    ExameRealizadoViewSet,
    TipoEPIViewSet,
    EPIViewSet,
    CargoEPIViewSet
)

router = DefaultRouter()
router.register(r'exames', ExameViewSet, basename='exame')
router.register(r'asos', ASOViewSet, basename='aso')
router.register(r'exames-realizados', ExameRealizadoViewSet, basename='exame-realizado')
router.register(r'tipos-epi', TipoEPIViewSet, basename='tipo-epi')
router.register(r'epis', EPIViewSet, basename='epi')
router.register(r'cargos-epis', CargoEPIViewSet, basename='cargo-epi')

urlpatterns = [
    path('', include(router.urls)),
]