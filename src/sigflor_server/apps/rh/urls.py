# -*- coding: utf-8 -*-
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CargoViewSet, FuncionarioViewSet, DependenteViewSet

router = DefaultRouter()
router.register(r'cargos', CargoViewSet, basename='cargo')
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionario')
router.register(r'dependentes', DependenteViewSet, basename='dependente')

urlpatterns = [
    path('', include(router.urls)),
]
