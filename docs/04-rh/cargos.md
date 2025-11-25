# Modulo RH — Cargos

## 1. Visao Geral

O submodulo **Cargos** gerencia a estrutura de cargos da empresa.
E utilizado para:

- Definicao de posicoes/funcoes
- Padronizacao de salarios base
- Classificacao por CBO (Classificacao Brasileira de Ocupacoes)
- Niveis hierarquicos
- Vinculacao com funcionarios

---

## 2. Objetivo do Submodulo

- Cadastrar cargos da empresa
- Definir salarios base por cargo
- Registrar codigo CBO
- Classificar por nivel hierarquico
- Permitir ativacao/desativacao de cargos

---

## 3. Entidade: Cargo

### 3.1 Estrutura da Tabela

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | UUID | Sim | Identificador unico |
| nome | varchar(100) | Sim (unique) | Nome do cargo |
| salario | decimal(10,2) | Nao | Salario base do cargo |
| cbo | varchar(20) | Nao | Codigo CBO |
| descricao | text | Nao | Descricao das atribuicoes |
| nivel | varchar(20) | Nao | Nivel hierarquico |
| ativo | boolean | Sim (default=True) | Status do cargo |
| created_at | datetime | Sim | Auditoria |
| updated_at | datetime | Sim | Auditoria |
| deleted_at | datetime | Nao | Soft delete |

### 3.2 Niveis Disponiveis

| Nivel | Descricao |
|-------|-----------|
| operacional | Nivel operacional |
| tecnico | Nivel tecnico |
| supervisao | Nivel de supervisao |
| coordenacao | Nivel de coordenacao |
| gerencia | Nivel gerencial |
| diretoria | Nivel de diretoria |

---

## 4. Relacionamentos

- **1:N com Funcionario**
  Um cargo pode ter varios funcionarios.

---

## 5. Regras de Negocio

1. O nome do cargo deve ser unico no sistema.

2. O CBO e opcional mas recomendado para fins trabalhistas.

3. O cargo pode estar ativo ou inativo:
   - ativo = disponivel para novas contratacoes
   - inativo = preservado para historico

4. Exclusao e sempre soft delete.

5. Ao desativar um cargo, funcionarios existentes nao sao afetados.

---

## 6. Propriedades Calculadas

| Propriedade | Descricao |
|-------------|-----------|
| funcionarios_count | Quantidade de funcionarios no cargo |

---

## 7. Endpoints (API)

### Base
`/api/rh/cargos/`

---

### 7.1 Listar

**GET** `/api/rh/cargos/`

Filtros possiveis:
- `search` - busca por nome, CBO ou descricao
- `ativo` - true/false
- `cbo` - filtrar por CBO

---

### 7.2 Obter por ID

**GET** `/api/rh/cargos/{id}/`

---

### 7.3 Criar Cargo

**POST** `/api/rh/cargos/`

```json
{
  "nome": "Analista de Sistemas",
  "salario": 5500.00,
  "cbo": "2124-05",
  "descricao": "Responsavel pelo desenvolvimento e manutencao de sistemas",
  "nivel": "tecnico"
}
```

### 7.4 Editar Cargo

**PATCH** `/api/rh/cargos/{id}/`

### 7.5 Acoes Especiais

| Acao | Metodo | Endpoint | Descricao |
|------|--------|----------|-----------|
| Ativar | POST | `/{id}/ativar/` | Ativa o cargo |
| Desativar | POST | `/{id}/desativar/` | Desativa o cargo |
| Listar ativos | GET | `/ativos/` | Lista apenas cargos ativos |
| Funcionarios | GET | `/{id}/funcionarios/` | Lista funcionarios do cargo |
| Estatisticas | GET | `/estatisticas/` | Retorna estatisticas gerais |

### 7.6 Excluir (Soft Delete)

**DELETE** `/api/rh/cargos/{id}/`

---

## 8. Estatisticas Disponiveis

O endpoint `/estatisticas/` retorna:

```json
{
  "total_cargos": 25,
  "cargos_ativos": 22,
  "funcionarios_por_cargo": [
    {"cargo__nome": "Operador Florestal", "total": 45},
    {"cargo__nome": "Motorista", "total": 20},
    {"cargo__nome": "Mecanico", "total": 8}
  ]
}
```

---

## 9. Erros e Excecoes

| Codigo | Mensagem | Motivo |
|--------|----------|--------|
| 400 | Nome do cargo ja existe | Unicidade violada |
| 404 | Cargo nao encontrado | ID inexistente |
| 403 | Sem permissao | Usuario sem acesso |

---

## 10. Observacoes Tecnicas

- A PK e UUID e o soft delete e obrigatorio.
- Service layer deve ser usada para criacao e edicao.
- Indices criados para nome, cbo e ativo.
- O cargo utiliza on_delete=PROTECT no relacionamento com Funcionario.
