from django.db import models


class TipoContato(models.TextChoices):
    CELULAR = 'telefone_celular', 'Telefone Celular'
    FIXO = 'telefone_fixo', 'Telefone Fixo'
    EMAIL = 'email', 'E-mail'
    OUTRO = 'outro', 'Outro'

class TipoDeficiencia(models.TextChoices):
    FISICA = 'fisica', 'Fisica'
    AUDITIVA = 'auditiva', 'Auditiva'
    VISUAL = 'visual', 'Visual'
    MENTAL = 'mental', 'Mental/Intelectual'
    MULTIPLA = 'multipla', 'Multipla'
    REABILITADO = 'reabilitado', 'Reabilitado'
    OUTRA = 'outra', 'Outra'

class GrauDeficiencia(models.TextChoices):
    LEVE = 'leve', 'Leve'
    MODERADA = 'moderada', 'Moderada'
    GRAVE = 'grave', 'Grave'
    TOTAL = 'total', 'Total'

class TipoDocumento(models.TextChoices):
    RG = 'RG', 'RG'
    CNH = 'CNH', 'Carteira Nacional de Habilitação'
    CPF = 'CPF', 'Cadastro de Pessoas Físicas'
    TITULO_ELEITOR = 'TITULO_ELEITOR', 'Título de Eleitor'
    CERTIDAO_NASCIMENTO_CASAMENTO = 'CERTIDAO_NASCIMENTO_CASAMENTO', 'Certidão de Nascimento/Casamento'
    COMPROVANTE_ENDERECO = 'COMPROVANTE_ENDERECO', 'Comprovante de Endereço'
    CARTAO_SUS = 'CARTAO_SUS', 'Cartão do SUS'
    CARTEIRA_VACINA = 'CARTEIRA_VACINA', 'Carteira de Vacinação (Geral)'
    COMPROVANTE_PIS_NIS = 'COMPROVANTE_PIS_NIS', 'Comprovante PIS/NIS'
    CTPS = 'CTPS', 'Carteira de Trabalho Digital'
    CERTIDAO_NASCIMENTO_DEPENDENTE = 'CERTIDAO_NASCIMENTO_DEPENDENTE', 'Certidão de Nascimento de Dependente'
    CARTEIRA_VACINA_DEPENDENTE = 'CARTEIRA_VACINA_DEPENDENTE', 'Carteira de Vacinação de Dependente'
    DECLARACAO_ESCOLAR_DEPENDENTE = 'DECLARACAO_ESCOLAR_DEPENDENTE', 'Declaração de Matrícula Escolar de Dependente'
    CARTAO_CONTA_BANCO = 'CARTAO_CONTA_BANCO', 'Cartão/Comprovante de Conta Bancária'
    FOTO_3X4 = 'FOTO_3X4', 'Foto 3x4'
    NADA_CONSTA_DETRAN = 'NADA_CONSTA_DETRAN', 'Nada Consta DETRAN'
    CURSO_MOOP = 'CURSO_MOOP', 'Certificado Curso MOOP'
    CURSO_PASSAGEIROS = 'CURSO_PASSAGEIROS', 'Certificado Curso Transporte de Passageiros'
    CURSO_MAQUINAS_AGRICOLAS = 'CURSO_MAQUINAS_AGRICOLAS', 'Certificado Curso Operação de Máquinas Agrícolas'
    ASO = 'ASO', 'Atestado de Saúde Ocupacional (Documento PDF)'
    CONTRATO_SOCIAL = 'CONTRATO_SOCIAL', 'Contrato Social'
    NOTA_FISCAL = 'NOTA_FISCAL', 'Nota Fiscal'
    CONTRATO = 'CONTRATO', 'Contrato'
    ADITIVO = 'ADITIVO', 'Aditivo Contratual'
    CRLV = 'CRLV', 'CRLV'
    LAUDO = 'LAUDO', 'Laudo'
    OUTROS = 'OUTROS', 'Outros Documentos'

class UF(models.TextChoices):
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    AP = 'AP', 'Amapá'
    AM = 'AM', 'Amazonas'
    BA = 'BA', 'Bahia'
    CE = 'CE', 'Ceará'
    DF = 'DF', 'Distrito Federal'
    ES = 'ES', 'Espírito Santo'
    GO = 'GO', 'Goiás'
    MA = 'MA', 'Maranhão'
    MT = 'MT', 'Mato Grosso'
    MS = 'MS', 'Mato Grosso do Sul'
    MG = 'MG', 'Minas Gerais'
    PA = 'PA', 'Pará'
    PB = 'PB', 'Paraíba'
    PR = 'PR', 'Paraná'
    PE = 'PE', 'Pernambuco'
    PI = 'PI', 'Piauí'
    RJ = 'RJ', 'Rio de Janeiro'
    RN = 'RN', 'Rio Grande do Norte'
    RS = 'RS', 'Rio Grande do Sul'
    RO = 'RO', 'Rondônia'
    RR = 'RR', 'Roraima'
    SC = 'SC', 'Santa Catarina'
    SP = 'SP', 'São Paulo'
    SE = 'SE', 'Sergipe'
    TO = 'TO', 'Tocantins'

class TipoEndereco(models.TextChoices):
    RESIDENCIAL = 'RESIDENCIAL', 'Residencial'
    COMERCIAL = 'COMERCIAL', 'Comercial'
    CORRESPONDENCIA = 'CORRESPONDENCIA', 'Correspondência'
    OUTRO = 'OUTRO', 'Outro'

class StatusFilial(models.TextChoices):
    ATIVA = 'ativa', 'Ativa'
    INATIVA = 'inativa', 'Inativa'
    SUSPENSA = 'suspensa', 'Suspensa'

class Sexo(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMININO = 'F', 'Feminino'
    OUTRO = 'O', 'Outro'

class EstadoCivil(models.TextChoices):
    SOLTEIRO = 'solteiro', 'Solteiro(a)'
    CASADO = 'casado', 'Casado(a)'
    DIVORCIADO = 'divorciado', 'Divorciado(a)'
    VIUVO = 'viuvo', 'Viuvo(a)'
    SEPARADO = 'separado', 'Separado(a)'
    UNIAO_ESTAVEL = 'uniao_estavel', 'Uniao Estavel'

class SituacaoCadastral(models.TextChoices):
    ATIVA = 'ativa', 'Ativa'
    SUSPENSA = 'suspensa', 'Suspensa'
    INAPTA = 'inapta', 'Inapta'
    BAIXADA = 'baixada', 'Baixada'
    NULA = 'nula', 'Nula'

class StatusProjeto(models.TextChoices):
    PLANEJADO = 'PLANEJADO', 'Planejado'
    EM_EXECUCAO = 'EM_EXECUCAO', 'Em Execução'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'
