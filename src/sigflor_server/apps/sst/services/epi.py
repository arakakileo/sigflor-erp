from django.db import transaction
from django.core.exceptions import ValidationError

from apps.sst.models import TipoEPI, EPI, CargoEPI

class EPIService:

    @staticmethod
    @transaction.atomic
    def criar_tipo_epi(*, user, nome: str, unidade: str) -> TipoEPI:
        if TipoEPI.objects.filter(nome__iexact=nome, deleted_at__isnull=True).exists():
            raise ValidationError(f"Já existe um Tipo de EPI com o nome '{nome}'.")

        tipo = TipoEPI(nome=nome, unidade=unidade, created_by=user, updated_by=user)
        # TODO: Usar 'user' para log de auditoria se necessário
        tipo.save()
        return tipo

    @staticmethod
    @transaction.atomic
    def criar_epi(*, user, tipo: TipoEPI, ca: str, fabricante: str = '', modelo: str = '', validade_ca=None) -> EPI:
        if EPI.objects.filter(ca=ca, deleted_at__isnull=True).exists():
            raise ValidationError(f"Já existe um EPI cadastrado com o CA '{ca}'.")

        epi = EPI(
            tipo=tipo,
            ca=ca,
            fabricante=fabricante,
            modelo=modelo,
            validade_ca=validade_ca,
            created_by=user,
            updated_by=user
        )
        # TODO: Usar 'user' para log de auditoria se necessário
        epi.save()
        return epi

    @staticmethod
    def get_epis_cargo(cargo) -> list:
        """
        Retorna todos os EPIs configurados como obrigatórios para um cargo.
        """
        return list(CargoEPI.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        ).select_related('tipo_epi'))

    @staticmethod
    @transaction.atomic
    def vincular_epi_cargo(
        *,
        user,
        cargo,
        tipo_epi: TipoEPI,
        periodicidade_troca_dias: int,
        quantidade_padrao: int = 1,
        observacoes: str = ''
    ) -> CargoEPI:
        """
        Cria ou atualiza um vínculo de EPI para um cargo.
        """
        vinculo, created = CargoEPI.objects.update_or_create(
            cargo=cargo,
            tipo_epi=tipo_epi,
            defaults={
                'periodicidade_troca_dias': periodicidade_troca_dias,
                'quantidade_padrao': quantidade_padrao,
                'observacoes': observacoes,
                'deleted_at': None,
            }
        )

        if created:
            vinculo.created_by = user
            vinculo.save()

        return vinculo

    @staticmethod
    @transaction.atomic
    def remover_vinculo_epi_cargo(vinculo: CargoEPI, user=None) -> None:
        """
        Remove (soft delete) um vínculo de EPI do cargo.
        """
        vinculo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restaurar_vinculos_epis_cargo(cargo, data_delecao, user):
        """
        Restaura vínculos deletados em cascading.
        """
        pass

    @staticmethod
    @transaction.atomic
    def atualizar_vinculos_epis_cargo(
        *,
        cargo,
        epis_data: list,
        user
    ) -> list:
        """
        Sincroniza a lista de EPIs do cargo (Full Sync).
        """
        if epis_data is None:
            epis_data = []

        existentes = {
            doc.tipo_epi_id: doc 
            for doc in CargoEPI.objects.filter(cargo=cargo, deleted_at__isnull=True)
        }

        processados_tipos = set()
        resultado = []

        for data in epis_data:
            tipo_epi = data.get('tipo_epi')
            if not tipo_epi: continue

            processados_tipos.add(tipo_epi.id)

            vinculo = EPIService.vincular_epi_cargo(
                cargo=cargo,
                user=user,
                **data
            )
            resultado.append(vinculo)

        for tipo_id, doc_existente in existentes.items():
            if tipo_id not in processados_tipos:
                EPIService.remover_vinculo_epi_cargo(doc_existente, user=user)

        return resultado

    @staticmethod
    def get_todos_epis_para_cargo(cargo) -> list:
        """
        Retorna todos os EPIs configurados como obrigatórios para um cargo.
        """
        return list(CargoEPI.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        ).select_related('tipo_epi'))

    @staticmethod
    def validar_epis_funcionario(funcionario) -> dict:
        """
        Valida se o funcionário possui todos os EPIs obrigatórios entregues e válidos.
        Considera entregas recentes que ainda não venceram.
        """
        from apps.sst.models import EntregaEPI
        from datetime import date

        cargo = funcionario.cargo

        # 1. Obter requisitos do cargo (Tipos de EPI)
        requisitos = CargoEPI.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        )

        # 2. Obter entregas válidas do funcionário
        # Uma entrega é válida se:
        # - Pertence ao funcionário
        # - Não foi devolvida (devolvido=False)
        # - Data de validade >= Hoje
        entregas_validas_tipos = set(
            EntregaEPI.objects.filter(
                funcionario=funcionario,
                deleted_at__isnull=True,
                devolvido=False,
                data_validade__gte=date.today()
            ).values_list('epi__tipo_id', flat=True)
        )

        epis_ok = []
        epis_faltantes = []

        for req in requisitos:
            item = {
                'tipo_id': req.tipo_epi.id,
                'nome': req.tipo_epi.nome,
                'periodicidade_dias': req.periodicidade_troca_dias
            }

            if req.tipo_epi_id in entregas_validas_tipos:
                epis_ok.append(item)
            else:
                epis_faltantes.append(item)

        return {
            'valido': len(epis_faltantes) == 0,
            'epis_ok': epis_ok,
            'epis_faltantes': epis_faltantes
        }
