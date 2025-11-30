# Core — Pessoa Jurídica

## 1. Visão Geral

A entidade **Pessoa Jurídica** é a base técnica centralizada para qualquer organização ou empresa que interage com o sistema, seja ela interna ou externa.

Assim como a [Pessoa Física](./pessoa_fisica.md), esta entidade **não é gerenciada diretamente pelo usuário final**. Ela serve como o "molde" para entidades de negócio mais específicas, como:

-   [**Empresa**](./empresa.md): Um CNPJ do próprio grupo.
-   [**Cliente**](./cliente.md): Uma empresa externa que contrata os serviços.
-   **Fornecedor:** Uma empresa que fornece produtos ou serviços (módulo de Compras).

Essa abordagem garante que os dados legais de uma empresa sejam armazenados apenas uma vez, mantendo a consistência em todo o ERP.

**Status:** ✅ IMPLEMENTADO

## 2. Estrutura da Entidade `PessoaJuridica`

| Campo | Tipo Django | Tipo PostgreSQL | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| `razao_social` | `models.CharField` | `VARCHAR(200)` | Nome legal e completo da empresa. `null=False`, `blank=False`. |
| `nome_fantasia`| `models.CharField` | `VARCHAR(200)` | (Opcional) Nome comercial ou de fachada. |
| `cnpj` | `models.CharField` | `VARCHAR(14)` | Cadastro Nacional da Pessoa Jurídica. `unique=True`. **Regra:** Armazenado sem máscara, apenas dígitos. |
| `inscricao_estadual` | `models.CharField` | `VARCHAR(20)` | (Opcional) IE, pode ser isento. |
| `data_abertura` | `models.DateField` | `DATE` | (Opcional) Data de fundação da empresa. |
| `situacao_cadastral` | `models.CharField` | `VARCHAR(20)` | (Opcional) Status na Receita Federal. `choices=SituacaoCadastral.choices`. |
| `observacoes` | `models.TextField` | `TEXT` | (Opcional) Campo livre para anotações. |

### Campos Herdados (SoftDeleteModel)
- `created_at`, `updated_at`, `deleted_at`
- `created_by`, `updated_by`

### Enum `SituacaoCadastral`
```python
class SituacaoCadastral(models.TextChoices):
    ATIVA = 'ATIVA', 'Ativa'
    SUSPENSA = 'SUSPENSA', 'Suspensa'
    INAPTA = 'INAPTA', 'Inapta'
    BAIXADA = 'BAIXADA', 'Baixada'
    NULA = 'NULA', 'Nula'
```

## 3. Relacionamentos (Modelo de Composição)

Uma `PessoaJuridica` se relaciona com outras entidades através de **tabelas de vínculo explícitas** (sem uso de Generic Foreign Keys):

| Tabela de Vínculo | Entidade Relacionada | Campos Adicionais |
| :--- | :--- | :--- |
| `PessoaJuridicaEndereco` | [Endereço](./enderecos.md) | `tipo` (COMERCIAL/CORRESPONDENCIA), `principal` |
| `PessoaJuridicaContato` | [Contato](./contatos.md) | `principal` |
| `PessoaJuridicaDocumento` | [Documento](./documentos.md) | `principal` |

Consulte a documentação de cada entidade para detalhes sobre os campos e constraints das tabelas de vínculo.

## 4. Regras de Negócio

1.  **Unicidade do CNPJ:** O CNPJ é o identificador único de uma `PessoaJuridica`. Não podem existir dois registros com o mesmo CNPJ.
2.  **Validação de CNPJ:** O CNPJ informado é validado matematicamente.
3.  **Criação Indireta:** A criação de uma `PessoaJuridica` ocorre quando um módulo de negócio (como o de Clientes) precisa registrar uma nova empresa. Se o CNPJ já existir, o sistema reutiliza o cadastro.
4.  **Soft Delete:** Pessoas Jurídicas seguem a política de exclusão lógica.

## 5. Endpoints da API

Não há endpoints públicos para a gestão direta de `PessoaJuridica`. O fluxo é sempre iniciado por uma entidade de negócio.

### Exemplo: Fluxo de Criação via Cadastro de Cliente

1.  O usuário envia um `POST` para `/api/comum/clientes/`.
2.  O `body` contém os dados do cliente, incluindo um objeto `pessoa_juridica` com `razao_social` e `cnpj`.
3.  O `ClienteService` chama internamente o `PessoaJuridicaService`.
4.  O `PessoaJuridicaService` verifica se o CNPJ já existe.
    -   Se sim, retorna a instância existente.
    -   Se não, cria uma nova `PessoaJuridica`.
5.  O `ClienteService` prossegue com a criação do `Cliente`, associando-o à `PessoaJuridica` e à `empresa_gestora` informada.

---

## 6. Camada de Serviço (`PessoaJuridicaService`)

### Métodos de Criação

- **`get_or_create(*, cnpj, razao_social, created_by, **kwargs)`**:
  - Verifica se já existe uma `PessoaJuridica` com o CNPJ informado.
  - Se sim, retorna a instância existente.
  - Se não, cria uma nova instância.
  - Retorna uma tupla `(instância, criado)`.

### Métodos de Atualização

- **`update(pessoa_juridica, updated_by, **kwargs)`**:
  - Atualiza os campos da pessoa jurídica.
  - Não permite alteração do CNPJ.

### Métodos de Exclusão

- **`delete(pessoa_juridica, user)`**: Soft delete da pessoa jurídica e todos os seus vínculos.

### Métodos de Consulta

- **`get_by_cnpj(cnpj)`**: Retorna a pessoa jurídica pelo CNPJ.
- **`get_by_id(id)`**: Retorna a pessoa jurídica pelo ID.
- **`list_all()`**: Lista todas as pessoas jurídicas ativas.