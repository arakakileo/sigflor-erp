# -*- coding: utf-8 -*-
from .cargos import CargoService
from .cargo_documento import CargoDocumentoService
from .funcionarios import FuncionarioService
from .dependentes import DependenteService
from .equipes import EquipeService
from .alocacoes import AlocacaoService

__all__ = [
    'CargoService',
    'CargoDocumentoService',
    'FuncionarioService',
    'DependenteService',
    'EquipeService',
    'AlocacaoService',
]
