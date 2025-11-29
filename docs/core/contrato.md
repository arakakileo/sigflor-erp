# Core — Contrato

## 1. Visão Geral

O submódulo de **Contratos** gerencia os acordos comerciais formais celebrados entre uma [Empresa](./empresa.md) do grupo e um [Cliente](./cliente.md) externo.

Esta entidade serve como um "guarda-chuva" para um ou mais [Projetos](./projeto.md) (centros de custo), formalizando os termos, valores e vigência da prestação de serviços.

## 2. Estrutura da Entidade `Contrato`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `numero_interno` | String | Código único para identificação interna do contrato. |
| `numero_externo`| String | (Opcional) O número do contrato fornecido pelo cliente. |
| `cliente` | FK para `Cliente` | A empresa cliente que faz parte do contrato. |
| `empresa` | FK para `Empresa` | A empresa do grupo que é a parte contratada. |
| `descricao` | Text | Objeto do contrato e outras informações relevantes. |
| `data_inicio` | Date | Data de início da vigência do contrato. |
| `data_fim` | Date | (Opcional) Data de término da vigência. |
| `valor_total` | Decimal | (Opcional) O valor financeiro total do contrato. |
| `ativo` | Boolean | Indica se o contrato está ativo. |

## 3. Regras de Negócio

1.  **Unicidade:** O `numero_interno` deve ser único em todo o sistema.
2.  **Vigência:** Um contrato é considerado vigente se estiver `ativo` e a data atual estiver entre a `data_inicio` и `data_fim` (ou se `data_fim` for nula).
3.  **Consistência de Dados:** Ao criar um contrato, a `Empresa` selecionada deve ser a mesma `empresa_gestora` definida no cadastro do `Cliente`, garantindo a integridade do faturamento.
4.  **Soft Delete:** Contratos seguem a política de exclusão lógica. A desativação de um contrato não afeta os projetos vinculados, mas impede a criação de novos.

## 4. Endpoints da API

### Listar Contratos
`GET /api/core/contratos/`

Filtros: `ativo=true`, `vigente=true`, `cliente_id=<uuid>`, `empresa_id=<uuid>`

### Criar Contrato
`POST /api/core/contratos/`

**Request Body:**

```json
{
  "numero_interno": "CTR-2025-001",
  "cliente_id": "uuid-do-cliente",
  "empresa_id": "uuid-da-empresa-do-grupo",
  "descricao": "Contrato de prestação de serviços de reflorestamento.",
  "data_inicio": "2025-01-01",
  "data_fim": "2025-12-31",
  "valor_total": 500000.00
}
```

### Ações Específicas

-   **Listar Projetos de um Contrato:**
    `GET /api/core/contratos/{id}/projetos/`
