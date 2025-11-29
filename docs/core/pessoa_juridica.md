# Core — Pessoa Jurídica

## 1. Visão Geral

A entidade **Pessoa Jurídica** é a base técnica centralizada para qualquer organização ou empresa que interage com o sistema, seja ela interna ou externa.

Assim como a [Pessoa Física](./pessoa_fisica.md), esta entidade **não é gerenciada diretamente pelo usuário final**. Ela serve como o "molde" para entidades de negócio mais específicas, como:

-   [**Empresa**](./empresa.md): Um CNPJ do próprio grupo.
-   [**Cliente**](./cliente.md): Uma empresa externa que contrata os serviços.
-   **Fornecedor:** Uma empresa que fornece produtos ou serviços (módulo de Compras).

Essa abordagem garante que os dados legais de uma empresa sejam armazenados apenas uma vez, mantendo a consistência em todo o ERP.

## 2. Estrutura da Entidade `PessoaJuridica`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `razao_social` | String | Nome legal e completo da empresa. |
| `nome_fantasia`| String | (Opcional) Nome comercial ou de fachada. |
| `cnpj` | String | Cadastro Nacional da Pessoa Jurídica (único, sem máscara). |
| `inscricao_estadual` | String | (Opcional) IE, pode ser isento. |
| `data_abertura` | Date | (Opcional) Data de fundação da empresa. |
| `situacao_cadastral` | String | (Opcional) Status na Receita Federal (ex: "Ativa"). |
| `observacoes` | Text | (Opcional) Campo livre para anotações. |

**Relacionamentos Importantes:**
-   Uma `PessoaJuridica` pode ter múltiplos [Endereços](./enderecos.md), [Contatos](./contatos.md) e [Documentos](./documentos.md).

## 3. Regras de Negócio

1.  **Unicidade do CNPJ:** O CNPJ é o identificador único de uma `PessoaJuridica`. Não podem existir dois registros com o mesmo CNPJ.
2.  **Validação de CNPJ:** O CNPJ informado é validado matematicamente.
3.  **Criação Indireta:** A criação de uma `PessoaJuridica` ocorre quando um módulo de negócio (como o de Clientes) precisa registrar uma nova empresa. Se o CNPJ já existir, o sistema reutiliza o cadastro.
4.  **Soft Delete:** Pessoas Jurídicas seguem a política de exclusão lógica.

## 4. Endpoints da API

Não há endpoints públicos para a gestão direta de `PessoaJuridica`. O fluxo é sempre iniciado por uma entidade de negócio.

### Exemplo: Fluxo de Criação via Cadastro de Cliente

1.  O usuário envia um `POST` para `/api/core/clientes/`.
2.  O `body` contém os dados do cliente, incluindo um objeto `pessoa_juridica` com `razao_social` e `cnpj`.
3.  O `ClienteService` chama internamente o `PessoaJuridicaService`.
4.  O `PessoaJuridicaService` verifica se o CNPJ já existe.
    -   Se sim, retorna a instância existente.
    -   Se não, cria uma nova `PessoaJuridica`.
5.  O `ClienteService` prossegue com a criação do `Cliente`, associando-o à `PessoaJuridica` e à `empresa_gestora` informada.