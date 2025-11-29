# RH — Dependente (Especificação Detalhada)

## 1. Visão Geral

A entidade **Dependente** representa uma pessoa física que possui vínculo de dependência com um [Funcionário](./funcionarios.md). Essa informação é fundamental para o cálculo de benefícios, declarações fiscais e controle de elegibilidade a programas sociais.

**Propósito Arquitetural:** Centralizar os dados dos dependentes, garantindo que suas informações civis sejam únicas (`PessoaFisica`) e que a relação de dependência com o funcionário seja clara e auditável.

---

## 2. Estrutura do Modelo (`hr.Dependente`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **funcionario** | `models.ForeignKey` | `UUID` | `to='hr.Funcionario'`, `on_delete=models.CASCADE`. O funcionário titular. |
| **pessoa_fisica** | `models.OneToOneField` | `UUID` | `to='core.PessoaFisica'`, `on_delete=models.PROTECT`. **Regra:** Os dados civis do dependente. |
| **parentesco** | `models.CharField` | `VARCHAR(30)` | `choices=Dependente.Parentesco.choices`. `null=False`, `blank=False`. (Enum: FILHO, CONJUGE, IRMAO, OUTROS). |
| **dependencia_irrf** | `models.BooleanField`| `BOOLEAN` | `default=False`. Indica se é dependente para fins de Imposto de Renda. |
| **ativo** | `models.BooleanField`| `BOOLEAN` | `default=True`. Indica se o dependente está ativo (ex: ainda menor de idade, estudante). |

**Constraint:** `UniqueConstraint` para `(funcionario, pessoa_fisica)`, garantindo que uma pessoa física seja dependente de um funcionário apenas uma vez.

### Enums para `Dependente`
```python
class Parentesco(models.TextChoices):
    FILHO = 'FILHO', 'Filho(a)'
    CONJUGE = 'CONJUGE', 'Cônjuge'
    IRMAO = 'IRMAO', 'Irmão(ã)'
    PAIS = 'PAIS', 'Pais'
    OUTROS = 'OUTROS', 'Outros'
```

---

## 3. Relacionamentos

-   `hr.Dependente` N:1 `hr.Funcionario`
-   `hr.Dependente` 1:1 `core.PessoaFisica`

---

## 4. Estratégia de Indexação

-   **Índice Único Composto:** em `(funcionario, pessoa_fisica)`.
-   **Índice Padrão (B-Tree):** em `(funcionario, ativo)` para listar dependentes ativos de um funcionário.

---

## 5. Camada de Serviço (`DependenteService` / `FuncionarioService`)

A criação e gestão de dependentes será orquestrada via `DependenteService`, mas frequentemente acionada a partir do `FuncionarioService`.

-   **`vincular_dependente(*, funcionario: Funcionario, pessoa_fisica_data: dict, parentesco: Dependente.Parentesco, dependencia_irrf: bool = False) -> Dependente:`**:
    -   Recebe a instância do `Funcionario`, dados da `PessoaFisica` do dependente e os dados de dependência.
    -   Chama `PessoaFisicaService.get_or_create_pessoa_fisica` para garantir a unicidade do CPF do dependente e a criação/reutilização da `PessoaFisica`.
    -   Cria a instância de `Dependente`, estabelecendo o vínculo com o `Funcionario` e a `PessoaFisica`.
    -   **Regra:** Atualiza a flag `tem_dependente` no `hr.Funcionario` para `True`.
-   **`desativar_dependente(*, dependente: Dependente) -> Dependente:`**:
    -   Altera o status `ativo` para `False` (soft delete). 
    -   **Regra:** Se for o último dependente ativo do funcionário, atualiza a flag `tem_dependente` no `hr.Funcionario` para `False`.
-   Encapsular validações como idade limite para dependência de IR, se aplicável, e regras para tipos de parentesco.