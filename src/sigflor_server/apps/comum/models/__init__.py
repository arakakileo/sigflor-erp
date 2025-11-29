from .base import TimeStampedModel, AuditModel, SoftDeleteModel
from .pessoa_fisica import PessoaFisica
from .pessoa_juridica import PessoaJuridica
from .usuarios import Usuario, UsuarioManager
from .permissoes import Permissao, Papel
from .empresas import Empresa
from .clientes import Cliente
from .filiais import Filial
from .contratos import Contrato
from .subcontratos import SubContrato
from .enderecos import Endereco
from .contatos import Contato, PessoaFisicaContato, PessoaJuridicaContato, FilialContato
from .documentos import Documento
from .anexos import Anexo
from .deficiencias import Deficiencia
from .projeto import Projeto
from .exame import Exame

__all__ = [
    # Base
    'TimeStampedModel',
    'AuditModel',
    'SoftDeleteModel',
    # Pessoas
    'PessoaFisica',
    'PessoaJuridica',
    # Usuarios e RBAC
    'Usuario',
    'UsuarioManager',
    'Permissao',
    'Papel',
    # Empresas e Estrutura
    'Empresa',
    'Cliente',
    'Filial',
    'Contrato',
    'SubContrato',
    'Projeto',
    'Exame',
    # Entidades genericas
    'Endereco',
    'Contato',
    'PessoaFisicaContato',
    'PessoaJuridicaContato',
    'FilialContato',
    'Documento',
    'Anexo',
    'Deficiencia',
]
