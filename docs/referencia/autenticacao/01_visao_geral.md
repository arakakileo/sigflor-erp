# Autenticação e Autorização (Visão Geral)

O módulo de autenticação centraliza a segurança do Sigflor, gerindo usuários, sessões via JWT e o controle de acesso (RBAC).

## 1. Estratégia de Autenticação (JWT)

O sistema utiliza **JSON Web Tokens (JWT)** para autenticação stateless.
Pacote utilizado: `djangorestframework-simplejwt`.

### Ciclo de Vida
1.  **Obtenção do Par de Tokens:** O cliente envia credenciais e recebe um `access` token (curta duração) e um `refresh` token (longa duração).
2.  **Uso do Token:** O `access` token deve ser enviado no cabeçalho `Authorization: Bearer <token>` em todas as requisições protegidas.
3.  **Renovação (Refresh):** Quando o `access` expira, o cliente usa o `refresh` endpoint para obter um novo `access` sem reenviar a senha.
4.  **Logout (Blacklist):** Para efetuar logout, o token de `refresh` é enviado para uma lista negra (blacklist), invalidando-o imediatamente.

---
## 2. API e Exemplos de Uso

### 2.1. Login (Obter Tokens)
**Endpoint:** `POST /api/auth/login/` (ou `/api/token/`)

**Requisito:** `AllowAny`

**Request Headers:** `Content-Type: application/json`

**Request Body:**
```json
{
  "email": "admin@sigflor.com",
  "password": "senha_segura"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "usuario": {
      "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
      "nome": "Administrador",
      "email": "admin@sigflor.com"
  }
}
```

---

### 2.2. Refresh Token (Renovar Sessão)
**Endpoint:** `POST /api/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 2.3. Logout (Invalidar Sessão)
O logout invalida o `refresh` token, impedindo que ele seja usado para gerar novos tokens de acesso.

**Endpoint:** `POST /api/auth/logout/`

**Requisito:** `IsAuthenticated` (Header Authorization obrigatório)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (205 Reset Content):**
```json
"Usuário deslogado com sucesso."
```

---

### 2.4. Exemplo de Requisição Autenticada
Para acessar qualquer rota protegida:

**Headers:**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```
