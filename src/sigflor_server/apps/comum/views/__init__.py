from .empresas import EmpresaViewSet
from .clientes import ClienteViewSet
from .usuarios import UsuarioViewSet
from .permissoes import PermissaoViewSet, PapelViewSet
from .enderecos import EnderecoViewSet
from .contatos import ContatoViewSet
from .documentos import DocumentoViewSet
from .anexos import AnexoViewSet
from .deficiencias import DeficienciaViewSet
from .filiais import FilialViewSet
from .contratos import ContratoViewSet
from .projeto import ProjetoViewSet
from .exame import ExameViewSet

__all__ = [
    'EmpresaViewSet',
    'ClienteViewSet',
    'UsuarioViewSet',
    'PermissaoViewSet',
    'PapelViewSet',
    'EnderecoViewSet',
    'ContatoViewSet',
    'DocumentoViewSet',
    'AnexoViewSet',
    'DeficienciaViewSet',
    'FilialViewSet',
    'ContratoViewSet',
    'ProjetoViewSet',
    'ExameViewSet',
]
