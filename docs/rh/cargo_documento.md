# RH — Cargo Documento (Especificação Detalhada)

## 1. Visão Geral

A entidade **Cargo Documento** define quais documentos são obrigatórios para cada [Cargo](./cargos.md) específico. Ela estabelece as regras de compliance e os requisitos documentais para a admissão e manutenção do vínculo empregatício.

**Propósito Arquitetural:** Centralizar e parametrizar a validação de documentos por cargo, permitindo que o sistema verifique automaticamente se um funcionário possui toda a documentação necessária para sua função.

---

## 2. Estrutura do Modelo (`hr.CargoDocumento`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **cargo** | `models.ForeignKey` | `UUID` | `to='hr.Cargo'`, `on_delete=models.CASCADE`. O cargo ao qual esta regra documental se aplica. |
| **documento_tipo** | `models.CharField` | `VARCHAR(50)` | `choices=core.Documento.Tipo.choices`. O tipo de documento ([`core.Documento`](../core/documentos.md)) que é exigido. |
| **obrigatorio** | `models.BooleanField`| `BOOLEAN` | `default=True`. Indica se a posse deste documento é mandatório para o cargo. |
| **condicional** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. (Opcional) Descrição de condições adicionais para a obrigatoriedade (ex: "Obrigatório se tiver CNH"). |

**Constraint:** `UniqueConstraint` para `(cargo, documento_tipo)`, garantindo que cada tipo de documento tenha apenas uma regra por cargo.

---

## 3. Relacionamentos

-   `hr.CargoDocumento` N:1 `hr.Cargo`

---

## 4. Estratégia de Indexação

-   **Índice Único Composto:** em `(cargo, documento_tipo)` (já garantido pelo `UniqueConstraint`).

---

## 5. Camada de Serviço (`CargoDocumentoService` / `FuncionarioService`)

A gestão da obrigatoriedade dos documentos será feita através de um serviço dedicado. O `FuncionarioService` utilizará esta configuração durante o processo de admissão.

-   **`configurar_documento_para_cargo(*, cargo: Cargo, documento_tipo: core.Documento.Tipo, obrigatorio: bool = True, condicional: str = None) -> CargoDocumento:`**:
    -   Cria ou atualiza uma regra de documento para um cargo.
-   **`get_documentos_obrigatorios_para_cargo(*, cargo: Cargo) -> QuerySet[CargoDocumento]:`**:
    -   Retorna todos os documentos que são configurados como obrigatórios para um determinado cargo.

### Lógica no `FuncionarioService.admitir_funcionario`
Durante o processo de admissão, após a criação do `Funcionario` e o upload de seus documentos:

1.  O `FuncionarioService` consulta `CargoDocumentoService.get_documentos_obrigatorios_para_cargo(funcionario.cargo)`.
2.  Para cada `CargoDocumento` retornado, o serviço verifica se existe um `core.Documento` correspondente (do `documento_tipo` exigido) vinculado à `PessoaFisica` do funcionário.
3.  Se um documento obrigatório não for encontrado, a admissão pode ser impedida ou marcada como pendente, dependendo da regra de negócio.
