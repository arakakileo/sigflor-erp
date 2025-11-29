# RH — Alocação (Especificação Detalhada)

## 1. Visão Geral

A entidade **Alocação** registra o histórico de vinculação de um [Funcionário](./funcionarios.md) a um [Projeto](../core/projeto.md) específico. Ela é essencial para o controle de custos, apropriação de despesas e para a rastreabilidade da trajetória do funcionário dentro da empresa.

**Para o MVP, esta entidade focará no vínculo primário do funcionário com um projeto e datas. As complexidades de moradia (casa individual, compartilhada, alojamento, hotel) serão abstraídas em uma fase futura, mas o modelo será construído para permitir essa expansão.**

**Propósito Arquitetural:** Prover um registro auditável de onde e quando um funcionário esteve alocado, permitindo análises de custo por centro de custo e histórico funcional.

---

## 2. Estrutura do Modelo (`hr.Alocacao`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **funcionario** | `models.ForeignKey` | `UUID` | `to='hr.Funcionario'`, `on_delete=models.PROTECT`. O funcionário alocado. |
| **projeto** | `models.ForeignKey` | `UUID` | `to='core.Projeto'`, `on_delete=models.PROTECT`. O [Projeto](../core/projeto.md) ao qual o funcionário está vinculado. |
| **data_inicio** | `models.DateField` | `DATE` | `null=False`, `blank=False`. Data de início da alocação no projeto. |
| **data_fim** | `models.DateField` | `DATE` | `null=True`, `blank=True`. Data de término da alocação. Se `null`, a alocação está ativa. |
| **observacoes** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. Detalhes ou justificativas da alocação. |

**Constraint:** `UniqueConstraint` para `(funcionario, projeto, data_inicio)` para garantir a unicidade de uma alocação.
**Regra:** Um funcionário **ativo** (sem `data_fim`) só pode ter **uma** `Alocacao` com `data_fim=null` por vez. Ao criar uma nova alocação ativa, a anterior ativa (se houver) deve ser automaticamente encerrada (`data_fim` preenchida).

---

## 3. Relacionamentos

-   `hr.Alocacao` N:1 `hr.Funcionario`
-   `hr.Alocacao` N:1 `core.Projeto`

---

## 4. Estratégia de Indexação

-   **Índice Único Composto:** em `(funcionario, projeto, data_inicio)`.
-   **Índice Composto:** em `(funcionario, data_inicio, data_fim)` para consultas de histórico e alocações ativas.

---

## 5. Camada de Serviço (`AlocacaoService` / `FuncionarioService`)

A gestão de alocações será feita via `AlocacaoService` ou através de métodos específicos no `FuncionarioService`.

-   **`alocar_funcionario(*, funcionario: Funcionario, projeto: core.Projeto, data_inicio: date) -> Alocacao:`**:
    -   Recebe o funcionário, o projeto e a data de início.
    -   **Regra:** Antes de criar uma nova `Alocacao` com `data_fim=null` (ativa):
        -   Verifica se o `funcionario` já possui uma `Alocacao` ativa (`data_fim=null`).
        -   Se sim, encerra a alocação anterior, definindo sua `data_fim` para `data_inicio - 1 dia` da nova alocação (ou outro critério).
    -   Cria a nova instância de `Alocacao`.
-   **`encerrar_alocacao(*, alocacao: Alocacao, data_fim: date) -> Alocacao:`**:
    -   Define a `data_fim` para uma `Alocacao` existente, marcando-a como inativa.
    -   **Regra:** `data_fim` não pode ser anterior a `data_inicio`.
-   **`get_alocacao_ativa(*, funcionario: Funcionario) -> Optional[Alocacao]:`**:
    -   Retorna a alocação ativa atual de um funcionário, se existir.
