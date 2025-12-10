from .empresas import EmpresaViewSet
from .clientes import ClienteViewSet
from .enderecos import EnderecoViewSet
from .contatos import ContatoViewSet
from .documentos import DocumentoViewSet
from .anexos import AnexoViewSet
from .deficiencias import DeficienciaViewSet
from .filiais import FilialViewSet
from .projeto import ProjetoViewSet
from .exame import ExameViewSet
from .enums import EnumsView

__all__ = [
    'EmpresaViewSet',
    'ClienteViewSet',
    'EnderecoViewSet',
    'ContatoViewSet',
    'DocumentoViewSet',
    'AnexoViewSet',
    'DeficienciaViewSet',
    'FilialViewSet',
    'ProjetoViewSet',
    'ExameViewSet',
    'EnumsView',
]
