# Core — Usuários

## 1. Visão Geral

O submódulo de **Usuários** gerencia as identidades digitais que acessam o sistema Sigflor. Um `Usuário` representa uma conta de login, com credenciais de acesso e um conjunto de permissões.

É importante distinguir um `Usuário` de uma [Pessoa Física](./pessoa_fisica.md):
-   **Pessoa Física:** Representa o indivíduo no mundo real, com seus dados civis (CPF, RG, etc.).
-   **Usuário:** Representa a conta de acesso ao sistema (`username`, senha, etc.).

No Sigflor, um `Usuário` pode (e deve, na maioria dos casos) estar vinculado a uma `PessoaFisica` para garantir uma auditoria mais robusta e a integração com outros módulos, como o de RH.

## 2. Estrutura da Entidade `Usuario`

O sistema utiliza o modelo de usuário customizado do Django, estendendo o `AbstractUser`.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `username` | String | Nome de login único. |
| `email` | String | E-mail único, usado para notificações e recuperação de senha. |
| `first_name` | String | Primeiro nome do usuário. |
| `last_name` | String | Sobrenome do usuário. |
| `password` | String | Senha criptografada (hash). |
| `pessoa_fisica`| FK (1:1) para `PessoaFisica` | (Opcional, mas recomendado) O vínculo com o registro civil do usuário. |
| `is_active` | Boolean | Controla se o usuário pode fazer login. |
| `is_staff` | Boolean | Concede acesso à interface de administração do Django. |
| `is_superuser`| Boolean | Concede todas as permissões, ignorando o RBAC. |
| `papeis` | N:N para `Papel` | Os [Papéis](./permissoes_rbac.md) que definem as permissões do usuário. |

## 3. Autenticação e Autorização

-   **Autenticação:** O login é realizado via **JWT (JSON Web Token)**. O usuário envia `username` e `password` para um endpoint de login e recebe em troca um `access_token` (de curta duração) e um `refresh_token` (de longa duração).
-   **Autorização:** A autorização para acessar cada recurso da API é controlada pelo sistema de [Permissões (RBAC)](./permissoes_rbac.md).

## 4. Regras de Negócio

1.  **Unicidade:** `username` e `email` devem ser únicos em todo o sistema.
2.  **Segurança da Senha:** As senhas nunca são armazenadas em texto plano, apenas seu hash.
3.  **Desativação:** Um usuário com `is_active = False` não pode se autenticar no sistema.
4.  **Soft Delete:** Usuários seguem a política de exclusão lógica.

## 5. Endpoints da API

### Autenticação
-   `POST /api/auth/token/`: Realiza o login e obtém os tokens JWT.
-   `POST /api/auth/token/refresh/`: Obtém um novo `access_token` usando o `refresh_token`.

### Gestão de Usuários (Administrativo)
-   `GET /api/core/usuarios/`: Lista todos os usuários.
-   `POST /api/core/usuarios/`: Cria um novo usuário.
-   `PATCH /api/core/usuarios/{id}/`: Atualiza um usuário.
-   `DELETE /api/core/usuarios/{id}/`: Desativa (Soft Delete) um usuário.
-   `POST /api/core/usuarios/{id}/definir-senha/`: Define uma nova senha para o usuário.
