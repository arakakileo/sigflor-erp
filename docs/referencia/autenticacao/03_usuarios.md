# Gestão de Usuários e Acesso Regional

A gestão de usuários no Sigflor centraliza credenciais, atribuição de papéis e controle de acesso geográfico (Regionais/Filiais).

## 1. Modelo de Dados (`Usuario`)

O modelo `Usuario` estende `AbstractUser` do Django, adicionando campos de auditoria e controle.

### 1.1. Diferenças Importantes
Diferente da maioria das entidades do sistema, o **`Usuario` NÃO herda de `SoftDeleteModel`**.
*   **Motivo:** Evitar dependência circular, já que `SoftDeleteModel` depende de `Usuario` para registrar quem deletou o registro.
*   **Implementação:** Os campos `deleted_at`, `deleted_by`, `created_by` e `updated_by` são reimplementados manualmente no modelo.

### 1.2. Controle de Acesso Regional (`allowed_filiais`)
Para suportar operações em múltiplas filiais, o usuário possui um campo Many-to-Many chamado `allowed_filiais`.
*   **Contexto:** Um usuário (ex: Gerente Regional) pode ter acesso a dados de apenas um subconjunto de filiais.
*   **Validação:** A camada de **Services** deve verificar explicitamente se a entidade alvo pertence a uma filial contida em `user.allowed_filiais`.

---

## 2. API de Gestão de Usuários (Exemplos)

### 2.1. Listar Usuários
Permite filtros por status, termo de busca e papel.

**Endpoint:** `GET /api/auth/usuarios/?search=joao&ativo=true`

**Response (200 OK):**
```json
[
  {
    "id": "uuid-user-1",
    "username": "joao.silva",
    "email": "joao@sigflor.com",
    "nome": "João",
    "sobrenome": "Silva",
    "ativo": true,
    "lista_papeis": ["Gerente RH"],
    "lista_filiais": ["Matriz", "Filial Sul"],
    "ultimo_login": "2024-03-20T10:30:00Z"
  }
]
```

### 2.2. Criar Usuário
Cria um usuário e define seus papéis e filiais permitidas.

**Endpoint:** `POST /api/auth/usuarios/`
**Requisito:** Permissão `autenticacao.add_usuario`

**Request Body:**
```json
{
  "nome": "Maria",
  "sobrenome": "Souza",
  "email": "maria@sigflor.com",
  "username": "maria.souza",
  "senha": "SenhaInicial123!",
  "lista_papeis_ids": ["uuid-papel-rh"],
  "lista_filiais_ids": [1, 2],
  "ativo": true
}
```

### 2.3. Redefinir Senha (Admin)
Rota para administradores forçarem a troca de senha de um usuário.

**Endpoint:** `POST /api/auth/usuarios/{id}/redefinir-senha/`
**Requisito:** Permissão `autenticacao.change_usuario`

**Request Body:**
```json
{
  "nova_senha": "NovaSenhaSegura2024"
}
```

### 2.4. Alterar Própria Senha
Qualquer usuário autenticado pode alterar sua senha.

**Endpoint:** `POST /api/auth/usuarios/alterar-minha-senha/`

**Request Body:**
```json
{
  "senha_atual": "SenhaAntiga123",
  "nova_senha": "NovaSenha123",
  "confirmacao_senha": "NovaSenha123"
}
```
