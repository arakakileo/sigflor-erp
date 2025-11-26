from typing import List, Any
from django.db import models
from django.contrib.contenttypes.models import ContentType

class ServiceUtils:
    """
    Utilitários para camadas de serviço.
    """

    @staticmethod
    def sincronizar_lista_aninhada(
        entidade_pai: Any,
        dados_lista: List[dict],
        service_filho: Any,
        model_filho: Any,
        user: Any,
        metodo_busca_existentes: str
    ) -> None:
        """
        Sincroniza lista aninhada garantindo a PROPRIEDADE dos dados.
        """
        # 1. Identificar o tipo da entidade pai para validação de segurança
        content_type_pai = ContentType.objects.get_for_model(entidade_pai)
        object_id_pai = str(entidade_pai.pk)

        # 2. Buscar itens existentes (para lógica de exclusão)
        metodo_busca = getattr(service_filho, metodo_busca_existentes)
        itens_existentes = metodo_busca(entidade_pai)

        # Mapear IDs recebidos
        ids_recebidos = set()
        for item in dados_lista:
            item_id = item.get('id')
            if item_id:
                ids_recebidos.add(str(item_id))

        # 3. EXCLUIR (Seguro: só deletamos o que o 'get_por_entidade' retornou, ou seja, o que é nosso)
        for item_db in itens_existentes:
            if str(item_db.id) not in ids_recebidos:
                service_filho.delete(item_db, user=user)

        # 4. PROCESSAR: Criar ou Atualizar
        for item_data in dados_lista:
            item_id = item_data.get('id')

            if item_id:
                # ATUALIZAR (Agora com SEGURANÇA DE PROPRIEDADE)
                try:
                    instancia = model_filho.objects.get(
                        pk=item_id,
                        # TRAVA DE SEGURANÇA:
                        # Só recupera o objeto se ele pertencer ao Pai atual
                        content_type=content_type_pai,
                        object_id=object_id_pai,
                        deleted_at__isnull=True
                    )
                    service_filho.update(instancia, updated_by=user, **item_data)
                except model_filho.DoesNotExist:
                    # Se o ID existe mas é de OUTRA empresa, o 'get' falha aqui.
                    # Podemos ignorar (não faz nada) ou lançar erro.
                    # Ignorar é mais seguro (não expõe que o ID existe).
                    pass 
            else:
                # CRIAR
                item_data.pop('id', None)
                service_filho.create(entidade=entidade_pai, created_by=user, **item_data)