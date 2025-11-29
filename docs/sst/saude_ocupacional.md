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
| **status** | `models.CharField` | `VARCHAR(20)` | `choices=ASO.Status.choices` (Enum: `ABERTO`, `EM_ANDAMENTO`, `FINALIZADO`, `CANCELADO`). `default='ABERTO'`. |
| **data_solicitacao** | `models.DateField` | `DATE` | `auto_now_add=True`. Data de criação/solicitação do ASO. |
| **data_finalizacao**| `models.DateField` | `DATE` | `null=True`, `blank=True`. Preenchido quando o ASO é `FINALIZADO`. |
| **medico_responsavel` | `models.CharField` | `VARCHAR(255)` | `null=True`, `blank=True`. Nome e CRM do médico que assinou. Preenchido ao `FINALIZAR`. |
| **resultado_final` | `models.CharField` | `VARCHAR(30)` | `choices=ASO.Resultado.choices` (Enum: `APTO`, `INAPTO`, `APTO_COM_RESTRICOES`). `null=True`, `blank=True`. Preenchido ao `FINALIZAR`. |
| **observacoes**| `models.TextField`| `TEXT` | `null=True`, `blank=True`. |
| **documento_aso_pdf**| `models.ForeignKey` | `UUID` | `to='core.Documento'`, `null=True`, `blank=True`, `on_delete=models.SET_NULL`. **Regra:** Link para o PDF escaneado do ASO completo. Anexado somente quando o ASO é `FINALIZADO`. |

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
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
    FINALIZADO = 'FINALIZADO', 'Finalizado'
    CANCELADO = 'CANCELADO', 'Cancelado'

class Resultado(models.TextChoices):
    APTO = 'APTO', 'Apto'
    INAPTO = 'INAPTO', 'Inapto'
    APTO_COM_RESTRICOES = 'APTO_COM_RESTRICOES', 'Apto com Restrições'
```

### 2.4. Modelo `sst.ExameRealizado` (Registro de Exame Individual)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **aso** | `models.ForeignKey` | `UUID` | `to='sst.ASO'`, `on_delete=models.CASCADE`. Vínculo com o ASO pai. |
| **exame** | `models.ForeignKey` | `UUID` | `to='core.Exame'`, `on_delete=models.PROTECT`. O tipo de exame realizado. |
| **data_realizacao**| `models.DateField` | `DATE` | `null=False`, `blank=False`. Data específica em que *este* exame foi feito. |
| **data_vencimento**| `models.DateField` | `DATE` | `null=False`, `blank=False`. **Regra:** Calculado automaticamente. |
| **resultado**| `models.CharField` | `VARCHAR(30)` | `choices=ExameRealizado.Resultado.choices` (Enum: `NORMAL`, `ALTERADO`, `NAO_REALIZADO`). `null=False`, `blank=False`. |
| **observacoes**| `models.TextField`| `TEXT` | `null=True`, `blank=True`. |

### Enum para `ExameRealizado`
```python
class Resultado(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    ALTERADO = 'ALTERADO', 'Alterado'
    NAO_REALIZADO = 'NAO_REALIZADO', 'Não Realizado'
```

---

## 3. Relacionamentos

-   `sst.CargoExame` N:1 `hr.Cargo`
-   `sst.CargoExame` N:1 `core.Exame`
-   `sst.ASO` N:1 `hr.Funcionario`
-   `sst.ASO` N:1 `core.Documento` (para o PDF do ASO)
-   `sst.ExameRealizado` N:1 `sst.ASO`
-   `sst.ExameRealizado` N:1 `core.Exame`

---

## 4. Estratégia de Indexação

-   **`sst.ASO`:** `(funcionario, status, data_solicitacao)`
-   **`sst.ExameRealizado`:** `(funcionario, exame, data_vencimento)`, `(aso, exame)`
-   **`sst.CargoExame`:** `(cargo, exame)` (já coberto pelo UniqueConstraint)

---

## 5. Camada de Serviço (`SSTService` / `ASOService`)

A lógica de negócio para ASOs é complexa e será encapsulada em serviços dedicados, possivelmente `ASOService`.

### 5.1. `solicitar_aso(*, funcionario: Funcionario, tipo: ASO.Tipo) -> ASO:`
-   Cria um novo `ASO` com `status='ABERTO'`.
-   **Lógica de Pré-população:**
    -   Se `tipo='DEMISSIONAL'`: Popula automaticamente todos os `ExameRealizado` necessários para o `Cargo` atual do funcionário, buscando em `CargoExame`, **independentemente da data de vencimento**. Define `data_vencimento` como a data do ASO + periodicidade, mas sinaliza que o exame deve ser feito.
    -   Se `tipo='PERIODICO'`: Identifica os exames vencidos ou a vencer (dentro de um período configurável, ex: 60 dias) para o `Funcionario` com base nos `ExameRealizado` anteriores e `CargoExame`. Adiciona **apenas** esses exames ao `ASO`.
    -   Para outros tipos: Popula com base em exames relevantes para o cargo.
-   Os `ExameRealizado` são criados com `data_realizacao` e `resultado` vazios.

### 5.2. `registrar_exame(*, aso: ASO, exame: Exame, data_realizacao: date, resultado: ExameRealizado.Resultado) -> ExameRealizado:`
-   Recebe o `ASO` em `status='ABERTO'` ou `EM_ANDAMENTO`.
-   Busca o `CargoExame` correspondente para obter a `periodicidade_meses`.
-   Calcula `data_vencimento = data_realizacao + periodicidade_meses`.
-   Atualiza um `ExameRealizado` existente ou cria um novo.
-   **Validação:** Se o `ASO` é `PERIODICO`, impede a adição de exames que já estão válidos (não vencidos).
-   Atualiza o `status` do `ASO` para `EM_ANDAMENTO` se for o primeiro exame registrado.

### 5.3. `finalizar_aso(*, aso: ASO, medico_responsavel: str, resultado_final: ASO.Resultado, documento_pdf: File = None) -> ASO:`
-   Recebe o `ASO` em `status='EM_ANDAMENTO'`.
-   Valida se todos os `ExameRealizado` obrigatórios foram registrados.
-   Define `data_finalizacao`, `medico_responsavel`, `resultado_final`.
-   Se `documento_pdf` for fornecido, cria um `core.Documento` e o vincula a `documento_aso_pdf`.
-   Atualiza o `status` do `ASO` para `FINALIZADO`.

### 5.4. `get_exames_a_vencer(*, funcionario: Funcionario = None, dias: int = 90) -> QuerySet[ExameRealizado]:`
-   Retorna uma lista de `ExameRealizado` (para um funcionário ou todos) cuja `data_vencimento` está dentro do período especificado. Base para notificações.

### 5.5. `editar_exame_realizado(*, exame_realizado: ExameRealizado, data: dict) -> ExameRealizado:`
-   Permite a edição dos campos `data_realizacao`, `resultado`, `observacoes`.
-   Recalcula `data_vencimento` se `data_realizacao` for alterada.

### 5.6. `excluir_exame_realizado(*, exame_realizado: ExameRealizado)`
-   Realiza o soft delete do `ExameRealizado`.

---

## 6. Endpoints da API (Exemplos)

-   `POST /api/sst/asos/`: Criar um ASO (Solicitar).
-   `GET /api/sst/asos/{id}/`: Obter detalhes de um ASO.
-   `POST /api/sst/asos/{aso_id}/exames/`: Registrar um exame individual para um ASO.
-   `PATCH /api/sst/asos/{aso_id}/exames/{exame_realizado_id}/`: Editar um exame individual.
-   `DELETE /api/sst/asos/{aso_id}/exames/{exame_realizado_id}/`: Soft delete de um exame individual.
-   `POST /api/sst/asos/{id}/finalizar/`: Finalizar um ASO.
-   `GET /api/sst/exames-a-vencer/`: Listar exames próximos do vencimento.

---

## 7. Próximos Passos

Com o módulo SST e a saúde ocupacional detalhados, podemos agora focar na especificação do módulo RH, começando com `Cargo` e `Funcionario`, que agora terão relações claras com `SST` e `Core`.
