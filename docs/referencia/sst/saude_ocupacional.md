# SST — Saúde Ocupacional (Especificação Detalhada)

## 1. Visão Geral

O submódulo de **Saúde Ocupacional** no módulo de SST (Saúde e Segurança do Trabalho) é responsável por gerenciar os Atestados de Saúde Ocupacional (ASOs) e os exames associados. Ele permite o controle granular da validade de cada exame, garantindo a conformidade legal e a segurança do trabalhador.

**Propósito Arquitetural:** Automatizar o controle de periodicidade de exames, gerenciar o ciclo de vida dos ASOs (de solicitação a finalização) e centralizar a documentação dos exames de saúde.

---

## 2. Estrutura dos Modelos

### 2.1. Modelo `core.Exame` (Cadastro Mestre de Exames)

*(Este modelo reside no módulo `core` por ser uma entidade mestre genérica, utilizada por outros contextos se necessário.)*

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **nome** | `models.CharField` | `VARCHAR(100)` | `unique=True`, `null=False`, `blank=False`. Nome descritivo do exame. |
| **descricao**| `models.TextField`| `TEXT` | `null=True`, `blank=True`. |

### 2.2. Modelo `sst.CargoExame` (Regra de Periodicidade por Cargo)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **cargo** | `models.ForeignKey` | `UUID` | `to='hr.Cargo'`, `on_delete=models.PROTECT`. |
| **exame** | `models.ForeignKey` | `UUID` | `to='core.Exame'`, `on_delete=models.PROTECT`. |
| **periodicidade_meses**| `models.PositiveSmallIntegerField` | `SMALLINT` | `null=False`, `blank=False`. Periodicidade em meses (ex: 6, 12, 18, 24). |

**Constraint:** `UniqueConstraint` para `(cargo, exame)`, garantindo uma única periodicidade por exame para cada cargo.

### 2.3. Modelo `sst.ASO` (Atestado de Saúde Ocupacional - O Processo)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **funcionario**| `models.ForeignKey` | `UUID` | `to='hr.Funcionario'`, `on_delete=models.PROTECT`. |
| **tipo** | `models.CharField` | `VARCHAR(30)` | `choices=ASO.Tipo.choices` (Enum: `ADMISSIONAL`, `PERIODICO`, `DEMISSIONAL`, `RETORNO_AO_TRABALHO`, `MUDANCA_DE_FUNCAO`). `null=False`, `blank=False`. |
| **status** | `models.CharField` | `VARCHAR(20)` | `choices=ASO.Status.choices` (Enum: `ABERTO`, `FINALIZADO`). `default='ABERTO'`. |
| **data_solicitacao** | `models.DateField` | `DATE` | `auto_now_add=True`. Data de criação/solicitação do ASO. |
| **data_finalizacao**| `models.DateField` | `DATE` | `null=True`, `blank=True`. Preenchido quando o ASO é `FINALIZADO`. |
| **medico_responsavel** | `models.CharField` | `VARCHAR(255)` | `null=True`, `blank=True`. Nome e CRM do médico que assinou. Preenchido ao `FINALIZAR`. |
| **resultado_final** | `models.CharField` | `VARCHAR(30)` | `choices=ASO.Resultado.choices` (Enum: `APTO`, `INAPTO`). `null=True`, `blank=True`. Preenchido ao `FINALIZAR`. |
| **observacoes**| `models.TextField`| `TEXT` | `null=True`, `blank=True`. |

### Enums para `ASO`
```python
class Tipo(models.TextChoices):
    ADMISSIONAL = 'ADMISSIONAL', 'Admissional'
    PERIODICO = 'PERIODICO', 'Periódico'
    DEMISSIONAL = 'DEMISSIONAL', 'Demissional'
    RETORNO_AO_TRABALHO = 'RETORNO_AO_TRABALHO', 'Retorno ao Trabalho'
    MUDANCA_DE_FUNCAO = 'MUDANCA_DE_FUNCAO', 'Mudança de Função'

class Status(models.TextChoices):
    ABERTO = 'ABERTO', 'Aberto'
    FINALIZADO = 'FINALIZADO', 'Finalizado'

class Resultado(models.TextChoices):
    APTO = 'APTO', 'Apto'
    INAPTO = 'INAPTO', 'Inapto'
```

### 2.4. Modelo `sst.ExameRealizado` (Registro de Exame Individual)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **aso** | `models.ForeignKey` | `UUID` | `to='sst.ASO'`, `on_delete=models.CASCADE`. Vínculo com o ASO pai. |
| **exame** | `models.ForeignKey` | `UUID` | `to='core.Exame'`, `on_delete=models.PROTECT`. O tipo de exame realizado. |
| **data_realizacao**| `models.DateField` | `DATE` | `null=True`, `blank=True`. Data específica em que *este* exame foi feito. |
| **data_vencimento**| `models.DateField` | `DATE` | `null=True`, `blank=True`. **Regra:** Calculado automaticamente. |
| **resultado**| `models.CharField` | `VARCHAR(30)` | `choices=ExameRealizado.Resultado.choices` (Enum: `NORMAL`, `ALTERADO`, `NAO_REALIZADO`). `null=True`. |
| **observacoes**| `models.TextField`| `TEXT` | `null=True`, `blank=True`. |

### Enum para `ExameRealizado`
```python
class Resultado(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    ALTERADO = 'ALTERADO', 'Alterado'
    PENDENTE = 'PENDENTE', 'Pendente'
```

---

## 3. Relacionamentos

-   `sst.CargoExame` N:1 `hr.Cargo`
-   `sst.CargoExame` N:1 `core.Exame`
-   `sst.ASO` N:1 `hr.Funcionario`
-   `sst.ExameRealizado` N:1 `sst.ASO`
-   `sst.ExameRealizado` N:1 `core.Exame`

---

## 4. Camada de Serviço (`ASOService`)

A lógica de negócio para ASOs é centralizada no `ASOService`.

### 4.1. `gerar_solicitacao(*, funcionario: Funcionario, tipo: ASO.Tipo, user: Usuario) -> ASO:`
-   Cria um novo `ASO` com `status='ABERTO'`.
-   **Lógica Automática:** Identifica os exames exigidos pelo `Cargo` do funcionário (via `CargoExame`).
-   Cria os registros de `ExameRealizado` com status `PENDENTE` para cada exame obrigatório.

### 4.2. `concluir(*, aso: ASO, medico: str, resultado: Resultado, user: Usuario) -> ASO:`
-   Valida se todos os exames foram registrados (nenhum pendente/sem data).
-   Define `data_finalizacao` e `status='FINALIZADO'`.

### 4.3.Integração com RH
-   Ao tentar ativar um funcionário (`FuncionarioService.ativar`), o sistema verifica se existe um ASO Admissional `FINALIZADO` e `APTO`.

---

## 5. Endpoints (API)

-   `POST /api/sst/asos/gerar_solicitacao/`: Criar um ASO.
-   `POST /api/sst/asos/{id}/concluir/`: Finalizar.
-   `POST /api/sst/exames-realizados/{id}/registrar_resultado/`: Preencher data e resultado de um exame.

