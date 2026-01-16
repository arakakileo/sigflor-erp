# -*- coding: utf-8 -*-
from .cargos import CargoViewSet
from .cargo_documento import CargoDocumentoViewSet
from .funcionarios import FuncionarioViewSet
from .dependentes import DependenteViewSet
from .equipes import EquipeViewSet, EquipeFuncionarioViewSet

__all__ = [
    'CargoViewSet',
    'CargoDocumentoViewSet',
    'FuncionarioViewSet',
    'DependenteViewSet',
    'EquipeViewSet',
    'EquipeFuncionarioViewSet',
]
