# Alojamento — Gestão de Alojamentos (Especificação Detalhada)

## 1. Visão Geral

O módulo de **Alojamento** gerencia os recursos de moradia da empresa, sejam eles casas alugadas individualmente, casas compartilhadas, alojamentos coletivos ou hotéis temporários. Ele permite o cadastro desses locais, suas características e a rastreabilidade da ocupação de funcionários, impactando diretamente os custos e a logística.

**Propósito Arquitetural:** Centralizar a gestão de moradias, vincular custos (aluguel, manutenção) e rastrear a alocação de funcionários a esses locais, fornecendo dados para o financeiro e auditoria.

---

## 2. Estrutura dos Modelos

### 2.1. Modelo `alojamento.Alojamento` (Cadastro do Local de Moradia)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **nome** | `models.CharField` | `VARCHAR(100)` | `unique=True`, `null=False`, `blank=False`. Nome identificador do alojamento (ex: "Casa Matriz - Q.1", "Alojamento Boa Esperança"). |
| **filial** | `models.ForeignKey` | `UUID` | `to='core.Filial'`, `on_delete=models.PROTECT`. A [Filial](../core/filial.md) à qual o alojamento pertence. |
| **responsavel_alojamento** | `models.ForeignKey` | `UUID` | `to='rh.Funcionario'`, `on_delete=models.SET_NULL`, `null=True`, `blank=True`. [Funcionário](../rh/funcionarios.md) responsável pela gestão do alojamento. |
| **tipo_moradia** | `models.CharField` | `VARCHAR(30)` | `choices=Alojamento.TipoMoradia.choices`. `null=False`, `blank=False`. (Enum: CASA_INDIVIDUAL, CASA_COMPARTILHADA, ALOJAMENTO_COLETIVO, HOTEL). |
| **capacidade** | `models.PositiveSmallIntegerField` | `SMALLINT` | `default=1`. Capacidade máxima de ocupação. |
| **contrato_aluguel_doc** | `models.ForeignKey` | `UUID` | `to='core.Documento'`, `on_delete=models.SET_NULL`, `null=True`, `blank=True`. Link para o [Documento](../core/documentos.md) PDF do contrato de aluguel do imóvel. |
| **valor_aluguel** | `models.DecimalField`| `DECIMAL(10, 2)` | `null=True`, `blank=True`. Valor mensal do aluguel. |
| **data_inicio_contrato** | `models.DateField` | `DATE` | `null=True`, `blank=True`. |
| **data_fim_contrato** | `models.DateField` | `DATE` | `null=True`, `blank=True`. |
| **observacoes** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. |
| **ativo** | `models.BooleanField`| `BOOLEAN` | `default=True`. Indica se o alojamento está ativo e disponível. |

### Enums para `alojamento.Alojamento`
```python
class TipoMoradia(models.TextChoices):
    CASA_INDIVIDUAL = 'CASA_INDIVIDUAL', 'Casa Individual'
    CASA_COMPARTILHADA = 'CASA_COMPARTILHADA', 'Casa Compartilhada'
    ALOJAMENTO_COLETIVO = 'ALOJAMENTO_COLETIVO', 'Alojamento Coletivo'
    HOTEL = 'HOTEL', 'Hotel / Hospedagem Temporária'
```

### 2.2. Modelo `alojamento.AlojamentoFuncionario` (Ocupação de Funcionário por Alojamento)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **funcionario**| `models.ForeignKey` | `UUID` | `to='rh.Funcionario'`, `on_delete=models.PROTECT`. O [Funcionário](../rh/funcionarios.md) alocado. |
| **alojamento** | `models.ForeignKey` | `UUID` | `to='alojamento.Alojamento'`, `on_delete=models.PROTECT`. O alojamento ocupado. |
| **data_entrada** | `models.DateField` | `DATE` | `null=False`, `blank=False`. Data de entrada do funcionário no alojamento. |
| **data_saida** | `models.DateField` | `DATE` | `null=True`, `blank=True`. Data de saída do funcionário do alojamento. Se `null`, funcionário está atualmente no alojamento. |
| **observacoes** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. |

**Constraint:** `UniqueConstraint` para `(funcionario, alojamento, data_entrada)`. |
**Regra:** Um funcionário só pode ter uma `AlojamentoFuncionario` ativa (`data_saida=null`) por vez. Ao criar uma nova alocação ativa, a alocação anterior ativa (se houver) deve ser automaticamente encerrada (`data_saida` preenchida).

---

## 3. Relacionamentos

-   `alojamento.Alojamento` N:1 `core.Filial`
-   `alojamento.Alojamento` N:1 `rh.Funcionario` (Responsável pelo alojamento)
-   `alojamento.Alojamento` N:1 `core.Documento` (Contrato de Aluguel)
-   `alojamento.AlojamentoFuncionario` N:1 `alojamento.Alojamento`
-   `alojamento.AlojamentoFuncionario` N:1 `rh.Funcionario`
-   `alojamento.Alojamento` 1:N `core.Endereco` (via tabela de vínculo `AlojamentoEndereco` - a ser criada no core se necessário, ou gerenciado via relacionamento reverso com `EnderecoService`)

---

## 4. Estratégia de Indexação

-   **`alojamento.Alojamento`:** `(filial, ativo, nome)`, `(responsavel_alojamento)`.
-   **`alojamento.AlojamentoFuncionario`:** `(funcionario, data_saida)`, `(alojamento, data_saida)`.

---

## 5. Camada de Serviço (`AlojamentoService`)

-   **`criar_alojamento(*, nome: str, filial: core.Filial, tipo_moradia: Alojamento.TipoMoradia, capacidade: int, data: dict) -> Alojamento:`**:
    -   Cria um novo alojamento, validando a unicidade do nome.
    -   Pode gerenciar o upload e vínculo do `contrato_aluguel_doc` (via `DocumentoService`).
-   **`alocar_funcionario_em_alojamento(*, funcionario: rh.Funcionario, alojamento: Alojamento, data_entrada: date) -> AlojamentoFuncionario:`**:
    -   Recebe o funcionário, o alojamento e a data de entrada.
    -   **Regra:** Verifica se o funcionário já possui uma `AlojamentoFuncionario` ativa (`data_saida=null`).
    -   Se sim, encerra a alocação anterior, definindo sua `data_saida` para `data_entrada - 1 dia` da nova alocação.
    -   Cria a nova instância de `AlojamentoFuncionario`.
-   **`desalocar_funcionario(*, alojamento_funcionario: AlojamentoFuncionario, data_saida: date) -> AlojamentoFuncionario:`**:
    -   Define a `data_saida` para uma `AlojamentoFuncionario` existente, marcando-a como inativa.
    -   **Regra:** `data_saida` não pode ser anterior a `data_entrada`.
-   **`get_ocupacao_atual(*, alojamento: Alojamento) -> int:`**:
    -   Retorna o número de funcionários atualmente alocados em um alojamento.
