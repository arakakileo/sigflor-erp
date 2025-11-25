# Modulo Core — Contratos

## 1. Visao Geral

O submodulo **Contratos** representa os acordos comerciais formais entre uma **Contratante** e uma **EmpresaCNPJ** do grupo.
E a entidade central para:

- Gestao de relacionamento com clientes
- Controle de vigencia e valores
- Base para criacao de SubContratos
- Rastreabilidade financeira e operacional

Cada contrato vincula um contratante (cliente) a uma empresa do grupo que prestara os servicos.

---

## 2. Objetivo do Submodulo

- Registrar contratos comerciais com clientes
- Controlar vigencia (data inicio/fim)
- Registrar valores contratuais
- Permitir ativacao/desativacao sem perda de historico
- Servir como base para subcontratos

---

## 3. Entidade: Contrato

### 3.1 Estrutura da Tabela

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | UUID | Sim | Identificador unico |
| numero_interno | varchar(50) | Sim (unique) | Numero interno do contrato |
| numero_externo | varchar(50) | Nao (unique) | Numero externo/cliente |
| contratante | FK → Contratante | Sim | Cliente contratante |
| empresa | FK → EmpresaCNPJ | Sim | Empresa do grupo contratada |
| descricao | text | Nao | Descricao do contrato |
| data_inicio | date | Sim | Data de inicio da vigencia |
| data_fim | date | Nao | Data de fim da vigencia |
| ativo | boolean | Sim (default=True) | Status do contrato |
| valor | decimal(15,2) | Nao | Valor do contrato |
| observacoes | text | Nao | Observacoes adicionais |
| created_at | datetime | Sim | Auditoria |
| updated_at | datetime | Sim | Auditoria |
| deleted_at | datetime | Nao | Soft delete |

---

## 4. Relacionamentos

- **N:1 com Contratante**
  Cada contrato pertence a um contratante (cliente).

- **N:1 com EmpresaCNPJ**
  Cada contrato e executado por uma empresa do grupo.

- **1:N com SubContrato**
  Um contrato pode ter varios subcontratos.

---

## 5. Regras de Negocio

1. O numero_interno deve ser unico no sistema.

2. O numero_externo, quando informado, tambem deve ser unico.

3. Um contrato e considerado **vigente** quando:
   - ativo = True
   - data_inicio <= hoje
   - data_fim >= hoje OU data_fim e nulo

4. Exclusao e sempre soft delete.

5. Ao desativar um contrato, subcontratos existentes nao sao afetados.

6. A renovacao atualiza data_fim e opcionalmente o valor.

---

## 6. Propriedades Calculadas

| Propriedade | Descricao |
|-------------|-----------|
| is_vigente | Retorna True se ativo e dentro do periodo |
| contratante_nome | Razao social do contratante |
| empresa_nome | Razao social da empresa |

---

## 7. Endpoints (API)

### Base
`/api/comum/contratos/`

---

### 7.1 Listar

**GET** `/api/comum/contratos/`

Filtros possiveis:
- `search` - busca por numero_interno, numero_externo ou contratante
- `ativo` - true/false
- `vigente` - true/false (calcula baseado em datas)
- `contratante_id` - filtrar por contratante
- `empresa_id` - filtrar por empresa

---

### 7.2 Obter por ID

**GET** `/api/comum/contratos/{id}/`

---

### 7.3 Criar Contrato

**POST** `/api/comum/contratos/`

```json
{
  "numero_interno": "CTR-2024-001",
  "numero_externo": "EXT-123",
  "contratante": "uuid-do-contratante",
  "empresa": "uuid-da-empresa",
  "descricao": "Contrato de servicos florestais",
  "data_inicio": "2024-01-01",
  "data_fim": "2024-12-31",
  "valor": 150000.00
}
```

### 7.4 Editar Contrato

**PATCH** `/api/comum/contratos/{id}/`

### 7.5 Acoes Especiais

| Acao | Metodo | Endpoint | Descricao |
|------|--------|----------|-----------|
| Ativar | POST | `/{id}/ativar/` | Ativa o contrato |
| Desativar | POST | `/{id}/desativar/` | Desativa o contrato |
| Renovar | POST | `/{id}/renovar/` | Renova com nova data_fim e valor |
| Listar vigentes | GET | `/vigentes/` | Lista contratos vigentes |
| Estatisticas | GET | `/estatisticas/` | Retorna estatisticas gerais |
| SubContratos | GET | `/{id}/subcontratos/` | Lista subcontratos do contrato |

**Renovar payload:**
```json
{
  "data_fim": "2025-12-31",
  "valor": 180000.00
}
```

### 7.6 Excluir (Soft Delete)

**DELETE** `/api/comum/contratos/{id}/`

---

## 8. Erros e Excecoes

| Codigo | Mensagem | Motivo |
|--------|----------|--------|
| 400 | Numero interno ja existe | Unicidade violada |
| 400 | Numero externo ja existe | Unicidade violada |
| 400 | Data de fim obrigatoria para renovacao | Renovacao invalida |
| 404 | Contrato nao encontrado | ID inexistente |
| 403 | Sem permissao | Usuario sem acesso |

---

## 9. Observacoes Tecnicas

- A PK e UUID e o soft delete e obrigatorio.
- Constraints de unicidade incluem condicao para numero_externo nulo.
- Service layer deve ser usada para criacao e edicao.
- Indices criados para numero_interno, numero_externo, ativo, data_inicio, contratante e empresa.
