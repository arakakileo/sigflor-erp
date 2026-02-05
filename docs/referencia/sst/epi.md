# SST — Equipamentos de Proteção Individual (EPI)

## 1. Visão Geral

O submódulo de **EPIs** no módulo de SST é responsável por gerenciar o catálogo de equipamentos, o controle de estoque (CA) e o fluxo de entrega e devolução para os funcionários.

**Propósito Arquitetural:** Garantir o rastreamento individualizado da entrega de EPIs, controle de validade (CA e troca) e conformidade com as normas regulamentadoras (NR-6).

---

## 2. Estrutura dos Modelos

### 2.1. Modelo `sst.TipoEPI` (Categoria)

Entidade classificatória para agrupar EPIs (ex: "Capacete", "Luva de Vaqueta"). Usado para definir requisitos no `Cargo`.

| Atributo | Tipo Django | Regras |
| :--- | :--- | :--- |
| **id** | `UUIDField` | PK, Auto. |
| **nome** | `CharField(100)` | Único. Nome da categoria. |
| **descricao** | `TextField` | Opcional. |
| **created_at/updated_at** | `DateTimeField` | Auditoria. |

### 2.2. Modelo `sst.EPI` (Item de Catálogo)

Representa um equipamento físico específico, incluindo fabricante e CA (Certificado de Aprovação).

| Atributo | Tipo Django | Regras |
| :--- | :--- | :--- |
| **id** | `UUIDField` | PK, Auto. |
| **tipo** | `ForeignKey` | `sst.TipoEPI`. Categoria do equipamento. |
| **nome** | `CharField(100)` | Nome comercial (ex: "Luva Vaqueta Tam G - Marca X"). |
| **fabricante** | `CharField(100)` | Fabricante do equipamento. |
| **ca** | `CharField(20)` | Código do Certificado de Aprovação. Obrigatório. |
| **validade_ca** | `DateField` | Data de validade do certificado. |
| **ativo** | `BooleanField` | Disponibilidade para entrega. |

### 2.3. Modelo `sst.CargoEPI` (Requisito por Cargo)

Aninhado ao `Cargo`, define a periodicidade de troca obrigatória.

| Atributo | Tipo Django | Regras |
| :--- | :--- | :--- |
| **cargo** | `ForeignKey` | `hr.Cargo`. |
| **tipo_epi** | `ForeignKey` | `sst.TipoEPI`. Requisito genérico (ex: requer "Capacete"). |
| **periodicidade_troca_dias** | `IntegerField` | Dias para troca regular (ex: 90 dias). |

**Constraint:** Único por `(cargo, tipo_epi)`.

### 2.4. Modelo `sst.EntregaEPI` (Registro de Movimentação)

Registra o fato da entrega de um item específico para um funcionário.

| Atributo | Tipo Django | Regras |
| :--- | :--- | :--- |
| **id** | `UUIDField` | PK, Auto. |
| **funcionario** | `ForeignKey` | `hr.Funcionario`. Recebedor. |
| **epi** | `ForeignKey` | `sst.EPI`. Item entregue. |
| **data_entrega** | `DateField` | Data da entrega. |
| **quantidade** | `IntegerField` | Qtd entregue (padrão 1). |
| **data_validade_uso** | `DateField` | Calculado: `data_entrega + CargoEPI.periodicidade`. |
| **data_devolucao** | `DateField` | Opcional. Preenchido na baixa. |
| **motivo_devolucao** | `CharField` | Enum: `DESGASTE`, `DANIFICADO`, `PERDA`, `DEMISSAO`, `OUTRO`. |

---

## 3. Relacionamentos

- `sst.CargoEPI` N:1 `hr.Cargo`
- `sst.EntregaEPI` N:1 `hr.Funcionario`
- `sst.EntregaEPI` N:1 `sst.EPI`

---

## 4. Camada de Serviço (`EPIService`)

- **`vincular_epi_cargo`**: Configura obrigatoriedade de EPI para um cargo.
- **`registrar_entrega`**:
    - Cria `EntregaEPI`.
    - Calcula `data_validade_uso` buscando a regra em `CargoEPI`.
- **`registrar_devolucao`**: Define `data_devolucao` e motivo.
- **`get_epis_a_vencer`**: Lista entregas próximas da troca obrigatória.

---

## 5. Endpoints (API)

- `GET /api/sst/tipos-epis/`: CRUD de Tipos.
- `GET /api/sst/epis/`: CRUD de Catálogo.
- `GET /api/rh/cargos/{id}/epis/`: Listar requisitos do cargo (via CargoViewSet).
- `POST /api/sst/entregas-epi/`: Registrar entrega.
- `POST /api/sst/entregas-epi/{id}/devolver/`: Action para registrar devolução.
