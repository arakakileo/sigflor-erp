from django.db import models
from .base import SoftDeleteModel, AuditModel
from .clientes import Cliente
from .empresas import Empresa
from .filiais import Filial

class Projeto(SoftDeleteModel, AuditModel):
    """
    Representa um Projeto (Centro de Custo/Obra) que une Empresa, Cliente e Filial.
    É uma entidade transversal utilizada por diversos módulos.
    """
    nome = models.CharField(max_length=255, verbose_name="Nome do Projeto")
    
    # FK para o Contratante (Cliente) que é quem paga pelo serviço
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="projetos",
        verbose_name="Cliente"
    )
    
    # FK para a Filial (Onde o serviço é executado)
    filial = models.ForeignKey(
        Filial,
        on_delete=models.PROTECT,
        related_name="projetos",
        verbose_name="Filial"
    )
    
    # FK para a Empresa (CNPJ do próprio Grupo Econômico)
    # Este campo é preenchido automaticamente pela empresa_gestora do cliente.
    # Conforme ADRs, ele é denormalizado para otimizar queries e garantir consistência.
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="projetos_gerenciados",
        verbose_name="Empresa Gerenciadora"
    )

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        unique_together = ('nome', 'cliente', 'filial', 'empresa') # Garante unicidade do projeto
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cliente']),
            models.Index(fields=['filial']),
            models.Index(fields=['empresa']),
        ]

    def save(self, *args, **kwargs):
        """
        Preenche automaticamente o campo 'empresa' com a empresa_gestora do cliente
        antes de salvar.
        """
        if not self.empresa_id and self.cliente and self.cliente.empresa_gestora:
            self.empresa = self.cliente.empresa_gestora
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.cliente.pessoa_juridica.nome_fantasia}/{self.filial.nome})"
