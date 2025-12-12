# -*- coding: utf-8 -*-
from .cargos import (
    CargoSerializer, CargoCreateSerializer,
    CargoListSerializer, CargoUpdateSerializer
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
from .alocacoes import (
    AlocacaoSerializer, AlocacaoCreateSerializer,
    AlocacaoListSerializer, AlocacaoUpdateSerializer
)

__all__ = [
    'CargoSerializer',
    'CargoCreateSerializer',
    'CargoListSerializer',
    'CargoUpdateSerializer',
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
    'AlocacaoSerializer',
    'AlocacaoCreateSerializer',
    'AlocacaoListSerializer',
    'AlocacaoUpdateSerializer',
]
