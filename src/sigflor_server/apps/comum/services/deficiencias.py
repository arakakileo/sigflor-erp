# -*- coding: utf-8 -*-
from typing import Optional
from django.db import transaction

from ..models import Deficiencia, PessoaFisica


class DeficienciaService:
    """Service layer para operacoes com Deficiencia."""

    @staticmethod
    @transaction.atomic
    def create(
        pessoa_fisica: PessoaFisica,
        nome: str,
        tipo: str = None,
        cid: Optional[str] = None,
        grau: Optional[str] = None,
        data_diagnostico=None,
        congenita: bool = False,
        observacoes: Optional[str] = None,
        created_by=None,
    ) -> Deficiencia:
        """Cria uma nova Deficiencia para uma pessoa fisica."""
        deficiencia = Deficiencia(
            pessoa_fisica=pessoa_fisica,
            nome=nome,
            tipo=tipo or Deficiencia.TipoDeficiencia.OUTRA,
            cid=cid,
            grau=grau,
            data_diagnostico=data_diagnostico,
            congenita=congenita,
            observacoes=observacoes,
            created_by=created_by,
        )
        deficiencia.save()
        return deficiencia

    @staticmethod
    @transaction.atomic
    def update(deficiencia: Deficiencia, updated_by=None, **kwargs) -> Deficiencia:
        """Atualiza uma Deficiencia existente."""
        # Nao permite alterar pessoa_fisica
        kwargs.pop('pessoa_fisica', None)
        kwargs.pop('pessoa_fisica_id', None)

        for attr, value in kwargs.items():
            if hasattr(deficiencia, attr):
                setattr(deficiencia, attr, value)
        deficiencia.updated_by = updated_by
        deficiencia.save()
        return deficiencia

    @staticmethod
    @transaction.atomic
    def delete(deficiencia: Deficiencia, user=None) -> None:
        """Soft delete de uma Deficiencia."""
        deficiencia.delete(user=user)

    @staticmethod
    def get_deficiencias_por_pessoa(pessoa_fisica: PessoaFisica) -> list:
        """Retorna todas as deficiencias de uma pessoa fisica."""
        return list(Deficiencia.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).order_by('nome'))

    @staticmethod
    def get_deficiencias_por_tipo(tipo: str) -> list:
        """Retorna deficiencias de um tipo especifico."""
        return list(Deficiencia.objects.filter(
            tipo=tipo,
            deleted_at__isnull=True
        ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo'))

    @staticmethod
    def get_deficiencias_por_cid(cid: str) -> list:
        """Retorna deficiencias por codigo CID."""
        return list(Deficiencia.objects.filter(
            cid__icontains=cid,
            deleted_at__isnull=True
        ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo'))
