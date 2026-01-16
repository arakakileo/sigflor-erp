# -*- coding: utf-8 -*-
from .cargos import (
    CargoSerializer, CargoCreateSerializer,
    CargoListSerializer, CargoUpdateSerializer,
    CargoSelecaoSerializer
)
from .cargo_documento import (
    CargoDocumentoSerializer, CargoDocumentoCreateSerializer,
    CargoDocumentoListSerializer, CargoDocumentoUpdateSerializer
)
from .funcionarios import (
    FuncionarioSerializer, FuncionarioCreateSerializer,
    FuncionarioListSerializer, FuncionarioUpdateSerializer
)
from .dependentes import (
    DependenteSerializer, DependenteNestedCreateSerializer,
    DependenteListSerializer, DependenteUpdateSerializer
)
from .equipes import (
    EquipeSerializer, EquipeCreateSerializer,
    EquipeListSerializer, EquipeUpdateSerializer,
    EquipeFuncionarioSerializer, EquipeFuncionarioCreateSerializer,
    EquipeFuncionarioListSerializer, EquipeFuncionarioUpdateSerializer
)

__all__ = [
    'CargoSerializer',
    'CargoCreateSerializer',
    'CargoListSerializer',
    'CargoUpdateSerializer',
    'CargoSelecaoSerializer',
    'CargoDocumentoSerializer',
    'CargoDocumentoCreateSerializer',
    'CargoDocumentoListSerializer',
    'CargoDocumentoUpdateSerializer',
    'FuncionarioSerializer',
    'FuncionarioCreateSerializer',
    'FuncionarioListSerializer',
    'FuncionarioUpdateSerializer',
    'DependenteSerializer',
    'DependenteNestedCreateSerializer',
    'DependenteListSerializer',
    'DependenteUpdateSerializer',
    'EquipeSerializer',
    'EquipeCreateSerializer',
    'EquipeListSerializer',
    'EquipeUpdateSerializer',
    'EquipeFuncionarioSerializer',
    'EquipeFuncionarioCreateSerializer',
    'EquipeFuncionarioListSerializer',
    'EquipeFuncionarioUpdateSerializer',
]
