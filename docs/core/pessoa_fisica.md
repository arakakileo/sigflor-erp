# Core — Pessoa Física (Especificação Detalhada)

## 1. Visão Geral

A entidade **Pessoa Física** é a fonte canônica de verdade para dados de indivíduos. Ela armazena informações civis de forma centralizada e desacoplada de qualquer contexto de negócio (como funcionário, dependente, etc.). Sua chave primária (`id`) será a referência para qualquer outro módulo que precise se associar a um indivíduo.

**Propósito Arquitetural:** Evitar a duplicação de dados pessoais e garantir a consistência em todo o ecossistema do ERP.

---

## 2. Estrutura do Modelo (`comum.PessoaFisica`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **nome_completo** | `models.CharField` | `VARCHAR(200)` | `null=False`, `blank=False`. Nome civil completo. |
| **cpf** | `models.CharField` | `VARCHAR(11)` | `unique=True`. **Regra:** Armazenado sem máscara, apenas dígitos. Validado matematicamente. |
| **rg** | `models.CharField` | `VARCHAR(20)` | `null=True`, `blank=True`. Registro Geral. |
| **orgao_emissor** | `models.CharField` | `VARCHAR(20)` | `null=True`, `blank=True`. Órgão emissor do RG. |
| **data_nascimento** | `models.DateField` | `DATE` | `null=True`, `blank=True`. |
| **sexo** | `models.CharField` | `VARCHAR(1)` | `choices=[M, F, O]`. `null=True`, `blank=True`. |
| **estado_civil** | `models.CharField` | `VARCHAR(20)` | `choices=[Solteiro, Casado, etc.]`. `null=True`, `blank=True`. |
| **nacionalidade** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`, `default='Brasileira'`. |
| **naturalidade** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. |
| **possui_deficiencia** | `models.BooleanField`| `BOOLEAN` | `default=False`. **Regra:** Gerenciado automaticamente. `True` se houver alguma `Deficiencia` associada. |
| **observacoes** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. |
| *created_at* | `models.DateTimeField`| `TIMESTAMP` | `auto_now_add=True`. Herdado do `SoftDeleteModel`. |
| *updated_at* | `models.DateTimeField`| `TIMESTAMP` | `auto_now=True`. Herdado do `SoftDeleteModel`. |
| *deleted_at* | `models.DateTimeField`| `TIMESTAMP` | `null=True`, `default=None`. Herdado do `SoftDeleteModel`. |

---

## 3. Regras de Negócio

1.  **Unicidade do CPF:** O CPF é o identificador único de uma `PessoaFisica`. Não podem existir dois registros com o mesmo CPF ativo (`deleted_at` is null).
2.  **Validação de CPF:** O CPF informado é validado matematicamente e normalizado (apenas dígitos) antes de ser salvo.
3.  **Criação Indireta:** A criação de uma `PessoaFisica` ocorre quando um módulo de negócio (como `rh.Funcionario` ou `comum.Usuario`) precisa registrar um novo indivíduo. Se o CPF já existir, o sistema reutiliza o cadastro existente, atualizando os dados recebidos.
4.  **Gerenciamento de `possui_deficiencia`:** O campo `possui_deficiencia` é gerenciado automaticamente pela camada de serviço/modelo `Deficiencia`. Ele é `True` se houver pelo menos uma `Deficiencia` ativa vinculada à `PessoaFisica`.
5.  **Soft Delete:** Pessoas Físicas seguem a política de exclusão lógica.

---

## 4. Relacionamentos

As associações são feitas via tabelas de vínculo explícitas, exceto onde a `GenericRelation` é justificada (Anexos) ou há uma ForeignKey direta.

| Relacionamento com | Tipo de Relacionamento | Tabela de Vínculo | Cardinalidade | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **Usuario** | `OneToOneField` (reverso) | N/A | 1:1 | Vínculo com a conta de usuário do sistema (`comum.Usuario`). |
| **Endereco** | `ManyToManyField` | `PessoaFisicaEndereco` | 1:N | Uma pessoa pode ter múltiplos endereços, com um principal. |
| **Contato** | `ManyToManyField` | `PessoaFisicaContato` | 1:N | Uma pessoa pode ter múltiplos contatos (telefone, e-mail), com um principal. |
| **Documento** | `GenericRelation` | N/A | 1:N | Uma pessoa pode ter múltiplos documentos formais. (Exceção à regra de GFKs) |
| **Anexo** | `GenericRelation` | N/A | 1:N | Uma pessoa pode ter múltiplos anexos complementares. (Exceção à regra de GFKs) |
| **Deficiencia** | `ForeignKey` (reverso) | `Deficiencia` | 1:N | Vínculo direto de Deficiência para Pessoa Física. |

---

## 5. Estratégia de Indexação

Para otimizar as consultas, os seguintes índices devem ser criados no banco de dados:

-   **Índice Único:** no campo `cpf` (já garantido pelo `unique=True`).
-   **Índice Padrão (B-Tree):** no campo `nome_completo` para acelerar buscas por nome.
-   **Índice Composto:** em `(deleted_at, nome_completo)` para otimizar listagens de registros ativos ordenados por nome.

---

## 6. Camada de Serviço (`PessoaFisicaService`)

A interação com este modelo **deve** ser feita exclusivamente através do `PessoaFisicaService`. Suas responsabilidades incluem:

-   **`get_or_create_pessoa_fisica(*, cpf: str, data: dict) -> PessoaFisica:`**: O método principal.
    -   Recebe os dados de uma pessoa, com o CPF sendo o identificador principal.
    -   Normaliza e valida o CPF.
    -   Busca no banco de dados por uma `PessoaFisica` com o CPF fornecido.
    -   Se encontrar, atualiza os dados com as informações recebidas (se houver).
    -   Se não encontrar, cria uma nova instância.
    -   Retorna a instância da `PessoaFisica`.
-   Encapsular toda a lógica de validação, normalização e tratamento de exceções (ex: `CPFInvalidoError`, `ValidationError`).
-   Garantir que as regras de negócio, como a atualização do flag `possui_deficiencia`, sejam executadas atomicamente.

---

## 7. Endpoints da API

Não há endpoints públicos para a gestão direta de `PessoaFisica`. O fluxo é sempre iniciado por uma entidade de negócio que a utiliza como base (e.g., `rh.Funcionario`, `comum.Usuario`).

### Exemplo: Fluxo de Criação via Cadastro de Funcionário

1.  O usuário envia um `POST` para `/api/rh/funcionarios/`.
2.  O `body` contém os dados do funcionário, incluindo um objeto `pessoa_fisica` com `nome_completo`, `cpf`, `data_nascimento`, etc.
3.  O `FuncionarioService` chama internamente o `PessoaFisicaService`.
4.  O `PessoaFisicaService` verifica se o CPF já existe.
    -   Se sim, retorna a instância existente.
    -   Se não, cria uma nova `PessoaFisica`.
5.  O `FuncionarioService` prossegue com a criação do `Funcionario`, associando-o à `PessoaFisica` gerada/existente.

---
