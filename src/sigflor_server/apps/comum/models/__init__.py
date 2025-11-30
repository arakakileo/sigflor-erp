from .base import TimeStampedModel, AuditModel, SoftDeleteModel
from .pessoa_fisica import PessoaFisica
from .pessoa_juridica import PessoaJuridica, SituacaoCadastral
from .usuarios import Usuario, UsuarioManager
from .permissoes import Permissao, Papel
from .empresas import Empresa
from .clientes import Cliente
from .filiais import Filial
from .contratos import Contrato
from .enderecos import (
    Endereco, TipoEndereco,
    PessoaFisicaEndereco, PessoaJuridicaEndereco, FilialEndereco
)
from .contatos import Contato, PessoaFisicaContato, PessoaJuridicaContato, FilialContato
from .documentos import Documento, PessoaFisicaDocumento, PessoaJuridicaDocumento
from .anexos import Anexo
from .deficiencias import Deficiencia
from .projeto import Projeto, StatusProjeto
from .exame import Exame

__all__ = [
    # Base
    'TimeStampedModel',
    'AuditModel',
    'SoftDeleteModel',
    # Pessoas
    'PessoaFisica',
    'PessoaJuridica',
    'SituacaoCadastral',
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
    'Projeto',
    'StatusProjeto',
    'Exame',
    # Entidades genericas
    'Endereco',
    'TipoEndereco',
    'PessoaFisicaEndereco',
    'PessoaJuridicaEndereco',
    'FilialEndereco',
    'Contato',
    'PessoaFisicaContato',
    'PessoaJuridicaContato',
    'FilialContato',
    'Documento',
    'PessoaFisicaDocumento',
    'PessoaJuridicaDocumento',
    'Anexo',
    'Deficiencia',
]
