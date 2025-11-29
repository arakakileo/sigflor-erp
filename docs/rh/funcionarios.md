# RH — Funcionários (Especificação Detalhada)

## 1. Visão Geral

A entidade **Funcionário** é o cadastro central de colaboradores do sistema, representando o **vínculo empregatício** de uma [Pessoa Física](../core/pessoa_fisica.md) com uma [Empresa](../core/empresa.md) do grupo.

Este modelo gerencia o ciclo de vida do colaborador na empresa, desde a admissão até o desligamento, incluindo dados contratuais, alocação em centros de custo (Projetos) e informações complementares necessárias para o RH, folha de pagamento e SST.

**Propósito Arquitetural:** Centralizar todas as informações do vínculo empregatício, permitir a rastreabilidade do histórico funcional e integrar dados para outros módulos do ERP.

---

## 2. Estrutura do Modelo (`hr.Funcionario`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **pessoa_fisica** | `models.OneToOneField` | `UUID` | `to='core.PessoaFisica'`, `on_delete=models.PROTECT`. **Regra:** O vínculo com a pessoa civil. |
| **empresa** | `models.ForeignKey` | `UUID` | `to='core.Empresa'`, `on_delete=models.PROTECT`. A empresa empregadora. |
| **matricula** | `models.CharField` | `VARCHAR(20)` | `unique=True`, `null=False`, `blank=False`. **Regra:** Gerada automaticamente (ex: AAAANNNC - Ano + Sequencial 4 dígitos + Dígito de Controle). |
| **cargo** | `models.ForeignKey` | `UUID` | `to='hr.Cargo'`, `on_delete=models.PROTECT`. O [Cargo](./cargos.md) ocupado. |
| **data_admissao** | `models.DateField` | `DATE` | `null=False`, `blank=False`. |
| **data_demissao** | `models.DateField` | `DATE` | `null=True`, `blank=True`. Preenchida no desligamento. |
| **status** | `models.CharField` | `VARCHAR(30)` | `choices=Funcionario.Status.choices`. `default='ATIVO'`. (Enum: ATIVO, AFASTADO, FERIAS, DEMITIDO). |
| **tipo_contrato** | `models.CharField` | `VARCHAR(30)` | `choices=Funcionario.TipoContrato.choices`. `null=False`, `blank=False`. (Enum: CLT, PJ, ESTAGIARIO). |
| **salario_nominal** | `models.DecimalField`| `DECIMAL(10, 2)` | `null=False`, `blank=False`. Salário contratual. **Regra:** Se não informado na criação, assume o `salario_base` do `Cargo`. Se informado, o valor mínimo deve ser igual ou superior ao `salario_base` do `Cargo` (se `salario_base` estiver definido). |
| **turno** | `models.CharField` | `VARCHAR(20)` | `choices=Funcionario.Turno.choices`. `null=True`, `blank=True`. (Enum: DIURNO, NOTURNO). |
| **projeto** | `models.ForeignKey` | `UUID` | `to='core.Projeto'`, `on_delete=models.PROTECT`, `null=True`, `blank=True`. O [Projeto](../core/projeto.md) ao qual o funcionário está alocado como centro de custo. |
| **peso_corporal** | `models.DecimalField`| `DECIMAL(5, 2)` | `null=True`, `blank=True`. Peso do funcionário em kg. |
| **altura** | `models.DecimalField`| `DECIMAL(3, 2)` | `null=True`, `blank=True`. Altura do funcionário em metros. |
| **indicacao** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. Informações sobre quem indicou o funcionário. |
| **cidade_atual** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. Cidade de localização do funcionário no momento da contratação/atualização (para logística de demissão). |
| **gestor_imediato** | `models.ForeignKey` | `UUID` | `to='self'`, `on_delete=models.SET_NULL`, `null=True`, `blank=True`. (Autoreferência para hierarquia). |
| **tem_dependente** | `models.BooleanField`| `BOOLEAN` | `default=False`. **Regra:** Gerenciado automaticamente, `True` se houver `Dependentes` vinculados. |

**Dados de Documentação Trabalhista:**
| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **ctps_numero** | `models.CharField` | `VARCHAR(20)` | `null=True`, `blank=True`. |
| **ctps_serie** | `models.CharField` | `VARCHAR(10)` | `null=True`, `blank=True`. |
| **ctps_uf** | `models.CharField` | `VARCHAR(2)` | `choices=core.Endereco.UF.choices`. `null=True`, `blank=True`. |
| **pis_pasep** | `models.CharField` | `VARCHAR(15)` | `null=True`, `blank=True`. |

**Dados Bancários:**
| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **banco** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. |
| **agencia** | `models.CharField` | `VARCHAR(20)` | `null=True`, `blank=True`. |
| **conta_corrente** | `models.CharField` | `VARCHAR(30)` | `null=True`, `blank=True`. |
| **tipo_conta** | `models.CharField` | `VARCHAR(20)` | `choices=Funcionario.TipoConta.choices`. `null=True`, `blank=True`. (Enum: CORRENTE, POUPANCA). |
| **chave_pix** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. |

**Dados de Uniforme/EPI (opcional - para futuras integrações):**
| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **tamanho_camisa** | `models.CharField` | `VARCHAR(10)` | `null=True`, `blank=True`. (Ex: P, M, G, GG). |
| **tamanho_calca** | `models.CharField` | `VARCHAR(10)` | `null=True`, `blank=True`. (Ex: 38, 40, 42). |
| **tamanho_calcado** | `models.CharField` | `VARCHAR(10)` | `null=True`, `blank=True`. (Ex: 39, 40, 41). |

### Enums para `Funcionario`
```python
class Status(models.TextChoices):
    ATIVO = 'ATIVO', 'Ativo'
    AFASTADO = 'AFASTADO', 'Afastado'
    FERIAS = 'FERIAS', 'Em Férias'
    DEMITIDO = 'DEMITIDO', 'Demitido'

class TipoContrato(models.TextChoices):
    CLT = 'CLT', 'CLT'
    PJ = 'PJ', 'Pessoa Jurídica'
    ESTAGIARIO = 'ESTAGIARIO', 'Estagiário'
    TEMPORARIO = 'TEMPORARIO', 'Temporário'
    APRENDIZ = 'APRENDIZ', 'Jovem Aprendiz'

class Turno(models.TextChoices):
    DIURNO = 'DIURNO', 'Diurno'
    NOTURNO = 'NOTURNO', 'Noturno'
    INTEGRAL = 'INTEGRAL', 'Integral'
    FLEXIVEL = 'FLEXIVEL', 'Flexível'

class TipoConta(models.TextChoices):
    CORRENTE = 'CORRENTE', 'Conta Corrente'
    POUPANCA = 'POUPANCA', 'Conta Poupança'
```

---

## 3. Relacionamentos

-   **`core.PessoaFisica` (1:1):** O funcionário **é** uma pessoa física. (`OneToOneField`).
-   **`core.Empresa` (N:1):** O funcionário pertence a uma empresa do grupo. (`ForeignKey`).
-   **`hr.Cargo` (N:1):** O funcionário ocupa um cargo. (`ForeignKey`).
-   **`core.Projeto` (N:1):** O funcionário está alocado a um [Projeto](../core/projeto.md) (centro de custo). (`ForeignKey`).
-   **`self` (N:1 - `gestor_imediato`):** Para hierarquia (`ForeignKey` autoreferencial).
-   **`hr.Dependente` (1:N):** Um funcionário pode ter múltiplos dependentes. (`Dependente` terá FK para `Funcionario`).
-   **`hr.EquipeFuncionario` (1:N):** Um funcionário pode fazer parte de múltiplas equipes ao longo do tempo. ([`EquipeFuncionario`](./equipes.md) terá FK para `Funcionario`).
-   **`sst.ASO` (1:N):** Um funcionário realiza múltiplos ASOs. (`ASO` terá FK para `Funcionario`).
-   **`sst.ExameRealizado` (1:N - indiretamente via ASO):** Um funcionário tem múltiplos exames registrados.

---

## 6. Futura Implementação: Gestão de Alterações de Cargo com Período de Testes

Em fases futuras, será necessário implementar um sistema robusto para gerenciar alterações de cargo que incluam períodos de avaliação. Este sistema deverá contemplar:

-   **Aditivo Contratual:** Registrar o início de um período de testes para um novo cargo.
-   **Dados do Aditivo:** Incluir o cargo alvo, o novo salário nominal durante o teste (se aplicável), e a duração do período de avaliação.
-   **Status de Avaliação:** Rastrear o status do funcionário durante o período de testes (em avaliação, aprovado, reprovado).
-   **Ações Pós-Avaliação:** Se aprovado, efetivar a mudança de cargo e salário. Se reprovado, o funcionário retorna ao cargo anterior.
-   **Histórico:** Manter um histórico claro de todas as tentativas e efetivações de mudança de cargo.

Este mecanismo será vital para a mobilidade interna e o desenvolvimento de carreira dos colaboradores, integrando-se diretamente com as entidades `Funcionario`, `Cargo` e o módulo de Auditoria.

---

## 4. Estratégia de Indexação

-   **Índice Único:** no campo `matricula`.
-   **Índices Padrão (B-Tree):** em `(status, data_admissao)`, `(cargo, status)`, `(empresa, status)`. Isso otimiza buscas por funcionários ativos, por cargo ou por empresa.

---

## 5. Camada de Serviço (`FuncionarioService`)

A interação com `Funcionario` será gerenciada por este serviço, encapsulando complexas lógicas de negócio.

-   **`admitir_funcionario(*, pessoa_fisica_data: dict, funcionario_data: dict, documentos_data: list[dict], contatos_data: list[dict], enderecos_data: list[dict]) -> Funcionario:`**:
    -   Recebe dados para `PessoaFisica`, `Funcionario`, `Documento`s, `Contato`s e `Endereco`s.
    -   **1. Gerenciamento de `PessoaFisica`:** Chama `PessoaFisicaService.get_or_create_pessoa_fisica(cpf=pessoa_fisica_data['cpf'], data=pessoa_fisica_data)` para garantir a unicidade do CPF e a criação/reutilização da `PessoaFisica`.
    -   **2. Geração de Matrícula:** Gera a `matricula` automaticamente (ex: Ano + Sequencial 4 dígitos + Dígito de Controle).
    -   **3. Validação e Definição do Salário:**
        -   Se `funcionario_data['salario_nominal']` não for informado, assume o `salario_base` do `Cargo`.
        -   Se for informado, valida que seja igual ou superior ao `salario_base` do `Cargo` (se `salario_base` estiver definido).
    -   **4. Criação de `Funcionario`:** Cria a instância de `Funcionario`, vinculando a `PessoaFisica`, o `Cargo` e o `Projeto` (se informado e válido).-   **5. Gerenciamento de `Enderecos`:** Para cada item em `enderecos_data`, chama `EnderecoService.add_endereco_to_pessoa_fisica` (ou similar para `PessoaJuridica`) para vincular os endereços.
-   **6. Gerenciamento de `Contatos`:** Para cada item em `contatos_data`, chama `ContatoService.add_contato_to_pessoa_fisica` (ou similar) para vincular os contatos, aplicando a lógica de `get_or_create` e `contato_emergencia`.
-   **7. Gerenciamento de `Documentos`:** Para cada item em `documentos_data`, chama `DocumentoService.add_documento_to_pessoa_fisica` (ou similar) para vincular os documentos, incluindo o upload do arquivo.
-   **8. Validação de Documentos Obrigatórios por Cargo:**
    -   Consulta `CargoDocumentoService.get_documentos_obrigatorios_para_cargo(funcionario.cargo)`.
    -   Para cada `CargoDocumento` obrigatório, verifica se existe um `core.Documento` do `documento_tipo` correspondente (e válido, se aplicável) vinculado à `PessoaFisica` do funcionário.
    -   Se um documento obrigatório não for encontrado, a admissão pode ser impedida, marcada como pendente, ou um aviso pode ser gerado (decisão a ser refinada).

-   **`demitir_funcionario(*, funcionario: Funcionario, data_demissao: date, motivo: str) -> Funcionario:`**:
    -   Define `data_demissao` e altera o `status` para `DEMITIDO`.
    -   **Regra:** Desativa quaisquer `hr.Alocacao` ativas para o funcionário.
    -   **Regra:** Se o funcionário tem ASOs pendentes (`status != FINALIZADO`), o serviço pode acionar a criação de um ASO demissional no módulo SST ou emitir um aviso.
-   **`atualizar_dados_contratuais(*, funcionario: Funcionario, data: dict) -> Funcionario:`**:
    -   Permite a atualização de `cargo`, `salario_nominal`, `tipo_contrato`, etc.
    -   **Regra:** Alterações salariais podem exigir um histórico ou aprovação (futuramente).
-   **`vincular_dependente(*, funcionario: Funcionario, dependente_data: dict) -> Dependente:`**:
    -   Chama `PessoaFisicaService` para o dependente.
    -   Cria o `hr.Dependente` e atualiza a flag `tem_dependente` do funcionário.
-   **`alocar_funcionario_em_projeto(*, funcionario: Funcionario, projeto: core.Projeto, data_inicio: date, data_fim: date = None) -> Alocacao:`**:
    -   Cria um novo registro em `hr.Alocacao`.
    -   **Regra:** Um funcionário ativo só pode ter uma alocação ativa por vez (se for o caso, a anterior deve ser finalizada).