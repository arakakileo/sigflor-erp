from typing import Optional
from django.db import transaction
from django.db.models import QuerySet

from ..models import (
    Contato, 
    PessoaFisica, PessoaJuridica, Filial,
    PessoaFisicaContato, PessoaJuridicaContato, FilialContato
)

class ContatoService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        created_by=None,
    ) -> Contato:

        contato = Contato(
            tipo=tipo,
            valor=valor,
            tem_whatsapp=tem_whatsapp,
            created_by=created_by,
        )
        contato.save()
        return contato

    @staticmethod
    @transaction.atomic
    def update(contato: Contato, updated_by=None, **kwargs) -> Contato:
        campos_permitidos = ['tipo', 'valor', 'tem_whatsapp']
        for attr, value in kwargs.items():
            if attr in campos_permitidos and hasattr(contato, attr):
                setattr(contato, attr, value)
        contato.updated_by = updated_by
        contato.save()
        return contato

    @staticmethod
    def _verificar_e_apagar_orfao(contato: Contato, user) -> None:

        if PessoaFisicaContato.objects.filter(contato=contato, deleted_at__isnull=True).exists():
            return
        
        if PessoaJuridicaContato.objects.filter(contato=contato, deleted_at__isnull=True).exists():
            return

        if FilialContato.objects.filter(contato=contato, deleted_at__isnull=True).exists():
            return

        contato.delete(user=user)

    # =========================================================================
    # 1. PESSOA FÍSICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_contatos_pessoa_fisica(pessoa_fisica: PessoaFisica) -> QuerySet:
        return PessoaFisicaContato.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).select_related('contato').order_by('-principal', 'contato__tipo')

    @staticmethod
    @transaction.atomic
    def vincular_contato_pessoa_fisica(
        *,
        pessoa_fisica: PessoaFisica,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        contato_emergencia: bool = False,
        created_by=None,
    ) -> PessoaFisicaContato:
        
        contato = ContatoService.create(
            tipo=tipo,
            valor=valor,
            tem_whatsapp=tem_whatsapp,
            created_by=created_by,
        )

        if principal:
            PessoaFisicaContato.objects.filter(
                pessoa_fisica=pessoa_fisica,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = PessoaFisicaContato(
            pessoa_fisica=pessoa_fisica,
            contato=contato,
            principal=principal,
            contato_emergencia=contato_emergencia,
            created_by=created_by
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_fisica(vinculo: PessoaFisicaContato, user=None) -> None:
        contato = vinculo.contato
        vinculo.delete(user=user)
        ContatoService._verificar_e_apagar_orfao(contato, user)

    # =========================================================================
    # 2. PESSOA JURÍDICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_contatos_pessoa_juridica(pessoa_juridica: PessoaJuridica) -> QuerySet:
        return PessoaJuridicaContato.objects.filter(
            pessoa_juridica=pessoa_juridica,
            deleted_at__isnull=True
        ).select_related('contato').order_by('-principal', 'contato__tipo')

    @staticmethod
    @transaction.atomic
    def vincular_contato_pessoa_juridica(
        *,
        pessoa_juridica: PessoaJuridica,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        created_by=None,
    ) -> PessoaJuridicaContato:
        
        contato = ContatoService.create(
            tipo=tipo,
            valor=valor,
            tem_whatsapp=tem_whatsapp,
            created_by=created_by,
        )

        if principal:
            PessoaJuridicaContato.objects.filter(
                pessoa_juridica=pessoa_juridica,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = PessoaJuridicaContato(
            pessoa_juridica=pessoa_juridica,
            contato=contato,
            principal=principal,
            created_by=created_by
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_juridica(vinculo: PessoaJuridicaContato, user=None) -> None:
        contato = vinculo.contato
        vinculo.delete(user=user)
        ContatoService._verificar_e_apagar_orfao(contato, user)

    # =========================================================================
    # 3. FILIAL (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_contatos_filial(filial: Filial) -> QuerySet:
        return FilialContato.objects.filter(
            filial=filial,
            deleted_at__isnull=True
        ).select_related('contato').order_by('-principal', 'contato__tipo')

    @staticmethod
    @transaction.atomic
    def vincular_contato_filial(
        *,
        filial: Filial,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        created_by=None,
    ) -> FilialContato:
        
        contato = ContatoService.create(
            tipo=tipo,
            valor=valor,
            tem_whatsapp=tem_whatsapp,
            created_by=created_by,
        )

        if principal:
            FilialContato.objects.filter(
                filial=filial,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = FilialContato(
            filial=filial,
            contato=contato,
            principal=principal,
            created_by=created_by
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_filial(vinculo: FilialContato, user=None) -> None:
        contato = vinculo.contato
        vinculo.delete(user=user)
        ContatoService._verificar_e_apagar_orfao(contato, user)