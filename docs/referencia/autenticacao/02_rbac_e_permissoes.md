# Controle de Acesso e RBAC

O Sigflor implementa um sistema de **Role-Based Access Control (RBAC)** customizado para gerenciar permissões de forma escalável. Em vez de atribuir permissões diretamente aos usuários, as permissões são agrupadas em **Papéis** (ex: "Gerente de RH", "Assistente de SST"), e os usuários recebem um ou mais papéis.

## 1. Arquitetura de Permissões

### 1.1. Backend Customizado (`RbacBackend`)
O Django nativo verifica permissões apenas na tabela `auth_user_user_permissions`. O Sigflor estende isso através da classe `apps.autenticacao.backends.RbacBackend`.

**Como funciona:**
1.  Intercepta as chamadas de verificação de permissão (`user.has_perm()`).
2.  O Django verifica primeiramente as **permissões diretas** usando o sistema nativo (`user_permissions`).
3.  **Adição:** O `RbacBackend` busca todas as permissões associadas aos **Papéis** que o usuário possui.
4.  O resultado final é a soma das permissões diretas e das permissões dos papéis.

### 1.2. Entidade Papel (`models.Papel`)
Representa uma função ou cargo no sistema.
- **Nome:** Identificador único (ex: "Administrador").
- **Permissões:** Relacionamento Many-to-Many com `auth.Permission`.

---

## 2. Implementação na API (`HasPermission`)

Para proteger rotas na API, utilizamos a classe `apps.comum.permissions.HasPermission`.

**Exemplo de Uso em ViewSet:**
Para simplificar o controle, o sistema fornece a classe base `BaseRBACViewSet` (em `apps.comum.views.base`), que mapeia as ações do DRF (list, create, update, destroy) para códigos de permissão específicos definidos nos atributos da classe.

```python
from apps.comum.views.base import BaseRBACViewSet

class ExemploViewSet(BaseRBACViewSet):
    # Definição das permissões para cada tipo de operação
    permissao_leitura = 'app.view_model'   # GET (list, retrieve)
    permissao_create = 'app.add_model'     # POST (create)
    permissao_update = 'app.change_model'  # PUT/PATCH (update)
    permissao_delete = 'app.delete_model'  # DELETE (destroy)

    # Para Actions customizadas (@action)
    permissoes_acoes = {
        'minha_action_customizada': 'app.change_model',
    }
```

---

## 3. API de Gestão de Papéis (Exemplos)

A gestão de papéis é restrita a administradores.

### 3.1. Listar Papéis
**Endpoint:** `GET /api/auth/papeis/`
**Requisito:** Permissão `autenticacao.view_papel`

**Response (200 OK):**
```json
[
  {
    "id": "uuid-papel-1",
    "nome": "Gerente RH",
    "descricao": "Acesso total ao módulo de RH",
    "permissoes_count": 15
  },
  {
    "id": "uuid-papel-2",
    "nome": "Leitor",
    "descricao": "Acesso somente leitura",
    "permissoes_count": 5
  }
]
```

### 3.2. Criar Papel
**Endpoint:** `POST /api/auth/papeis/`
**Requisito:** Permissão `autenticacao.add_papel`

**Request Body:**
```json
{
  "nome": "Supervisor de Campo",
  "descricao": "Permite gerenciar equipes e apontamentos."
}
```

### 3.3. Adicionar Permissões ao Papel
Adiciona uma lista de permissões a um papel existente.

**Endpoint:** `POST /api/auth/papeis/{id}/adicionar-permissoes/`

**Request Body:**
```json
{
  "permissoes_ids": [
      78, 79, 102
  ]
}
```
*Nota: IDs correspondem à tabela `auth_permission` do Django.*

### 3.4. Ver Usuários do Papel
Lista todos os usuários que possuem este papel.

**Endpoint:** `GET /api/auth/papeis/{id}/usuarios/`

**Response (200 OK):**
```json
[
  {
    "id": "uuid-user-1",
    "nome": "João Silva",
    "email": "joao@sigflor.com"
  }
]
```
