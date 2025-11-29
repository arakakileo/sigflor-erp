# Dicionário de Dados

Este documento descreve as principais entidades de negócio do sistema e seus campos mais relevantes, com foco na nova estrutura orientada a domínio.

---

## Módulo: Core (Entidades Centrais)

O módulo `core` contém as entidades fundamentais que são compartilhadas por todo o sistema.

| Entidade | Tabela (Exemplo) | Descrição | Principais Campos |
| :--- | :--- | :--- |:--- |
| **PessoaFisica** | `core_pessoafisica` | O indivíduo civil. | `cpf` (Único), `nome_completo`, `raca_cor`, `escolaridade`, `usa_oculos_grau` |
| **PessoaJuridica** | `core_pessoajuridica` | Entidade legal base. | `cnpj` (Único), `razao_social`, `nome_fantasia` |
| **Empresa** | `core_empresa` | **(Quem fatura)** Um CNPJ do próprio Grupo Econômico. | FK `PessoaJuridica`, `ativa` |
| **Cliente** | `core_cliente` | **(Quem paga)** A empresa contratante externa. | FK `PessoaJuridica`, FK `Empresa` (Gestora) |
| **Filial** | `core_filial` | **(Onde executa)** Base operacional física/geográfica. | `nome`, `codigo_interno`, FK `Empresa` |
| **Projeto** | `core_projeto` | **(Centro de Custo/Obra)** Une `Empresa`, `Cliente`, `Filial`. | FK `Empresa` (Auto-preenchido), FK `Cliente`, FK `Filial` |
| **Endereco** | `core_endereco` | Repositório de logradouros. | `logradouro`, `cep`, `cidade`, `estado` |
| **Contato** | `core_contato` | Contato (telefone, e-mail). | `tipo`, `valor`, `tem_whatsapp` |
| **Documento** | `core_documento` | Arquivos formais com metadados. | `tipo`, `arquivo`, `data_validade` |
| **Exame** | `core_exame` | Cadastro mestre de exames. | `nome` |

### Detalhes Importantes do "Tripé" (Projeto)

-   **`Cliente.empresa_gestora`**: Define qual `Empresa` do seu Grupo Econômico é a "dona" da conta deste `Cliente`.
-   **`Projeto.empresa`**: Campo de **apenas leitura**. O sistema copia automaticamente a `empresa_gestora` do `Cliente` selecionado.

---

## Módulo: RH (Recursos Humanos)

| Entidade | Tabela (Exemplo) | Descrição | Principais Campos |
| :--- | :--- | :--- | :--- |
| **Funcionario** | `rh_funcionario` | Vínculo empregatício. | FK `PessoaFisica`, FK `Empresa`, `matricula`, FK `Cargo`, FK `Projeto` |
| **Cargo** | `rh_cargo` | Posição/função. | `nome`, `cbo`, `salario_base`, `risco_fisico`, `risco_biologico`, `risco_quimico`, `risco_ergonomico`, `risco_acidente` |
| **CargoDocumento** | `rh_cargo_documento` | Documentos obrigatórios por cargo. | FK `Cargo`, `documento_tipo`, `obrigatorio` |
| **Dependente** | `rh_dependente` | Vínculo de dependência com funcionário. | FK `Funcionario`, FK `PessoaFisica`, `parentesco` |
| **Equipe** | `rh_equipe` | Grupo de trabalho. | `nome`, `tipo_equipe`, FK `Projeto`, FK `Funcionario` (Líder), FK `Funcionario` (Coordenador) |
| **EquipeFuncionario** | `rh_equipe_funcionario` | Membro de equipe. | FK `Equipe`, FK `Funcionario`, `data_entrada`, `data_saida` |

---

## Módulo: SST (Saúde e Segurança do Trabalho)

| Entidade | Tabela (Exemplo) | Descrição | Principais Campos |
| :--- | :--- | :--- | :--- |
| **ASO** | `sst_aso` | Atestado de Saúde Ocupacional (processo). | FK `Funcionario`, `tipo`, `status`, `data_solicitacao`, FK `Documento` (PDF) |
| **CargoExame** | `sst_cargo_exame` | Exames e periodicidade por cargo. | FK `Cargo`, FK `Exame`, `periodicidade_meses` |
| **ExameRealizado** | `sst_exame_realizado` | Registro de exame individual. | FK `ASO`, FK `Exame`, `data_realizacao`, `data_vencimento`, `resultado` |

---

## Módulo: Alojamento

| Entidade | Tabela (Exemplo) | Descrição | Principais Campos |
| :--- | :--- | :--- | :--- |
| **Alojamento** | `alojamento_alojamento` | Local de moradia. | `nome`, FK `Filial`, `tipo_moradia`, `capacidade`, `valor_aluguel` |
| **AlojamentoFuncionario** | `alojamento_alojamento_funcionario` | Ocupação de funcionário. | FK `Alojamento`, FK `Funcionario`, `data_entrada`, `data_saida` |