# RH — Cargos (Especificação Detalhada)

## 1. Visão Geral

A entidade **Cargo** gerencia a estrutura formal de posições e funções dentro da organização. É um cadastro fundamental que serve como base para o vínculo empregatício do [Funcionário](./funcionarios.md) e para a definição de regras de saúde ocupacional (via `sst.CargoExame`).

**Propósito Arquitetural:** Padronizar as funções, associar classificações legais (CBO) e definir níveis hierárquicos, garantindo a consistência das vagas e requisitos para contratação.

---

## 2. Estrutura do Modelo (`hr.Cargo`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **nome** | `models.CharField` | `VARCHAR(100)` | `unique=True`, `null=False`, `blank=False`. Nome descritivo e único do cargo (ex: "Operador de Campo"). |
| **cbo** | `models.CharField` | `VARCHAR(10)` | `null=True`, `blank=True`. Código da Classificação Brasileira de Ocupações. |
| **salario_base** | `models.DecimalField`| `DECIMAL(10, 2)` | `null=True`, `blank=True`. Salário base para este cargo. |
| **risco_fisico** | `models.BooleanField`| `BOOLEAN` | `default=False`. Indica exposição a riscos físicos. |
| **risco_biologico** | `models.BooleanField`| `BOOLEAN` | `default=False`. Indica exposição a riscos biológicos. |
| **risco_quimico** | `models.BooleanField`| `BOOLEAN` | `default=False`. Indica exposição a riscos químicos. |
| **risco_ergonomico** | `models.BooleanField`| `BOOLEAN` | `default=False`. Indica exposição a riscos ergonômicos. |
| **risco_acidente** | `models.BooleanField`| `BOOLEAN` | `default=False`. Indica exposição a riscos de acidente. |
| **descricao**| `models.TextField`| `TEXT` | `null=True`, `blank=True`. Detalhes sobre as atribuições do cargo. |
| **nivel** | `models.CharField` | `VARCHAR(20)` | `choices=Cargo.Nivel.choices` (Enum: `OPERACIONAL`, `TECNICO`, `SUPERVISAO`, `COORDENACAO`, `GERENCIA`, `DIRETORIA`). `null=False`, `blank=False`. |
| **ativo** | `models.BooleanField`| `BOOLEAN` | `default=True`. Indica se o cargo está ativo e disponível para novas contratações. |
| *created_at* | `models.DateTimeField`| `TIMESTAMP` | `auto_now_add=True`. Herdado do `ModeloBase`. |
| *updated_at* | `models.DateTimeField`| `TIMESTAMP` | `auto_now=True`. Herdado do `ModeloBase`. |
| *deleted_at* | `models.DateTimeField`| `TIMESTAMP` | `null=True`, `default=None`. Herdado do `ModeloBase`. |

### Enum `Nivel` para `Cargo`
```python
class Nivel(models.TextChoices):
    OPERACIONAL = 'OPERACIONAL', 'Operacional'
    TECNICO = 'TECNICO', 'Técnico'
    SUPERVISAO = 'SUPERVISAO', 'Supervisão'
    COORDENACAO = 'COORDENACAO', 'Coordenação'
    GERENCIA = 'GERENCIA', 'Gerência'
    DIRETORIA = 'DIRETORIA', 'Diretoria'
```

---

## 3. Relacionamentos

-   **`hr.Funcionario` (1:N):** Um cargo pode ter múltiplos funcionários. O `Funcionario` terá uma `ForeignKey` para `hr.Cargo`.
-   **`sst.CargoExame` (1:N):** Um cargo pode ter múltiplas configurações de exames. A tabela `sst.CargoExame` terá uma `ForeignKey` para `hr.Cargo`.

---

## 4. Estratégia de Indexação

-   **Índice Único:** no campo `nome` (já garantido pelo `unique=True`).
-   **Índice Padrão (B-Tree):** em `(ativo, nome)` para otimizar listagens de cargos ativos ordenados por nome.

--जै---नग

## 5. Camada de Serviço (`CargoService`)

A interação com este modelo deve ser feita exclusivamente através do `CargoService`.

-   **`create_cargo(*, nome: str, nivel: Cargo.Nivel, cbo: str = None, descricao: str = None) -> Cargo:`**:
    -   Cria uma nova instância de `Cargo`, validando a unicidade do nome.
-   **`update_cargo(*, cargo: Cargo, data: dict) -> Cargo:`**:
    -   Atualiza os atributos de um `Cargo` existente.
    -   **Regra:** Não permite alterar `nome` se já existirem funcionários vinculados (pode exigir reavaliação de impacto em dados históricos).
-   **`toggle_active_status(*, cargo: Cargo, is_active: bool) -> Cargo:`**:
    -   Altera o status `ativo` do cargo.
    -   **Regra:** Um cargo não pode ser inativado se ainda houver `Funcionario`s ativos vinculados a ele. Deve ser sugerida uma migração de cargo para esses funcionários primeiro.
-   Encapsular toda a lógica de validação, como a verificação de CBO, se necessário, e o tratamento de exceções (ex: `NomeDuplicadoError`, `CargoAtivoComFuncionariosError`).

---

## 6. Documentos Obrigatórios (`hr.CargoDocumento`)

### 6.1. Visão Geral
A entidade **Cargo Documento** (agora unificada ao domínio Cargo) define quais documentos são obrigatórios para cada Cargo.

### 6.2. Estrutura do Modelo
| Atributo | Tipo Django | Regras |
| :--- | :--- | :--- |
| **id** | `UUIDField` | PK. |
| **cargo** | `ForeignKey` | `hr.Cargo`. |
| **documento_tipo** | `CharField` | Enum `core.Documento.Tipo`. (Ex: CNH, RG, Diploma). |
| **obrigatorio** | `BooleanField` | Se o documento bloqueia a admissão/ativação. |
| **condicional** | `TextField` | (Opcional) Regra textual (ex: "Apenas se dirigir"). |

**Constraint:** Único por `(cargo, documento_tipo)`.

### 6.3. Camada de Serviço
A gestão é feita pelos métodos do próprio `CargoService`:
- `vincular_documento_cargo(...)`
- `get_documentos_cargo(...)`
- `validar_documentos_funcionario(funcionario)`: Usado na admissão/ativação.