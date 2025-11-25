# Modulo RH — Funcionarios

## 1. Visao Geral

O submodulo **Funcionarios** e o cadastro central de colaboradores da empresa.
Gerencia:

- Dados pessoais (via PessoaFisica)
- Dados contratuais
- Jornada de trabalho
- Alocacao (via SubContrato)
- Informacoes bancarias
- Documentacao trabalhista
- Vestimenta/uniformes
- Dependentes

---

## 2. Objetivo do Submodulo

- Centralizar informacoes de colaboradores
- Controlar admissoes e demissoes
- Gerenciar alocacoes por subcontrato
- Registrar dados trabalhistas completos
- Controlar uniformes e EPIs

---

## 3. Entidade: Funcionario

### 3.1 Estrutura da Tabela

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | UUID | Sim | Identificador unico |
| pessoa_fisica | FK → PessoaFisica | Sim | Dados pessoais |
| matricula | varchar(20) | Sim (unique) | Matricula auto-gerada |
| cargo | FK → Cargo | Sim | Cargo do funcionario |
| departamento | varchar(100) | Nao | Departamento/setor |
| subcontrato | FK → SubContrato | Nao | Alocacao de custos |
| tipo_contrato | varchar(20) | Sim | Tipo de contrato |
| data_admissao | date | Sim | Data de admissao |
| data_demissao | date | Nao | Data de demissao |
| salario | decimal(10,2) | Nao | Salario atual |
| carga_horaria_semanal | integer | Sim (default=44) | Carga horaria semanal |
| turno | varchar(20) | Sim | Turno de trabalho |
| horario_entrada | time | Nao | Horario de entrada |
| horario_saida | time | Nao | Horario de saida |
| status | varchar(20) | Sim | Status do funcionario |
| tem_dependente | boolean | Sim (default=False) | Possui dependentes |
| tamanho_camisa | varchar(10) | Nao | Tamanho da camisa |
| tamanho_calca | varchar(10) | Nao | Tamanho da calca |
| tamanho_botina | varchar(10) | Nao | Tamanho do calcado |
| banco | varchar(100) | Nao | Banco |
| agencia | varchar(20) | Nao | Agencia |
| conta | varchar(30) | Nao | Conta |
| tipo_conta | varchar(20) | Nao | Tipo de conta |
| pix | varchar(100) | Nao | Chave PIX |
| ctps_numero | varchar(20) | Nao | Numero CTPS |
| ctps_serie | varchar(10) | Nao | Serie CTPS |
| ctps_uf | varchar(2) | Nao | UF da CTPS |
| pis | varchar(20) | Nao | Numero PIS/PASEP |
| empresa | FK → EmpresaCNPJ | Nao | Empresa do grupo |
| gestor | FK → Funcionario | Nao | Gestor direto |
| observacoes | text | Nao | Observacoes |
| created_at | datetime | Sim | Auditoria |
| updated_at | datetime | Sim | Auditoria |
| deleted_at | datetime | Nao | Soft delete |

### 3.2 Tipos de Contrato

| Tipo | Descricao |
|------|-----------|
| clt | CLT |
| pj | Pessoa Juridica |
| estagiario | Estagiario |
| temporario | Temporario |
| terceirizado | Terceirizado |
| aprendiz | Jovem Aprendiz |

### 3.3 Status do Funcionario

| Status | Descricao |
|--------|-----------|
| ativo | Ativo |
| afastado | Afastado |
| ferias | Em Ferias |
| licenca | Em Licenca |
| demitido | Demitido |
| aposentado | Aposentado |

### 3.4 Turnos

| Turno | Descricao |
|-------|-----------|
| diurno | Diurno |
| noturno | Noturno |
| integral | Integral |
| flexivel | Flexivel |

---

## 4. Relacionamentos

- **1:1 com PessoaFisica**
  Dados pessoais centralizados.

- **N:1 com Cargo**
  Cargo do funcionario.

- **N:1 com SubContrato**
  Alocacao para controle de custos.

- **N:1 com EmpresaCNPJ**
  Empresa do grupo.

- **N:1 com Funcionario (self)**
  Hierarquia de gestao.

- **1:N com Dependente**
  Dependentes do funcionario.

---

## 5. Regras de Negocio

1. A matricula e gerada automaticamente (AAAA + sequencial 4 digitos).

2. Todo funcionario deve ter uma PessoaFisica vinculada.

3. O campo `tem_dependente` e atualizado automaticamente.

4. O SubContrato define onde o funcionario esta alocado:
   - Permite rastrear custos por filial/contrato
   - Facilita relatorios por centro de custo

5. Exclusao e sempre soft delete.

---

## 6. Propriedades Calculadas

| Propriedade | Descricao |
|-------------|-----------|
| nome | Nome completo (via PessoaFisica) |
| cpf | CPF (via PessoaFisica) |
| cpf_formatado | CPF formatado |
| tempo_empresa | Dias na empresa |
| is_ativo | Se esta ativo |
| cargo_nome | Nome do cargo |
| subcontrato_numero | Numero do subcontrato |
| filial_nome | Nome da filial (via SubContrato) |
| contrato_numero | Numero do contrato (via SubContrato) |
| contratante_nome | Nome do contratante (via SubContrato) |

---

## 7. Endpoints (API)

### Base
`/api/rh/funcionarios/`

---

### 7.1 Listar

**GET** `/api/rh/funcionarios/`

Filtros possiveis:
- `search` - busca por nome, CPF, matricula ou cargo
- `status` - filtrar por status
- `tipo_contrato` - filtrar por tipo
- `departamento` - filtrar por departamento
- `empresa_id` - filtrar por empresa
- `cargo_id` - filtrar por cargo
- `subcontrato_id` - filtrar por subcontrato
- `filial_id` - filtrar por filial (via subcontrato)
- `contrato_id` - filtrar por contrato (via subcontrato)
- `gestor_id` - filtrar por gestor
- `apenas_ativos` - true/false

---

### 7.2 Obter por ID

**GET** `/api/rh/funcionarios/{id}/`

---

### 7.3 Criar Funcionario

**POST** `/api/rh/funcionarios/`

```json
{
  "nome_completo": "Joao da Silva",
  "cpf": "12345678901",
  "data_nascimento": "1990-05-15",
  "sexo": "M",
  "cargo": "uuid-do-cargo",
  "departamento": "Operacoes",
  "subcontrato": "uuid-do-subcontrato",
  "tipo_contrato": "clt",
  "data_admissao": "2024-01-15",
  "salario": 2500.00,
  "turno": "diurno",
  "tamanho_camisa": "M",
  "tamanho_calca": "42",
  "tamanho_botina": "40"
}
```

### 7.4 Editar Funcionario

**PATCH** `/api/rh/funcionarios/{id}/`

### 7.5 Acoes Especiais

| Acao | Metodo | Endpoint | Descricao |
|------|--------|----------|-----------|
| Demitir | POST | `/{id}/demitir/` | Registra demissao |
| Afastar | POST | `/{id}/afastar/` | Altera status para afastado |
| Ferias | POST | `/{id}/ferias/` | Altera status para ferias |
| Reativar | POST | `/{id}/reativar/` | Retorna ao status ativo |
| Ativos | GET | `/ativos/` | Lista funcionarios ativos |
| Afastados | GET | `/afastados/` | Lista afastados |
| Por departamento | GET | `/por_departamento/?departamento=X` | Lista por departamento |
| Aniversariantes | GET | `/aniversariantes/?mes=X` | Lista aniversariantes |
| Estatisticas | GET | `/estatisticas/` | Retorna estatisticas |
| Subordinados | GET | `/{id}/subordinados/` | Lista subordinados |
| Dependentes | GET | `/{id}/dependentes/` | Lista dependentes |

### 7.6 Excluir (Soft Delete)

**DELETE** `/api/rh/funcionarios/{id}/`

---

## 8. Integracao com SubContrato

A alocacao via SubContrato permite:

```
Funcionario → SubContrato → Filial + Contrato → Contratante
```

Isso possibilita:
- Saber em qual filial o funcionario trabalha
- Identificar o contrato/cliente atendido
- Calcular custos por centro de custo
- Gerar relatorios por alocacao

---

## 9. Vestimenta/Uniformes

Os campos de vestimenta facilitam:
- Controle de uniformes
- Pedidos de EPIs
- Inventario de roupas

| Campo | Exemplo |
|-------|---------|
| tamanho_camisa | PP, P, M, G, GG, XG |
| tamanho_calca | 36, 38, 40, 42, 44, 46 |
| tamanho_botina | 38, 39, 40, 41, 42, 43, 44 |

---

## 10. Erros e Excecoes

| Codigo | Mensagem | Motivo |
|--------|----------|--------|
| 400 | CPF invalido | CPF mal formatado |
| 400 | Cargo obrigatorio | Campo nao informado |
| 400 | Data de admissao obrigatoria | Campo nao informado |
| 404 | Funcionario nao encontrado | ID inexistente |
| 403 | Sem permissao | Usuario sem acesso |

---

## 11. Observacoes Tecnicas

- A PK e UUID e o soft delete e obrigatorio.
- Matricula gerada automaticamente no formato AAAANNNNN.
- Service layer deve ser usada para criacao e edicao.
- Indices criados para matricula, status, departamento, data_admissao e subcontrato.
- Relacionamentos usam on_delete=PROTECT para preservar integridade.
