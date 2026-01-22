from django.db import transaction
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.rh.models import Cargo
from ..models import Exame, CargoExame


class ExameService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        nome: str,
        created_by: Usuario,
        descricao: str = '',
    ) -> Exame:
        exame = Exame(
            nome=nome,
            descricao=descricao,
            created_by=created_by,
        )
        exame.save()
        return exame

    @staticmethod
    @transaction.atomic
    def update(
        *,
        exame: Exame,
        updated_by: Usuario,
        **kwargs
    ) -> Exame:
        for attr, value in kwargs.items():
            if hasattr(exame, attr):
                setattr(exame, attr, value)
        
        exame.updated_by = updated_by
        exame.save()
        return exame

    @staticmethod
    @transaction.atomic
    def delete(*, exame: Exame, user: Usuario) -> None:
        if hasattr(exame, 'cargos_associados') and \
           exame.cargos_associados.filter(deleted_at__isnull=True).exists():
            raise ValidationError("Não é possível excluir este exame pois ele é requisito obrigatório para alguns cargos.")
        
        if hasattr(exame, 'exames_realizados') and \
           exame.exames_realizados.filter(deleted_at__isnull=True).exists():
            raise ValidationError("Não é possível excluir este exame pois existem registros de realização dele em ASOs ativos.")

        exame.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(*, exame: Exame, user: Usuario) -> Exame:
        exame.restore(user=user)
        return exame
    
    @staticmethod
    @transaction.atomic
    def configurar_exame_para_cargo(
        *,
        cargo: Cargo,
        exame: Exame,
        periodicidade_meses: int = None,
        observacoes: str = '',
        created_by: Usuario = None,
    ) -> CargoExame:
        cargo_exame, created = CargoExame.objects.get_or_create(
            cargo=cargo,
            exame=exame,
            deleted_at__isnull=True,
            defaults={
                'periodicidade_meses': periodicidade_meses,
                'observacoes': observacoes,
                'created_by': created_by,
            }
        )

        if not created:
            cargo_exame.periodicidade_meses = periodicidade_meses
            cargo_exame.observacoes = observacoes
            cargo_exame.updated_by = created_by
            cargo_exame.save()

        return cargo_exame
    