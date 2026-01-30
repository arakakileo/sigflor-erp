from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExameViewSet, 
    ASOViewSet, 
    ExameRealizadoViewSet,
    TipoEPIViewSet,
    EPIViewSet,
    EntregaEPIViewSet
)

router = DefaultRouter()
router.register(r'exames', ExameViewSet, basename='exame')
router.register(r'asos', ASOViewSet, basename='aso')
router.register(r'exames-realizados', ExameRealizadoViewSet, basename='exame-realizado')
router.register(r'tipos-epi', TipoEPIViewSet, basename='tipos-epi')
router.register(r'epis', EPIViewSet, basename='epis')
router.register(r'entregas-epi', EntregaEPIViewSet, basename='entregas-epi')

urlpatterns = [
    path('', include(router.urls)),
]