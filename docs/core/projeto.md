# Core — Projeto (Centro de Custo)

## 1. Visão Geral

A entidade **Projeto** é o **coração do controle de custos e da logística operacional** no Sigflor. Ela representa um "Centro de Custo" ou uma "Obra", sendo a entidade que conecta a estrutura comercial com a estrutura física da empresa.

O `Projeto` materializa o conceito do **"Tripé"** da operação, unindo:
1.  **Quem Paga:** O [Cliente](./cliente.md).
2.  **Quem Fatura:** A [Empresa](./empresa.md) do grupo.
3.  **Onde Executa:** A [Filial](./filial.md) (base operacional).

Esta entidade substitui o conceito anteriormente chamado de "SubContrato" e centraliza a alocação de todos os recursos (funcionários, equipamentos, etc.).

**Status:** ✅ IMPLEMENTADO

---

## 2. Estrutura do Modelo (`comum.Projeto`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **numero** | `models.CharField` | `VARCHAR(20)` | `unique=True`, `editable=False`. Código único gerado automaticamente. Formato: `PRJ-YYYYMM-NNNN` |
| **descricao** | `models.TextField` | `TEXT` | `null=False`, `blank=False`. Nome ou objeto do projeto. |
| **cliente** | `models.ForeignKey` | `UUID` | FK para `Cliente`. `on_delete=PROTECT`. |
| **empresa** | `models.ForeignKey` | `UUID` | FK para `Empresa`. `on_delete=PROTECT`. **(Automático)** Preenchido via `cliente.empresa_gestora`. |
| **filial** | `models.ForeignKey` | `UUID` | FK para `Filial`. `on_delete=PROTECT`. Base operacional. |
| **contrato** | `models.ForeignKey` | `UUID` | FK para `Contrato`. `on_delete=PROTECT`, `null=True`, `blank=True`. (Opcional) |
| **data_inicio** | `models.DateField` | `DATE` | `null=False`. Data de início das atividades. |
| **data_fim** | `models.DateField` | `DATE` | `null=True`, `blank=True`. Data de término prevista. |
| **status** | `models.CharField` | `VARCHAR(20)` | `choices=StatusProjeto.choices`, `default='PLANEJADO'`. |

### Campos Herdados (SoftDeleteModel)
- `created_at`, `updated_at`, `deleted_at`
- `created_by`, `updated_by`

### Enum `StatusProjeto`
```python
class StatusProjeto(models.TextChoices):
    PLANEJADO = 'PLANEJADO', 'Planejado'
    EM_EXECUCAO = 'EM_EXECUCAO', 'Em Execução'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'
```

### Propriedades Computadas
- **`is_ativo`**: `True` se `status == EM_EXECUCAO`.
- **`cliente_nome`**: Retorna o nome fantasia ou razão social do cliente.
- **`empresa_nome`**: Retorna o nome fantasia ou razão social da empresa.
- **`filial_nome`**: Retorna o nome da filial.
- **`contrato_numero`**: Retorna o número interno do contrato, se houver.

---

## 3. Regras de Negócio

1.  **Criação do Número:** O `numero` do projeto é gerado automaticamente pelo sistema no momento da criação e não pode ser alterado. Formato: `PRJ-YYYYMM-NNNN` (ex: `PRJ-202511-0001`).
2.  **Preenchimento Automático da Empresa:** O campo `empresa` é **somente leitura** para o usuário. Seu valor é copiado do campo `empresa_gestora` do `Cliente` selecionado. Isso garante que o centro de custo esteja sempre alinhado com a estrutura de faturamento correta.
3.  **Vigência:** Um projeto é considerado ativo se seu `status` for `EM_EXECUCAO`.
4.  **Alocação de Recursos:** O `Projeto` é a entidade chave para a alocação de funcionários ([`rh.Funcionario`](../rh/funcionarios.md)), veículos (módulo de Frota) e outros ativos.
5.  **Soft Delete:** Projetos seguem a política de exclusão lógica.
6.  **Permissão Regional:** Operações de criação, atualização e exclusão verificam se o usuário tem acesso à filial do projeto.

---

## 4. Estratégia de Indexação

| Índice | Campos | Propósito |
| :--- | :--- | :--- |
| B-Tree | `numero` | Busca rápida por código do projeto |
| B-Tree | `status` | Filtro por status |
| B-Tree | `cliente` | Busca por cliente |
| B-Tree | `filial` | Busca por filial |
| B-Tree | `empresa` | Busca por empresa |
| B-Tree | `data_inicio` | Ordenação e filtro por data |

---

## 5. Camada de Serviço (`ProjetoService`)

### Métodos de Criação

- **`create(*, user, descricao, cliente_id, filial_id, data_inicio, contrato_id=None, data_fim=None, status='PLANEJADO')`**:
  - Cria um novo projeto.
  - O `numero` é gerado automaticamente.
  - A `empresa` é preenchida automaticamente via `cliente.empresa_gestora`.
  - Verifica permissão regional na filial.

### Métodos de Atualização

- **`update(*, user, projeto, **kwargs)`**: Atualiza dados do projeto (não permite alterar cliente/empresa).
- **`change_status(*, user, projeto, novo_status)`**: Altera o status do projeto.

### Métodos de Exclusão

- **`delete(*, user, projeto)`**: Soft delete do projeto.
- **`restore(*, user, projeto)`**: Restaura um projeto excluído.

### Métodos de Consulta

- **`get_by_numero(numero)`**: Busca projeto pelo número.
- **`list_ativos(user=None)`**: Lista projetos em execução (filtra por permissão regional).
- **`list_by_cliente(cliente_id)`**: Lista projetos de um cliente.
- **`list_by_filial(filial_id)`**: Lista projetos de uma filial.
- **`list_by_empresa(empresa_id)`**: Lista projetos de uma empresa.

---

## 6. Serializers

| Serializer | Propósito |
| :--- | :--- |
| `ProjetoListSerializer` | Listagem simplificada com nomes das entidades relacionadas |
| `ProjetoSerializer` | Leitura completa com todos os campos e propriedades |
| `ProjetoCreateSerializer` | Criação com validação de entidades relacionadas |
| `ProjetoUpdateSerializer` | Atualização parcial (não permite alterar cliente) |

---

## 7. Endpoints da API

### Listar Projetos
`GET /api/core/projetos/`

**Filtros:** `status`, `cliente_id`, `empresa_id`, `filial_id`

### Criar Projeto
`POST /api/core/projetos/`

**Request Body:**
```json
{
  "descricao": "Projeto de Silvicultura na Fazenda Boa Esperança",
  "cliente_id": "uuid-do-cliente",
  "filial_id": "uuid-da-filial-de-execucao",
  "contrato_id": "uuid-do-contrato-opcional",
  "data_inicio": "2025-02-01",
  "status": "PLANEJADO"
}
```
**Nota:** O `empresa_id` e `numero` não são enviados, pois o backend os preenche automaticamente.

### Atualizar Projeto
`PATCH /api/core/projetos/{id}/`

**Request Body:**
```json
{
  "descricao": "Novo nome do projeto",
  "status": "EM_EXECUCAO",
  "data_fim": "2025-12-31"
}
```

### Excluir Projeto (Soft Delete)
`DELETE /api/core/projetos/{id}/`
