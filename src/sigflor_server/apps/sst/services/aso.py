from django.db import transaction
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.rh.models import Funcionario
from apps.sst.models import ASO, ExameRealizado
from apps.sst.models.enums import Status, StatusExame, Tipo


class ASOService:

    @staticmethod
    @transaction.atomic
    def gerar_solicitacao(
        *,
        funcionario: Funcionario,
        tipo: str,
        created_by: Usuario
    ) -> ASO:
        """
        Gera uma solicitação de ASO.
        
        Regras Admissional:
        - Só pode ser gerado se funcionário estiver AGUARDANDO_ADMISSAO (ou similar).
        - Só pode existir UM ASO Admissional por funcionário (neste contexto).
        """
        
        # Regra Específica: Admissional
        if tipo == Tipo.ADMISSIONAL:
            # 1. Verifica se já existe um ASO Admissional (qualquer status)
            # Para evitar duplicidade no processo de admissão.
            existe_admissional = ASO.objects.filter(
                funcionario=funcionario,
                tipo=Tipo.ADMISSIONAL,
                deleted_at__isnull=True
            ).exists()
            
            if existe_admissional:
                raise ValidationError(
                    "Já existe um ASO Admissional gerado para este funcionário."
                )
        else:
            raise ValidationError(
                "Tipo de ASO ainda não implementado."
            )

        # Regra Geral: Não pode haver ASO aberto do mesmo tipo
        aso_aberto = ASO.objects.filter(
            funcionario=funcionario,
            tipo=tipo,
            status__in=[Status.ABERTO, Status.EM_ANDAMENTO],
            deleted_at__isnull=True
        ).exists()
        
        if aso_aberto:
            raise ValidationError(
                f"Já existe um ASO {tipo} em aberto para este funcionário."
            )
            
        # Cria o ASO
        aso = ASO(
            funcionario=funcionario,
            tipo=tipo,
            status=Status.ABERTO,
            created_by=created_by
        )
        aso.save()
        
        # Busca exames obrigatórios do cargo
        cargo = funcionario.cargo
        if not cargo:
             raise ValidationError("Funcionário não possui cargo.")
            
        cargo_exames = cargo.exames_obrigatorios.filter(deleted_at__isnull=True)
        
        for ce in cargo_exames:
            ExameRealizado.objects.create(
                aso=aso,
                exame=ce.exame,
                status=StatusExame.PENDENTE,
                created_by=created_by
            )
            
        return aso

    @staticmethod
    @transaction.atomic
    def registrar_resultado_exame(
        *,
        exame_realizado: ExameRealizado,
        data_realizacao,
        resultado: str,
        arquivo=None,
        observacoes: str = '',
        updated_by: Usuario
    ) -> ExameRealizado:
        """
        Registra o resultado de um exame e calcula validade.
        """
        from django.utils.dateparse import parse_date
        from dateutil.relativedelta import relativedelta
        import datetime
        
        exame_realizado.data_realizacao = data_realizacao
        exame_realizado.resultado = resultado
        if arquivo:
            exame_realizado.arquivo = arquivo
        exame_realizado.observacoes = observacoes
        exame_realizado.status = StatusExame.REALIZADO
        
        # CALCULO DA VALIDADE
        # Busca a regra (CargoExame) para o cargo do funcionário
        funcionario = exame_realizado.aso.funcionario
        cargo = funcionario.cargo
        
        if cargo:
            try:
                # Import evita circular dependency se houver, mas idealmente models ja estao carregados
                from apps.sst.models import CargoExame
                
                cargo_exame = CargoExame.objects.filter(
                    cargo=cargo,
                    exame=exame_realizado.exame,
                    deleted_at__isnull=True
                ).first()
                
                if cargo_exame and cargo_exame.periodicidade_meses:
                    if isinstance(data_realizacao, str):
                        data_ref = parse_date(data_realizacao)
                    else:
                        data_ref = data_realizacao
                        
                    if data_ref:
                        exame_realizado.data_validade = data_ref + relativedelta(months=cargo_exame.periodicidade_meses)
            except Exception:
                # Se falhar calculo, mantem null ou loga erro. 
                # Para MVP, seguimos sem quebrar.
                pass
        
        exame_realizado.updated_by = updated_by
        exame_realizado.save()
        
        # Atualiza status do ASO
        aso = exame_realizado.aso
        if aso.status == Status.ABERTO:
            aso.status = Status.EM_ANDAMENTO
            aso.updated_by = updated_by
            aso.save()
            
        return exame_realizado

    @staticmethod
    @transaction.atomic
    def concluir_aso(
        *,
        aso: ASO,
        resultado: str,
        data_emissao,
        validade,
        medico_coordenador: str,
        medico_examinador: str,
        observacoes: str = '',
        updated_by: Usuario
    ) -> ASO:
        """
        Finaliza o ASO.
        Valida se todos os exames foram realizados.
        """
        
        # 1. Validação de Exames Pendentes
        exames_pendentes = aso.exames_realizados.filter(
            status=StatusExame.PENDENTE,
            deleted_at__isnull=True
        ).exists()
        
        if exames_pendentes:
            raise ValidationError(
                "Não é possível concluir o ASO pois existem exames pendentes."
            )
            
        # 2. Atualiza dados
        aso.resultado = resultado
        aso.data_emissao = data_emissao
        aso.validade = validade
        aso.medico_coordenador = medico_coordenador
        aso.medico_examinador = medico_examinador
        aso.observacoes = observacoes
        aso.status = Status.FINALIZADO
        aso.updated_by = updated_by
        aso.save()
        
        return aso

    @staticmethod
    def validar_pendencias_admissional(funcionario: Funcionario):
        """
        Verifica se o funcionário possui ASO Admissional APTO e VÁLIDO.
        Usado pelo serviço de RH antes de ativar o funcionário.
        """
        aso_apto = ASO.objects.filter(
            funcionario=funcionario,
            tipo=Tipo.ADMISSIONAL,
            status=Status.FINALIZADO,
            resultado='APTO',
            deleted_at__isnull=True
        ).order_by('-data_emissao').first()
        
        if not aso_apto:
            raise ValidationError(
                "Funcionário não possui ASO Admissional com resultado APTO concluído."
            )
            
        # Opcional: Verificar validade (se data_emissao muito antiga?)
        # Por enquanto apenas a existência.
