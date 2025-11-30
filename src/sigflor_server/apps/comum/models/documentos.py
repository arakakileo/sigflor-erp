import uuid
from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel


def documento_upload_path(instance, filename):
    """Define o caminho de upload para documentos organizados por ano/mês."""
    from django.utils import timezone
    now = timezone.now()
    return f'documentos/{now.year}/{now.month:02d}/{filename}'


class Documento(SoftDeleteModel):
    """
    Entidade centralizada de documentos formais.
    Documentos são vinculados a outras entidades através de tabelas de junção
    (ex: PessoaFisicaDocumento, PessoaJuridicaDocumento).
    """

    class Tipo(models.TextChoices):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=50, choices=Tipo.choices)
    descricao = models.TextField(blank=True, null=True)
    arquivo = models.FileField(upload_to=documento_upload_path)

    # Metadados do arquivo
    nome_original = models.CharField(
        max_length=255,
        help_text='Nome do arquivo no momento do upload'
    )
    mimetype = models.CharField(
        max_length=100,
        help_text='Tipo MIME do arquivo (ex: application/pdf)'
    )
    tamanho = models.PositiveIntegerField(
        help_text='Tamanho do arquivo em bytes'
    )

    data_emissao = models.DateField(blank=True, null=True)
    data_validade = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'documentos'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['data_validade']),
            models.Index(fields=['tipo', 'data_emissao']),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome_original}"

    @property
    def vencido(self) -> bool:
        """Verifica se o documento está vencido."""
        from django.utils import timezone
        if self.data_validade:
            return self.data_validade < timezone.now().date()
        return False


class PessoaFisicaDocumento(SoftDeleteModel):
    """Tabela de vínculo entre PessoaFisica e Documento."""
    pessoa_fisica = models.ForeignKey(
        'comum.PessoaFisica',
        on_delete=models.CASCADE,
        related_name='documentos_vinculados'
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_fisica'
    )
    principal = models.BooleanField(
        default=False,
        help_text='Indica se é o documento principal deste tipo para esta pessoa'
    )

    class Meta:
        db_table = 'pessoas_fisicas_documentos'
        verbose_name = 'Documento de Pessoa Física'
        verbose_name_plural = 'Documentos de Pessoas Físicas'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_fisica', 'documento'],
                name='uniq_pf_documento'
            ),
            # Apenas um documento principal por tipo por pessoa física
            models.UniqueConstraint(
                fields=['pessoa_fisica'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pf_documento_principal_por_tipo',
                # Nota: a constraint de unicidade por tipo será verificada no service
            ),
        ]

    def __str__(self):
        return f"{self.pessoa_fisica} - {self.documento}"


class PessoaJuridicaDocumento(SoftDeleteModel):
    """Tabela de vínculo entre PessoaJuridica e Documento."""
    pessoa_juridica = models.ForeignKey(
        'comum.PessoaJuridica',
        on_delete=models.CASCADE,
        related_name='documentos_vinculados'
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_juridica'
    )
    principal = models.BooleanField(
        default=False,
        help_text='Indica se é o documento principal deste tipo para esta pessoa jurídica'
    )

    class Meta:
        db_table = 'pessoas_juridicas_documentos'
        verbose_name = 'Documento de Pessoa Jurídica'
        verbose_name_plural = 'Documentos de Pessoas Jurídicas'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_juridica', 'documento'],
                name='uniq_pj_documento'
            ),
            models.UniqueConstraint(
                fields=['pessoa_juridica'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pj_documento_principal_por_tipo',
            ),
        ]

    def __str__(self):
        return f"{self.pessoa_juridica} - {self.documento}"
