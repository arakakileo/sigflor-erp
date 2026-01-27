# Dicionário de Dados (As-Is)

Este documento reflete as estruturas de dados implementadas no código-fonte do sistema. Funcionalidades planejadas mas não codificadas foram omitidas.

---

## 1. Módulo: Comum (Core)
Entidades base compartilhadas por todo o ERP.

### Pessoas e Empresas
| Entidade | Tabela Real | Descrição | Principais Campos Implementados |
| :--- | :--- | :--- | :--- |
| **PessoaFisica** | `pessoa_fisica` | Dados civis de um indivíduo. | `nome_completo`, `cpf`, `rg`, `data_nascimento`, `sexo`, `estado_civil`, `possui_deficiencia` |
| **PessoaJuridica** | `pessoa_juridica` | Dados legais de uma empresa. | `razao_social`, `nome_fantasia`, `cnpj` (14), `inscricao_estadual`, `situacao_cadastral` |
| **Empresa** | `empresas` | CNPJ do próprio Grupo Econômico. | FK `PessoaJuridica` (1:1), `ativa` |
| **Cliente** | `clientes` | Empresa contratante externa. | FK `PessoaJuridica` (1:1), FK `Empresa` (Gestora), `ativo` |
| **Filial** | `filiais` | Unidade operacional do Grupo. | `nome`, `codigo_interno` (Único), FK `Empresa`, `status` (Ativa/Inativa) |

### Auxiliares e Tabelas de Link
O sistema utiliza tabelas intermediárias explícitas para relacionamentos N:M.

| Entidade | Tabela Real | Relacionamentos |
| :--- | :--- | :--- |
| **Endereco** | `enderecos` | `logradouro`, `numero`, `bairro`, `cidade`, `estado`, `cep` |
| **PessoaFisicaEndereco** | `pessoas_fisicas_enderecos` | Link `PessoaFisica` <-> `Endereco`. Campos: `tipo` (Residencial...), `principal`. |
| **PessoaJuridicaEndereco** | `pessoas_juridicas_enderecos` | Link `PessoaJuridica` <-> `Endereco`. |
| **FilialEndereco** | `filiais_enderecos` | Link `Filial` <-> `Endereco`. |
| **Contato** | `contatos` | `tipo` (Email, Celular, Fixo), `valor`, `tem_whatsapp` |
| **PessoaFisicaContato** | `pessoas_fisicas_contatos` | Link de contatos para PF. `principal`, `contato_emergencia`. |
| **PessoaJuridicaContato** | `pessoas_juridicas_contatos` | Link de contatos para PJ. `principal`. |
| **FilialContato** | `filiais_contatos` | Link de contatos para Filial. `principal`. |
| **Documento** | `documentos` | `tipo` (RG, CNH...), `arquivo` (Path), `data_validade`, `mimetype`. |
| **PessoaFisicaDocumento** | `pessoas_fisicas_documentos` | Link PF <-> Documento. |
| **PessoaJuridicaDocumento** | `pessoas_juridicas_documentos` | Link PJ <-> Documento. |
| **Deficiencia** | `deficiencias` | Catálogo de deficiências (CID). `nome`, `tipo`, `cid`. |
| **PessoaFisicaDeficiencia**| `pessoas_fisicas_deficiencias`| Link PF <-> Deficiencia. Campos: `grau`, `congenita`. |
| **Projeto** | `projetos` | Centro de Custo/Obra. `nome`, `codigo`, FK `Filial`, FK `Cliente`. |

---

## 2. Módulo: Autenticação
Gerenciamento de usuários e controle de acesso (RBAC).

| Entidade | Tabela Real | Descrição | Principais Campos |
| :--- | :--- | :--- | :--- |
| **Usuario** | `usuarios` | Extensão do User Django. | `email` (Username), `previous_login`, `allowed_filiais` (N:M Filial), `papeis` (N:M) |
| **Papel** | `papeis` | Grupo de permissões (Role). | `nome` (Único), `descricao`, `permissoes` (N:M Django Permission) |

---

## 3. Módulo: RH (Recursos Humanos)
Gestão de funcionários e estrutura organizacional.

| Entidade | Tabela Real | Descrição | Principais Campos Implementados |
| :--- | :--- | :--- | :--- |
| **Cargo** | `cargos` | Posição funcional e riscos. | `nome`, `cbo`, `salario_base`, `nivel`, Riscos (`fisico`, `quimico`, etc), `ativo` |
| **CargoDocumento** | `cargos_documentos` | Regra de obrigatoriedade de docs. | FK `Cargo`, `documento_tipo`, `obrigatorio` |
| **Funcionario** | `funcionarios` | Vínculo empregatício. | `matricula` (Gerada auto), FK `PessoaFisica` (1:1), FK `Empresa`, FK `Cargo`, `data_admissao`, `sem_projeto_direto`*, `salario_nominal` |
| **Dependente** | `dependentes` | Familiar do funcionário. | FK `Funcionario`, FK `PessoaFisica` (1:1), `parentesco`, `dependencia_irrf` |
| **Equipe** | `equipes` | Time operacional. | `nome`, `tipo_equipe`, FK `Projeto`, FK `Lider` (Func), FK `Coordenador` (Func) |
| **EquipeFuncionario** | `equipes_funcionarios` | Alocação em equipe. | FK `Equipe`, FK `Funcionario`, `data_entrada`, `data_saida` |

> *Nota: O campo de alocação direta `projeto` no Funcionário está comentado no código. A alocação atual ocorre via `Equipe`.*

---

## 4. Módulo: SST (Saúde e Segurança)
Gestão de exames ocupacionais.

| Entidade | Tabela Real | Descrição | Principais Campos |
| :--- | :--- | :--- | :--- |
| **Exame** | `sst_exame`* | Catálogo de exames. | `nome`, `descricao` (*Nome tabela inferido padrão Django, verificar migrations se necessário*) |
| **CargoExame** | `cargos_exames` | Regra de exames por cargo. | FK `Cargo`, FK `Exame`, `periodicidade_meses` |
| **Aso** | `aso` | Atestado de Saúde (Cabeçalho). | FK `Funcionario`, `tipo` (Admissional...), `status`, `resultado`, FK `Documento` (PDF) |
| **ExameRealizado** | `exames_realizados` | Item do ASO. | FK `ASO`, FK `Exame`, `data_realizacao`, `data_vencimento`, `resultado` |