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
    def get_exames_cargo(cargo: Cargo) -> list:
        """
        Retorna todos os exames configurados para um cargo.
        """
        return list(CargoExame.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        ).order_by('exame__nome'))

    @staticmethod
    @transaction.atomic
    def vincular_exame_cargo(
        *,
        cargo: Cargo,
        exame: Exame,
        periodicidade_meses: int = None,
        observacoes: str = '',
        user: Usuario = None,
    ) -> CargoExame:
        """
        Cria ou atualiza um vínculo de exame para um cargo.
        """
        cargo_exame, created = CargoExame.objects.get_or_create(
            cargo=cargo,
            exame=exame,
            deleted_at__isnull=True,
            defaults={
                'periodicidade_meses': periodicidade_meses,
                'observacoes': observacoes,
                'created_by': user,
            }
        )

        if not created:
            cargo_exame.periodicidade_meses = periodicidade_meses
            cargo_exame.observacoes = observacoes
            cargo_exame.save()

        return cargo_exame

    @staticmethod
    @transaction.atomic
    def remover_vinculo_exame_cargo(cargo_exame: CargoExame, user: Usuario) -> None:
        """
        Remove (soft delete) um vínculo de exame do cargo.
        """
        cargo_exame.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restaurar_vinculos_exames_cargo(cargo: Cargo, user: Usuario) -> None:
        # Implementação futura se necessário
        pass

    @staticmethod
    @transaction.atomic
    def atualizar_vinculos_exames_cargo(
        *,
        cargo: Cargo,
        exames_data: list,
        user: Usuario
    ) -> list:
        """
        Sincroniza a lista de exames do cargo (Full Sync).
        """
        if exames_data is None:
            exames_data = []

        existentes = {
            doc.exame_id: doc 
            for doc in CargoExame.objects.filter(cargo=cargo, deleted_at__isnull=True)
        }

        processados_ids = set()
        resultado = []
        print(exames_data)
        for data in exames_data:
            exame = data.get('exame')
            if not exame: continue
            print(f'exame: {exame}')
            # Ajuste: ExameService anterior esperava 'exame_id' no loop mas 'exame' no create.
            # Aqui ajustamos para garantir 'exame' objeto.
            
            processados_ids.add(exame.id)
            
            cargo_exame = ExameService.vincular_exame_cargo(
                cargo=cargo,
                user=user,
                **data
            )
            resultado.append(cargo_exame)

        for ex_id, doc_existente in existentes.items():
            if ex_id not in processados_ids:
                ExameService.remover_vinculo_exame_cargo(doc_existente, user=user)
        
        return resultado

    @staticmethod
    def validar_exames_funcionario(funcionario) -> dict:
        """
        Valida se o funcionário possui todos os exames obrigatórios (via ASO).
        """
        from apps.sst.models import ExameRealizado
        
        cargo = funcionario.cargo
        
        requisitos = CargoExame.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        )
        
        exames_funcionario_ids = set(
            ExameRealizado.objects.filter(
                aso__funcionario=funcionario,
                aso__deleted_at__isnull=True,
                deleted_at__isnull=True
            ).values_list('exame_id', flat=True)
        )
        
        exames_ok = []
        exames_faltantes = []
        
        for req in requisitos:
            item = {
                'id': req.exame.id,
                'nome': req.exame.nome,
                'periodicidade': req.periodicidade_meses,
            }
            
            if req.exame_id in exames_funcionario_ids:
                exames_ok.append(item)
            else:
                exames_faltantes.append(item)
                
        return {
            'valido': len(exames_faltantes) == 0,
            'exames_ok': exames_ok,
            'exames_faltantes': exames_faltantes
        }