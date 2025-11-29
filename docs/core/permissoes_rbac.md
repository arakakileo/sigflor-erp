# Core — Permissões (RBAC)

## 1. Visão Geral

O submódulo de **Permissões** implementa o controle de acesso do Sigflor, utilizando o modelo **RBAC (Role-Based Access Control)**. Neste modelo, as permissões não são atribuídas diretamente aos usuários, mas sim a **Papéis** (Roles), que por sua vez são associados aos usuários.

Essa abordagem torna a gestão de acessos mais segura, organizada e escalável.

## 2. Componentes do RBAC

O sistema é composto por três entidades principais:

1.  **Permissão:** A unidade de autorização mais granular. Representa o direito de executar uma ação específica (ex: `visualizar_funcionario`).
2.  **Papel (Role):** Uma coleção de permissões que representa uma função de negócio (ex: "Supervisor de RH", "Gerente de Frota").
3.  **Usuário:** A identidade de quem acessa o sistema. Um usuário recebe suas permissões ao ser associado a um ou mais papéis.

## 3. Estrutura das Entidades

### 3.1. `Permissao`
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `codigo` | String | Código único da permissão (ex: `rh.funcionario.listar`). |
| `nome` | String | Nome amigável (ex: "Listar Funcionários"). |
| `descricao` | Text | Detalhes sobre o que a permissão concede. |

O `codigo` segue o padrão: `<modulo>.<entidade>.<acao>`.

### 3.2. `Papel`
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `nome` | String | Nome único do papel (ex: "Administrador Financeiro"). |
| `descricao` | Text | Responsabilidades do papel. |
| `permissoes` | N:N para `Permissao` | O conjunto de permissões que este papel concede. |

### 3.3. `Usuario`
O modelo de [Usuário](./usuarios.md) possui uma relação N:N com `Papel`.

## 4. Regras de Negócio

1.  **Autorização via Papel:** A verificação de acesso de um usuário é feita com base na união de todas as permissões concedidas por todos os papéis aos quais ele está associado.
2.  **Permissões Diretas:** Em casos excepcionais, uma permissão pode ser atribuída diretamente a um usuário, mas esta não é a prática recomendada.
3.  **Superusuário:** Um usuário com a flag `is_superuser` ignora todas as verificações do RBAC, tendo acesso irrestrito ao sistema.
4.  **Integração com a API:** Cada endpoint da API deve declarar a `permissao` necessária para acessá-lo. Um `permission_class` do DRF intercepta a requisição e realiza a verificação automaticamente.

## 5. Endpoints da API

A gestão de RBAC é uma área administrativa e de alta sensibilidade.

- `GET /api/core/papeis/` - Lista todos os papéis.
- `GET /api/core/papeis/{id}/permissoes/` - Lista as permissões de um papel.
- `POST /api/core/usuarios/{id}/papeis/` - Associa um papel a um usuário.
- `DELETE /api/core/usuarios/{id}/papeis/{papel_id}/` - Desassocia um papel de um usuário.
