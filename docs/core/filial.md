# Core — Filial (Especificação Detalhada)

## 1. Visão Geral

A entidade **Filial** representa uma unidade operacional ou base física do grupo. Ela armazena informações sobre as unidades físicas da empresa, sendo essencial para a alocação de projetos, equipes e funcionários. Uma filial pode ou não estar vinculada a uma `Empresa` específica dentro do grupo.

**Propósito Arquitetural:** Centralizar a gestão das unidades físicas, permitindo um controle granular sobre onde as operações são executadas e onde os recursos estão alocados.

---

## 2. Estrutura do Modelo (`comum.Filial`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **nome** | `models.CharField` | `VARCHAR(200)` | `null=False`, `blank=False`. Nome da filial. |
| **codigo_interno** | `models.CharField` | `VARCHAR(50)` | `unique=True`. Código interno único para identificação da filial. |
| **status** | `models.CharField` | `VARCHAR(20)` | `choices=['ATIVA', 'INATIVA', 'SUSPENSA']`. Status operacional da filial. |
| **descricao** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. Descrição detalhada da filial. |
| **empresa** | `models.ForeignKey` | `UUID` | `null=True`, `blank=True`. Vínculo com a `Empresa` do grupo à qual a filial pertence. `on_delete=models.PROTECT`. |
| *created_at* | `models.DateTimeField`| `TIMESTAMP` | `auto_now_add=True`. Herdado do `SoftDeleteModel`. |
| *updated_at* | `models.DateTimeField`| `TIMESTAMP` | `auto_now=True`. Herdado do `SoftDeleteModel`. |
| *deleted_at* | `models.DateTimeField`| `TIMESTAMP` | `null=True`, `default=None`. Herdado do `SoftDeleteModel`. |

---

## 3. Relacionamentos

As associações são feitas via tabelas de vínculo explícitas para manter a integridade referencial.

| Relacionamento com | Tabela de Vínculo | Cardinalidade | Descrição |
| :--- | :--- | :--- | :--- |
| **Empresa** | `N/A` (ForeignKey direta) | N:1 | Uma filial pertence a uma única empresa (opcional). |
| **Endereco** | `FilialEndereco` | 1:N | Uma filial pode ter múltiplos endereços. |
| **Contato** | `FilialContato` | 1:N | Uma filial pode ter múltiplos contatos. |
| **Projeto** | `Projeto` | N:1 | Uma filial pode estar associada a múltiplos projetos (relação reversa). |
| **Usuario** | `Usuario` | N:M | Usuários podem ter acesso a múltiplas filiais (relação reversa via `allowed_filiais`). |

---

## 4. Estratégia de Indexação

Para otimizar as consultas, os seguintes índices devem ser criados no banco de dados:

-   **Índice Único:** no campo `codigo_interno` (já garantido pelo `unique=True`).
-   **Índice Padrão (B-Tree):** nos campos `nome`, `status` e `empresa` para acelerar buscas e filtros.
-   **Índice Composto:** em `(deleted_at, nome)` para otimizar listagens de registros ativos ordenados por nome.

---

## 5. Propriedades e Métodos Úteis

-   **`is_ativa`** (bool): Retorna `True` se a filial estiver ativa e não tiver sido logicamente excluída.
-   **`endereco_principal`** (Endereco): Retorna a instância do `Endereco` marcado como principal para esta filial (necessita de implementação na camada de Selectors/Services).
-   **`empresa_nome`** (str): Retorna a razão social da `Empresa` à qual a filial está vinculada.
