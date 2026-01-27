# RH — Equipes (Especificação Detalhada)

## 1. Visão Geral

A entidade **Equipe** organiza grupos de [Funcionários](./funcionarios.md) para a execução de atividades, sejam elas manuais ou mecanizadas. Ela é um agrupador operacional vinculado a um [Projeto](../core/projeto.md) e possui sua própria estrutura hierárquica interna (Líder e Coordenador).

**Propósito Arquitetural:** Facilitar a gestão de grupos de trabalho, a alocação de pessoal por projeto, a apropriação de custos e a hierarquia operacional para o RH e gestão de operações.

---

## 2. Estrutura dos Modelos

### 2.1. Modelo `hr.Equipe` (Cadastro da Equipe)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **nome** | `models.CharField` | `VARCHAR(100)` | `unique=True`, `null=False`, `blank=False`. Nome único da equipe (ex: "Equipe Alpha Colheita"). |
| **tipo_equipe** | `models.CharField` | `VARCHAR(20)` | `choices=Equipe.TipoEquipe.choices`. `null=False`, `blank=False`. (Enum: MANUAL, MECANIZADA). |
| **projeto** | `models.ForeignKey` | `UUID` | `to='core.Projeto'`, `on_delete=models.PROTECT`. O [Projeto](../core/projeto.md) ao qual a equipe está alocada. |
| **lider** | `models.OneToOneField` | `UUID` | `to='hr.Funcionario'`, `on_delete=models.PROTECT`, `null=True`, `blank=True`. O [Funcionário](./funcionarios.md) que é líder desta equipe. **Regra:** Um funcionário só pode ser líder de uma equipe por vez. |
| **coordenador** | `models.ForeignKey` | `UUID` | `to='hr.Funcionario'`, `on_delete=models.SET_NULL`, `null=True`, `blank=True`. O [Funcionário](./funcionarios.md) que coordena esta equipe. |
| **ativa** | `models.BooleanField`| `BOOLEAN` | `default=True`. Indica se a equipe está ativa e operacional. |
| **observacoes** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. |

**Constraints:**
*   `UniqueConstraint` para `lider`, garantindo que um funcionário seja líder de apenas uma equipe por vez.

### Enums para `hr.Equipe`
```python
class TipoEquipe(models.TextChoices):
    MANUAL = 'MANUAL', 'Manual'
    MECANIZADA = 'MECANIZADA', 'Mecanizada'
```

### 2.2. Modelo `hr.EquipeFuncionario` (Membros da Equipe)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **equipe** | `models.ForeignKey` | `UUID` | `to='hr.Equipe'`, `on_delete=models.CASCADE`. A equipe à qual o funcionário pertence. |
| **funcionario**| `models.ForeignKey` | `UUID` | `to='hr.Funcionario'`, `on_delete=models.CASCADE`. O funcionário membro da equipe. |
| **data_entrada** | `models.DateField` | `null=False`, `blank=False`. Data de entrada do funcionário na equipe. |
| **data_saida** | `models.DateField` | `null=True`, `blank=True`. Data de saída do funcionário da equipe. Se `null`, ainda está na equipe. |

**Constraint:** `UniqueConstraint` para `(equipe, funcionario, data_entrada)`. |
**Regra:** Um funcionário só pode estar em uma equipe ativa (`data_saida=null`) por vez. Ao adicioná-lo a uma nova equipe ativa, a alocação anterior deve ser encerrada (com `data_saida` preenchida).

---

## 3. Relacionamentos

-   `hr.Equipe` N:1 `core.Projeto`
-   `hr.Equipe` N:1 `hr.Funcionario` (Coordenador)
-   `hr.Equipe` 1:1 `hr.Funcionario` (Líder)
-   `hr.EquipeFuncionario` N:1 `hr.Equipe`
-   `hr.EquipeFuncionario` N:1 `hr.Funcionario`

---

## 4. Estratégia de Indexação

-   **`hr.Equipe`:** `(projeto, ativa, nome)`, `(lider)`, `(coordenador)`.
-   **`hr.EquipeFuncionario`:** `(equipe, data_saida)`, `(funcionario, data_saida)`.

---

## 5. Camada de Serviço (`EquipeService`)

-   **`criar_equipe(*, nome: str, tipo_equipe: Equipe.TipoEquipe, projeto: core.Projeto, lider: hr.Funcionario = None, coordenador: hr.Funcionario = None) -> Equipe:`**:
    -   Cria uma nova equipe, validando a unicidade do nome.
    -   **Regra:** Se um `lider` for fornecido, valida que ele não seja líder de outra equipe ativa.
-   **`adicionar_membro(*, equipe: Equipe, funcionario: hr.Funcionario, data_entrada: date) -> EquipeFuncionario:`**:
    -   Adiciona um funcionário a uma equipe.
    -   **Regra:** Se o funcionário já estiver em outra `EquipeFuncionario` ativa, encerra a alocação anterior (`data_saida`).
-   **`remover_membro(*, equipe_funcionario: EquipeFuncionario, data_saida: date) -> EquipeFuncionario:`**:
    -   Define a `data_saida` para o membro da equipe, encerrando sua participação.
