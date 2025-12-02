from django.db import transaction

from ..models import (
    Contato, 
    PessoaFisica, PessoaJuridica, Filial,
    PessoaFisicaContato, PessoaJuridicaContato, FilialContato
)


class ContatoService:
    """Service layer para operações com Contato."""

    @staticmethod
    @transaction.atomic
    def create(
        *,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        created_by=None,
    ) -> Contato:
        """
        Cria ou recupera um Contato (sem vínculo).
        Utiliza get_or_create para respeitar a constraint unique (tipo, valor).
        """
        contato, created = Contato.objects.get_or_create(
            tipo=tipo,
            valor=valor,
            deleted_at__isnull=True,
            defaults={
                'tem_whatsapp': tem_whatsapp,
                'created_by': created_by,
            }
        )
        return contato

    @staticmethod
    @transaction.atomic
    def criar_contato_para_pessoa_juridica(
        *,
        pessoa_juridica: PessoaJuridica,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        created_by=None,
    ) -> PessoaJuridicaContato:
        """
        Cria um contato e vincula a uma PessoaJuridica.
        Se principal=True, desmarca outros contatos como principal.
        """
        # 1. Cria ou recupera o contato base
        contato = ContatoService.create(
            tipo=tipo,
            valor=valor,
            tem_whatsapp=tem_whatsapp,
            created_by=created_by,
        )

        # 2. Gerencia flag principal
        if principal:
            PessoaJuridicaContato.objects.filter(
                pessoa_juridica=pessoa_juridica,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        # 3. Cria o vínculo
        # Verifica se já existe o vínculo para evitar erro de constraint
        vinculo, created = PessoaJuridicaContato.objects.get_or_create(
            pessoa_juridica=pessoa_juridica,
            contato=contato,
            deleted_at__isnull=True,
            defaults={
                'principal': principal,
                'created_by': created_by
            }
        )

        # Se já existia e agora deve ser principal, atualiza
        if not created and principal and not vinculo.principal:
            vinculo.principal = True
            vinculo.updated_by = created_by
            vinculo.save()

        return vinculo

    @staticmethod
    @transaction.atomic
    def add_contato_to_pessoa_fisica(
        *,
        pessoa_fisica: PessoaFisica,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        contato_emergencia: bool = False,
        created_by=None,
    ) -> PessoaFisicaContato:
        """
        Cria um contato e vincula a uma PessoaFisica.
        """
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

        vinculo, created = PessoaFisicaContato.objects.get_or_create(
            pessoa_fisica=pessoa_fisica,
            contato=contato,
            deleted_at__isnull=True,
            defaults={
                'principal': principal,
                'contato_emergencia': contato_emergencia,
                'created_by': created_by
            }
        )

        if not created:
            updated = False
            if principal and not vinculo.principal:
                vinculo.principal = True
                updated = True
            if contato_emergencia != vinculo.contato_emergencia:
                vinculo.contato_emergencia = contato_emergencia
                updated = True
            
            if updated:
                vinculo.updated_by = created_by
                vinculo.save()

        return vinculo

    @staticmethod
    @transaction.atomic
    def add_contato_to_filial(
        *,
        filial: Filial,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        created_by=None,
    ) -> FilialContato:
        """
        Cria um contato e vincula a uma Filial.
        """
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

        vinculo, created = FilialContato.objects.get_or_create(
            filial=filial,
            contato=contato,
            deleted_at__isnull=True,
            defaults={
                'principal': principal,
                'created_by': created_by
            }
        )

        if not created and principal and not vinculo.principal:
            vinculo.principal = True
            vinculo.updated_by = created_by
            vinculo.save()

        return vinculo

    @staticmethod
    @transaction.atomic
    def update(contato: Contato, updated_by=None, **kwargs) -> Contato:
        """Atualiza um Contato existente."""
        for attr, value in kwargs.items():
            if hasattr(contato, attr):
                setattr(contato, attr, value)
        contato.updated_by = updated_by
        contato.save()
        return contato

    @staticmethod
    @transaction.atomic
    def delete(contato: Contato, user=None) -> None:
        """Soft delete de um Contato."""
        # A exclusão em cascata dos vínculos é feita via sinal ou manualmente se necessário
        # Como usamos tabelas de vínculo, podemos deletar apenas o vínculo ou o contato todo
        # Aqui deletamos o contato, o que logicamente invalida os vínculos
        contato.delete(user=user)

    @staticmethod
    @transaction.atomic
    def definir_principal(contato: Contato, updated_by=None) -> None:
        """
        Define um contato como principal. 
        Nota: Isso requer saber qual entidade está vinculada. 
        Idealmente deve ser feito através do vínculo (ex: set_principal_pessoa_juridica)
        ou passar o vínculo como argumento em vez do contato.
        """
        pass # Implementar nos métodos específicos de vínculo se necessário

    @staticmethod
    def get_contatos_pessoa_juridica(pessoa_juridica: PessoaJuridica) -> list:
        return list(PessoaJuridicaContato.objects.filter(
            pessoa_juridica=pessoa_juridica,
            deleted_at__isnull=True
        ).select_related('contato').order_by('-principal', 'contato__tipo'))