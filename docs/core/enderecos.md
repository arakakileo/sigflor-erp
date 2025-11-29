# Core — Endereços (Especificação Detalhada)

## 1. Visão Geral

A entidade **Endereço** é um repositório centralizado para informações de localização. Ela é uma entidade genérica, projetada para ser reutilizada por qualquer outro modelo do sistema (como `PessoaFisica` ou `PessoaJuridica`) através de tabelas de vínculo.

**Propósito Arquitetural:** Garantir um formato padronizado para endereços, centralizar a lógica de validação e normalização, e evitar a repetição de campos de endereço em múltiplas tabelas.

---

## 2. Estrutura do Modelo (`core.Endereco`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **logradouro** | `models.CharField` | `VARCHAR(255)` | `null=False`, `blank=False`. |
| **numero** | `models.CharField` | `VARCHAR(20)` | `null=True`, `blank=True`. |
| **complemento** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. |
| **bairro** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. |
| **cidade** | `models.CharField` | `VARCHAR(100)` | `null=False`, `blank=False`. |
| **estado** | `models.CharField` | `VARCHAR(2)` | `choices=Endereco.UF.choices` (Enum com UFs do Brasil). `null=False`, `blank=False`. |
| **cep** | `models.CharField` | `VARCHAR(8)` | `null=False`, `blank=False`. **Regra:** Armazenado sem máscara, apenas dígitos. |
| **pais** | `models.CharField` | `VARCHAR(50)` | `default='Brasil'`. |

---

## 3. Relacionamentos (Modelo de Composição)

A associação é feita por tabelas de vínculo explícitas.

### Tabela de Vínculo Exemplo: `PessoaFisicaEndereco`
| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **pessoa_fisica** | `models.ForeignKey` para `PessoaFisica` | `on_delete=models.CASCADE`. |
| **endereco** | `models.ForeignKey` para `Endereco` | `on_delete=models.CASCADE`. |
| **tipo** | `models.CharField` | `choices=['RESIDENCIAL', 'COMERCIAL']`. **Regra:** Contextualiza o endereço. |
| **principal** | `models.BooleanField` | `default=False`. **Constraint:** `UniqueConstraint` para `(pessoa_fisica, tipo)` onde `principal=True`. |

**Nota:** Esta estrutura se repetiria para `PessoaJuridicaEndereco`, `FilialEndereco`, etc. O campo `principal` e `tipo` vivem na tabela de associação, pois eles descrevem a *relação* entre a pessoa e o endereço, não o endereço em si.

---

## 4. Estratégia de Indexação

-   **Índice Padrão (B-Tree):** no campo `cep` para buscas rápidas por CEP.
-   **Índice Composto:** em `(cidade, estado)` para otimizar a busca de endereços por localidade.

---

## 5. Camada de Serviço (`EnderecoService`)

A interação deve ser feita via `EnderecoService`, que trabalhará em conjunto com os serviços das entidades principais (ex: `PessoaFisicaService`).

-   **`add_endereco_to_pessoa_fisica(*, pessoa_fisica: PessoaFisica, data: dict)`**:
    -   Recebe a instância da pessoa e um dicionário com os dados do endereço (`logradouro`, `cep`, etc.), o `tipo` e a flag `principal`.
    -   Normaliza e valida os dados do endereço (ex: remove máscara do CEP).
    -   Cria a instância de `Endereco`.
    -   Cria a instância de `PessoaFisicaEndereco`, estabelecendo o vínculo.
    -   **Lógica de Negócio:** Se `principal=True`, o serviço deve garantir que qualquer outro endereço do mesmo `tipo` para aquela `pessoa_fisica` seja marcado como `principal=False` (atomicamente, dentro de uma transação).