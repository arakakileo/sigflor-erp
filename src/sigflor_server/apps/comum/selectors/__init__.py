# -*- coding: utf-8 -*-
"""
Selectors para consultas otimizadas.
Centralizam queries complexas e evitam N+1 usando select_related e prefetch_related.
"""

# Importar todos os selectors de seus respectivos módulos
from .pessoa_fisica import *
from .pessoa_juridica import *
from .empresa import *
from .cliente import *
from .endereco import * # Contém endereco_list_por_entidade
from .contato import *   # Contém contato_list_por_entidade
from .documento import * # Contém documento_list_por_entidade
from .anexo import *     # Contém anexo_list_por_entidade
from .deficiencia import *
from .filial import *
from .projeto import *
from .exame import *
