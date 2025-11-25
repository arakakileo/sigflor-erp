# Modulo Core — Filiais

## 1. Visao Geral

O submodulo **Filiais** representa as unidades operacionais da empresa.
Cada filial pode estar vinculada a uma empresa do grupo (EmpresaCNPJ) e serve como ponto de referencia para:

- SubContratos
- Alocacao de funcionarios
- Custos operacionais
- Patrimonios
- Enderecos e contatos operacionais

A Filial e uma entidade organizacional que permite segmentar operacoes geograficamente ou funcionalmente.

---

## 2. Objetivo do Submodulo

- Registrar unidades operacionais da empresa
- Vincular filiais a empresas do grupo
- Centralizar enderecos e contatos por unidade
- Permitir gestao de status (ativa/inativa/suspensa)
- Servir como base para subcontratos e alocacoes

---

## 3. Entidade: Filial

### 3.1 Estrutura da Tabela

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | UUID | Sim | Identificador unico |
| nome | varchar(200) | Sim | Nome da filial |
| codigo_interno | varchar(50) | Sim (unique) | Codigo interno da filial |
| status | varchar(20) | Sim | Status: ativa, inativa, suspensa |
| descricao | text | Nao | Descricao complementar |
| empresa | FK → EmpresaCNPJ | Nao | Empresa do grupo a qual pertence |
| enderecos | GenericRelation | Nao | Enderecos associados |
| contatos | GenericRelation | Nao | Contatos associados |
| created_at | datetime | Sim | Auditoria |
| updated_at | datetime | Sim | Auditoria |
| deleted_at | datetime | Nao | Soft delete |

### 3.2 Status Disponiveis

| Status | Descricao |
|--------|-----------|
| ativa | Filial em operacao normal |
| inativa | Filial desativada |
| suspensa | Filial temporariamente suspensa |

---

## 4. Relacionamentos

- **N:1 com EmpresaCNPJ**
  Cada Filial pode pertencer a uma empresa do grupo (opcional).

- **1:N com SubContrato**
  Uma filial pode ter varios subcontratos.

- **GenericRelation para Enderecos e Contatos**
  Permite multiplos enderecos e contatos por filial.

---

## 5. Regras de Negocio

1. O codigo_interno deve ser unico no sistema.

2. Uma filial pode existir sem empresa vinculada (para casos genericos).

3. O status controla a visibilidade e operacionalidade:
   - ativa = disponivel para novas alocacoes
   - inativa = preservada para historico
   - suspensa = temporariamente indisponivel

4. Exclusao e sempre soft delete.

5. Ao desativar uma filial, subcontratos existentes nao sao afetados.

---

## 6. Propriedades Calculadas

| Propriedade | Descricao |
|-------------|-----------|
| is_ativa | Retorna True se status='ativa' e nao deletada |
| empresa_nome | Nome da empresa vinculada |
| endereco_principal | Endereco marcado como principal |
| contato_principal | Contato marcado como principal |

---

## 7. Endpoints (API)

### Base
`/api/comum/filiais/`

---

### 7.1 Listar

**GET** `/api/comum/filiais/`

Filtros possiveis:
- `search` - busca por nome ou codigo_interno
- `status` - filtrar por status
- `empresa_id` - filtrar por empresa

---

### 7.2 Obter por ID

**GET** `/api/comum/filiais/{id}/`

---

### 7.3 Criar Filial

**POST** `/api/comum/filiais/`

```json
{
  "nome": "Filial Norte",
  "codigo_interno": "FN001",
  "status": "ativa",
  "descricao": "Unidade operacional regiao norte",
  "empresa": "uuid-da-empresa"
}
```

### 7.4 Editar Filial

**PATCH** `/api/comum/filiais/{id}/`

### 7.5 Acoes Especiais

| Acao | Metodo | Endpoint | Descricao |
|------|--------|----------|-----------|
| Ativar | POST | `/{id}/ativar/` | Altera status para ativa |
| Desativar | POST | `/{id}/desativar/` | Altera status para inativa |
| Suspender | POST | `/{id}/suspender/` | Altera status para suspensa |
| Listar ativas | GET | `/ativas/` | Lista apenas filiais ativas |
| Estatisticas | GET | `/estatisticas/` | Retorna estatisticas gerais |
| SubContratos | GET | `/{id}/subcontratos/` | Lista subcontratos da filial |

### 7.6 Excluir (Soft Delete)

**DELETE** `/api/comum/filiais/{id}/`

---

## 8. Erros e Excecoes

| Codigo | Mensagem | Motivo |
|--------|----------|--------|
| 400 | Codigo interno ja existe | Unicidade violada |
| 404 | Filial nao encontrada | ID inexistente |
| 403 | Sem permissao | Usuario sem acesso |

---

## 9. Observacoes Tecnicas

- A PK e UUID e o soft delete e obrigatorio.
- GenericRelation permite enderecos e contatos flexiveis.
- Service layer deve ser usada para criacao e edicao.
- Indices criados para codigo_interno, status e nome.
