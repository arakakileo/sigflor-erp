# 5. Fluxos de Negócio (MVP de RH)

Este documento descreve os principais fluxos de negócio do MVP do módulo de Recursos Humanos, detalhando as interações do usuário, as regras de negócio e as entidades envolvidas. Ele serve como um guia funcional para a compreensão das operações críticas do sistema.

---

## 5.1. Admissão de um Novo Funcionário

**Objetivo:** Registrar um novo colaborador no sistema, desde seus dados pessoais até o vínculo empregatício e a alocação inicial.

**Atores:** Administrativo de RH.

**Pré-condições:**
*   [Cargos](../rh/cargos.md) e [Projetos](../core/projeto.md) devem estar previamente cadastrados.
*   [Tipos de Documento](../core/documentos.md) devem estar configurados.
*   [Regras de `CargoDocumento`](rh/cargo_documento.md) devem estar definidas.

**Fluxo:**
1.  **Início do Cadastro:** O usuário de RH inicia o processo de admissão, fornecendo:
    *   **Dados Pessoais:** Nome Completo, CPF, Data de Nascimento, Sexo, Estado Civil, Raça/Cor, Escolaridade, Uso de Óculos, Cidade Atual, Cidade Natal, Contatos (telefone, e-mail, emergência).
    *   **Dados Contratuais:** Cargo, Empresa empregadora, Salário Nominal, Tipo de Contrato, Data de Admissão, Turno, PIS/NIS, Dados da CTPS.
    *   **Dados Complementares:** Peso, Altura, Indicação, Tamanhos de Uniforme.
2.  **Gerenciamento de `PessoaFisica`:**
    *   O sistema (`FuncionarioService`) utiliza o CPF para verificar se a `PessoaFisica` já existe ([`PessoaFisicaService`](../core/pessoa_fisica.md)).
    *   Se existir, os dados da `PessoaFisica` existente são atualizados com as informações fornecidas.
    *   Se não existir, uma nova `PessoaFisica` é criada com os dados informados.
3.  **Geração de Matrícula:** O sistema gera automaticamente uma `matricula` única para o novo funcionário (ex: `AAAANNNC`).
4.  **Validação de Salário:**
    *   Se o `salario_nominal` for informado, ele é validado para ser igual ou superior ao `salario_base` do [Cargo](rh/cargos.md) selecionado.
    *   Se o `salario_nominal` **não** for informado, o sistema assume o `salario_base` do [Cargo](rh/cargos.md) como padrão.
5.  **Criação de `Funcionario`:** O sistema cria a entidade [`Funcionario`](rh/funcionarios.md), vinculando-a à `PessoaFisica` existente/criada, ao `Cargo`, `Empresa` e ao `Projeto` inicial (se informado).
6.  **Gerenciamento de Endereços:** O usuário fornece os dados do endereço principal. O sistema ([`EnderecoService`](../core/enderecos.md)) cria ou vincula o `core.Endereco` à `PessoaFisica` via `PessoaFisicaEndereco`.
7.  **Gerenciamento de Contatos:** O usuário fornece os contatos (telefone, e-mail) e os contatos de emergência. O sistema ([`ContatoService`](../core/contatos.md)) realiza um `get_or_create` para cada contato (`core.Contato`) e cria os vínculos (`PessoaFisicaContato`), definindo as flags `principal` e `contato_emergencia`.
8.  **Gerenciamento de Documentos:** O usuário faz o upload dos documentos necessários. O sistema ([`DocumentoService`](../core/documentos.md)) cria as entidades `core.Documento` para cada arquivo e os vincula à `PessoaFisica` via `PessoaFisicaDocumento`.
9.  **Validação de Documentos Obrigatórios por Cargo:**
    *   O sistema consulta as regras em [`hr.CargoDocumento`](rh/cargo_documento.md) para o `Cargo` do funcionário.
    *   Verifica se todos os documentos marcados como obrigatórios para aquele cargo foram fornecidos e estão válidos (se tiverem `data_validade`).
    *   Se houver pendências, o sistema pode:
        *   Impedir a conclusão da admissão.
        *   Marcar a admissão como "Pendente de Documentos".
        *   Gerar alertas para o RH.
10. **Conclusão:** O funcionário é registrado no sistema com status `ATIVO` e alocado ao `Projeto` inicial.

---

## 5.2. Gestão de Dependentes

**Objetivo:** Registrar e gerenciar os dependentes de um funcionário.

**Atores:** Administrativo de RH.

**Pré-condições:** Funcionário já cadastrado.

**Fluxo:**
1.  **Início do Cadastro:** O usuário de RH acessa o perfil de um `Funcionario` e inicia o cadastro de um dependente.
2.  **Fornecimento de Dados:** Informa os dados pessoais do dependente (Nome Completo, CPF, Data de Nascimento, Parentesco, se é dependente para IRRF).
3.  **Gerenciamento de `PessoaFisica` do Dependente:** O sistema ([`DependenteService`](rh/dependentes.md)) utiliza o CPF para `get_or_create` a `PessoaFisica` do dependente.
4.  **Criação de `Dependente`:** Cria a entidade [`Dependente`](rh/dependentes.md), vinculando-a ao `Funcionario` e à `PessoaFisica` do dependente.
5.  **Atualização do `Funcionario`:** A flag `tem_dependente` no `Funcionario` é atualizada automaticamente para `True`.
6.  **Gerenciamento de Documentos do Dependente:** O usuário anexa documentos específicos do dependente (Certidão de Nascimento, Carteira de Vacinação, Declaração Escolar).
7.  **Conclusão:** O dependente é registrado e associado ao funcionário.

---

## 5.3. Gestão de ASO (Atestado de Saúde Ocupacional)

**Objetivo:** Gerenciar o ciclo de vida dos ASOs, desde a solicitação até o registro detalhado dos exames e a finalização.

**Atores:** Equipe de SST.

**Pré-condições:**
*   rh/funcionarios.md cadastrado.
*   [Exames](../core/exame.md) e [`CargoExame`](sst/saude_ocupacional.md) configurados.

**Fluxo:**
1.  **Solicitação de ASO:**
    *   A equipe de SST cria um novo [`ASO`](sst/saude_ocupacional.md) para um `Funcionario`, definindo o `tipo` (Admissional, Periódico, Demissional, etc.). O `status` inicial é `ABERTO`.
    *   O sistema (`ASOService`) pré-popula a lista de exames esperados (entidades `sst.ExameRealizado` com `data_realizacao` e `resultado` vazios):
        *   **ASO Demissional:** Todos os exames do `Cargo` via `CargoExame`, independente do vencimento.
        *   **ASO Periódico:** Somente exames vencidos ou a vencer (em período configurável).
        *   **Outros Tipos:** Baseado nas regras do `Cargo`.
2.  **Registro dos Exames:**
    *   O funcionário realiza os exames. A equipe de SST atualiza cada [`ExameRealizado`](sst/saude_ocupacional.md) individualmente.
    *   Informam `data_realizacao` e `resultado` para cada exame.
    *   O sistema calcula `data_vencimento` (`data_realizacao` + `periodicidade_meses` do `CargoExame`).
    *   O `status` do `ASO` muda para `EM_ANDAMENTO` após o primeiro exame registrado.
    *   **Regra:** Não é possível adicionar exames não vencidos em ASOs Periódicos. Permite-se editar/excluir exames `ExameRealizado` para correção (soft delete para exclusão).
3.  **Finalização do ASO:**
    *   Quando todos os exames são registrados, a equipe de SST "finaliza" o `ASO`.
    *   Informam `data_finalizacao`, `medico_responsavel` e `resultado_final` do ASO.
    *   **Anexo do Documento:** O PDF escaneado do ASO completo é anexado e vinculado ao campo `documento_aso_pdf` do `ASO`.
    *   O `status` do `ASO` muda para `FINALIZADO`.
4.  **Monitoramento:** O sistema pode gerar relatórios e alertas sobre `ExameRealizado`s próximos do vencimento.

---

## 5.4. Alocação em Alojamento

**Objetivo:** Gerenciar a ocupação de funcionários em alojamentos da empresa, rastreando entradas e saídas.

**Atores:** Administrativo de RH, Gestão de Alojamentos.

**Pré-condições:**
*   rh/funcionarios.md cadastrado.
*   [Alojamento](alojamento/alojamentos.md) cadastrado.

**Fluxo:**
1.  **Cadastro de Alojamento:** A equipe responsável cadastra novos [`Alojamentos`](alojamento/alojamentos.md), informando: Nome, Filial, Responsável, Tipo de Moradia, Capacidade, Contrato de Aluguel (documento), Valor de Aluguel, Datas de Contrato.
2.  **Alocação de Funcionário:**
    *   O usuário seleciona um `Funcionario` e um `Alojamento`.
    *   Define a `data_entrada` do funcionário no alojamento.
    *   O sistema (`AlojamentoService` ou similar) cria um registro em [`alojamento.AlojamentoFuncionario`](alojamento/alojamentos.md).
    *   **Regra:** Se o funcionário já estiver em outro alojamento ativo, a alocação anterior é automaticamente encerrada (com `data_saida` preenchida).
3.  **Desalocação de Funcionário:** O usuário define a `data_saida` para um registro de `AlojamentoFuncionario`, liberando a vaga.
4.  **Monitoramento:** O sistema pode monitorar a ocupação atual dos alojamentos e gerar relatórios de custos.

---

## 5.5. Criação e Gestão de Equipes

**Objetivo:** Organizar funcionários em equipes para a execução de projetos, definindo líderes e coordenadores.

**Atores:** Gestão de Operações, Administrativo de RH.

**Pré-condições:**
*   [Funcionários](rh/funcionarios.md) e [Projetos](../core/projeto.md) cadastrados.

**Fluxo:**
1.  **Criação de Equipe:**
    *   O usuário cria uma nova rh/equipes.md, informando: Nome, Tipo (Manual/Mecanizada), [Projeto](core/projeto.md) de alocação, [Líder](rh/funcionarios.md) (um `Funcionario` específico) e [Coordenador](rh/funcionarios.md) (outro `Funcionario`).
    *   **Regra:** O Líder da equipe não pode ser líder de outra equipe ativa.
2.  **Adição de Membros:**
    *   O usuário adiciona `Funcionario`s à `Equipe`, definindo a `data_entrada`.
    *   O sistema cria registros em [`hr.EquipeFuncionario`](hr/equipes.md).
    *   **Regra:** Se um funcionário já estiver em outra equipe ativa, a alocação anterior é encerrada (`data_saida` preenchida).
3.  **Remoção de Membros:** O usuário define a `data_saida` para um `EquipeFuncionario`, removendo o membro da equipe.
4.  **Monitoramento:** O sistema pode gerar listas de equipes por projeto, por líder, e a composição atual de cada equipe.

---

## 5.6. Desligamento de Funcionário

**Objetivo:** Registrar o desligamento de um funcionário do quadro da empresa e desativar seus vínculos.

**Atores:** Administrativo de RH.

**Pré-condições:** rh/funcionarios.md ativo no sistema.

**Fluxo:**
1.  **Início do Desligamento:** O usuário de RH acessa o perfil do `Funcionario` e inicia o processo de desligamento, informando a `data_demissao` e o `motivo`.
2.  **Atualização de `Funcionario`:** O sistema (`FuncionarioService`) atualiza o `status` do `Funcionario` para `DEMITIDO` e preenche a `data_demissao`.
3.  **Encerramento de Vínculos:**
    *   **Alocação em Alojamento:** Encerra quaisquer [`alojamento.AlojamentoFuncionario`](alojamento/alojamentos.md) ativos do funcionário.
    *   **Membro de Equipe:** Remove o funcionário de qualquer [`hr.EquipeFuncionario`](hr/equipes.md) ativo.
    *   **Dependentes:** O sistema pode desativar (`ativo=False`) os [`hr.Dependente`](rh/dependentes.md)s associados ou, no mínimo, alertar o RH para revisão.
4.  **Pendências de ASO:** O sistema verifica se há [`sst.ASO`](sst/saude_ocupacional.md)s pendentes para o funcionário.
    *   Se houver, pode acionar a criação de um ASO Demissional no módulo SST ou gerar um alerta para a equipe de SST.
5.  **Soft Delete:** O registro do `Funcionario` é logicamente excluído, mantendo seu histórico, mas removendo-o das listagens ativas.
6.  **Conclusão:** O funcionário é marcado como desligado no sistema.
