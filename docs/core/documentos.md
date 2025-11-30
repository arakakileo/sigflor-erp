# Core — Documentos (Especificação Detalhada)

## 1. Visão Geral

O submódulo de **Documentos** fornece uma estrutura centralizada para o upload e armazenamento de arquivos formais e categorizados. Diferente de `Anexos` (informais), `Documentos` possuem metadados estruturados como tipo, data de emissão e validade.

**Propósito Arquitetural:** Centralizar a gestão de arquivos formais, permitindo o reaproveitamento da lógica de armazenamento, validação e controle de acesso, e associando-os a diferentes entidades através de **tabelas de vínculo explícitas** (sem uso de Generic Foreign Keys).

**Status:** ✅ IMPLEMENTADO

---

## 2. Estrutura do Modelo (`comum.Documento`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **tipo** | `models.CharField` | `VARCHAR(50)` | `choices=Documento.Tipo.choices` (Enum). `null=False`, `blank=False`. |
| **descricao** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. |
| **arquivo** | `models.FileField` | `VARCHAR(255)` | `upload_to='documentos/%Y/%m/'`. O arquivo físico. |
| **nome_original** | `models.CharField` | `VARCHAR(255)` | Nome do arquivo no momento do upload. Preenchido automaticamente. |
| **mimetype** | `models.CharField` | `VARCHAR(100)` | Tipo MIME do arquivo (ex: `application/pdf`). Preenchido automaticamente. |
| **tamanho** | `models.PositiveIntegerField` | `INTEGER` | Tamanho do arquivo em bytes. Preenchido automaticamente. |
| **data_emissao** | `models.DateField` | `DATE` | `null=True`, `blank=True`. |
| **data_validade** | `models.DateField` | `DATE` | `null=True`, `blank=True`. **Regra:** Importante para CNH, ASO, etc. |

### Campos Herdados (SoftDeleteModel)
- `created_at`, `updated_at`, `deleted_at`
- `created_by`, `updated_by`

### Propriedades Computadas
- **`vencido`**: `bool` - Retorna `True` se `data_validade < hoje`.

### Enum `Tipo` para `Documento`
```python
class Tipo(models.TextChoices):
    # Documentos Pessoais
    RG = 'RG', 'RG'
    CNH = 'CNH', 'Carteira Nacional de Habilitação'
    CPF = 'CPF', 'Cadastro de Pessoas Físicas'
    TITULO_ELEITOR = 'TITULO_ELEITOR', 'Título de Eleitor'
    CERTIDAO_NASCIMENTO_CASAMENTO = 'CERTIDAO_NASCIMENTO_CASAMENTO', 'Certidão de Nascimento/Casamento'
    COMPROVANTE_ENDERECO = 'COMPROVANTE_ENDERECO', 'Comprovante de Endereço'
    CARTAO_SUS = 'CARTAO_SUS', 'Cartão do SUS'
    CARTEIRA_VACINA = 'CARTEIRA_VACINA', 'Carteira de Vacinação (Geral)'
    COMPROVANTE_PIS_NIS = 'COMPROVANTE_PIS_NIS', 'Comprovante PIS/NIS'
    CTPS = 'CTPS', 'Carteira de Trabalho Digital'
    CARTAO_CONTA_BANCO = 'CARTAO_CONTA_BANCO', 'Cartão/Comprovante de Conta Bancária'
    FOTO_3X4 = 'FOTO_3X4', 'Foto 3x4'

    # Documentos de Dependentes
    CERTIDAO_NASCIMENTO_DEPENDENTE = 'CERTIDAO_NASCIMENTO_DEPENDENTE', 'Certidão de Nascimento de Dependente'
    CARTEIRA_VACINA_DEPENDENTE = 'CARTEIRA_VACINA_DEPENDENTE', 'Carteira de Vacinação de Dependente'
    DECLARACAO_ESCOLAR_DEPENDENTE = 'DECLARACAO_ESCOLAR_DEPENDENTE', 'Declaração de Matrícula Escolar de Dependente'

    # Documentos de Habilitação/Cursos
    NADA_CONSTA_DETRAN = 'NADA_CONSTA_DETRAN', 'Nada Consta DETRAN'
    CURSO_MOOP = 'CURSO_MOOP', 'Certificado Curso MOOP'
    CURSO_PASSAGEIROS = 'CURSO_PASSAGEIROS', 'Certificado Curso Transporte de Passageiros'
    CURSO_MAQUINAS_AGRICOLAS = 'CURSO_MAQUINAS_AGRICOLAS', 'Certificado Curso Operação de Máquinas Agrícolas'

    # Documentos de Saúde Ocupacional
    ASO = 'ASO', 'Atestado de Saúde Ocupacional (Documento PDF)'

    # Documentos Empresariais
    CONTRATO_SOCIAL = 'CONTRATO_SOCIAL', 'Contrato Social'
    NOTA_FISCAL = 'NOTA_FISCAL', 'Nota Fiscal'
    CONTRATO = 'CONTRATO', 'Contrato'
    ADITIVO = 'ADITIVO', 'Aditivo Contratual'
    CRLV = 'CRLV', 'CRLV'
    LAUDO = 'LAUDO', 'Laudo'

    # Outros
    OUTROS = 'OUTROS', 'Outros Documentos'
```
**Nota:** Esta lista pode ser estendida conforme necessidade do negócio.

---

## 3. Relacionamentos (Modelo de Composição)

O modelo `Documento` não possui vínculo direto com entidades. A associação é feita através de **tabelas de vínculo explícitas**, seguindo o padrão arquitetural do projeto (sem GFKs).

### 3.1 Tabela de Vínculo: `PessoaFisicaDocumento`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **pessoa_fisica** | `models.ForeignKey` para `PessoaFisica` | `on_delete=models.CASCADE`, `related_name='documentos_vinculados'`. |
| **documento** | `models.ForeignKey` para `Documento` | `on_delete=models.CASCADE`, `related_name='vinculos_pessoa_fisica'`. |
| **principal** | `models.BooleanField` | `default=False`. |

**Constraints:**
- `UniqueConstraint(fields=['pessoa_fisica', 'documento'])` - Impede duplicação de vínculo.
- A regra de "apenas um documento principal por tipo" é garantida na camada de `Service`.

**Tabela PostgreSQL:** `pessoas_fisicas_documentos`

### 3.2 Tabela de Vínculo: `PessoaJuridicaDocumento`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **pessoa_juridica** | `models.ForeignKey` para `PessoaJuridica` | `on_delete=models.CASCADE`, `related_name='documentos_vinculados'`. |
| **documento** | `models.ForeignKey` para `Documento` | `on_delete=models.CASCADE`, `related_name='vinculos_pessoa_juridica'`. |
| **principal** | `models.BooleanField` | `default=False`. |

**Constraints:**
- `UniqueConstraint(fields=['pessoa_juridica', 'documento'])` - Impede duplicação de vínculo.

**Tabela PostgreSQL:** `pessoas_juridicas_documentos`

### Sobre o Campo `principal`

O campo `principal` nas tabelas de vínculo permite que uma entidade tenha múltiplos documentos do mesmo tipo (ex: CNH vencida e CNH atual), mas apenas um seja marcado como "principal" ou "vigente" para aquele tipo. A lógica de negócio que garante isso está implementada no `DocumentoService`.

---

## 4. Estratégia de Indexação

| Índice | Campos | Propósito |
| :--- | :--- | :--- |
| B-Tree | `tipo` | Filtros por tipo de documento |
| B-Tree | `data_validade` | Busca por documentos vencidos ou a vencer |
| Composto | `(tipo, data_emissao)` | Consultas combinadas |

---

## 5. Camada de Serviço (`DocumentoService`)

### Métodos de Criação

- **`create(*, tipo, arquivo, descricao, data_emissao, data_validade, created_by)`**:
  - Cria um documento sem vínculo com entidade.
  - Extrai automaticamente `nome_original`, `mimetype` e `tamanho` do arquivo.
  - Valida o tipo MIME do arquivo.

- **`add_documento_to_pessoa_fisica(*, pessoa_fisica, tipo, arquivo, descricao, data_emissao, data_validade, principal, created_by)`**:
  - Cria o documento e o vínculo com `PessoaFisica` em uma transação.
  - Se `principal=True`, desmarca outros documentos do mesmo tipo como principal.
  - Retorna a instância de `PessoaFisicaDocumento`.

- **`add_documento_to_pessoa_juridica(*, pessoa_juridica, tipo, arquivo, ...)`**:
  - Análogo ao método acima para `PessoaJuridica`.

### Métodos de Atualização

- **`update(documento, updated_by, **kwargs)`**:
  - Atualiza metadados do documento (tipo, descricao, datas).
  - Não permite alteração do arquivo (imutável).

- **`set_principal_pessoa_fisica(*, vinculo, updated_by)`**:
  - Define um documento como principal, desmarcando outros do mesmo tipo.

- **`set_principal_pessoa_juridica(*, vinculo, updated_by)`**:
  - Análogo ao método acima.

### Métodos de Exclusão

- **`delete(documento, user)`**: Soft delete do documento e seus vínculos.
- **`remove_vinculo_pessoa_fisica(vinculo, user)`**: Remove apenas o vínculo.
- **`remove_vinculo_pessoa_juridica(vinculo, user)`**: Remove apenas o vínculo.

### Métodos de Consulta

- **`get_documentos_pessoa_fisica(pessoa_fisica)`**: Retorna todos os documentos vinculados.
- **`get_documentos_pessoa_juridica(pessoa_juridica)`**: Análogo ao acima.
- **`get_documentos_a_vencer(dias=30)`**: Documentos cuja validade expira em N dias.
- **`get_documentos_vencidos()`**: Documentos já vencidos.

---

## 6. Validação de Arquivos

O `DocumentoService` utiliza `validar_tipo_arquivo()` para garantir que apenas tipos MIME permitidos sejam aceitos:

**Tipos permitidos por padrão:**
- `application/pdf`
- `image/jpeg`, `image/png`
- `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `application/vnd.ms-excel`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

---

## 7. Serializers

| Serializer | Propósito |
| :--- | :--- |
| `DocumentoSerializer` | Leitura completa do documento |
| `DocumentoCreateSerializer` | Criação com upload de arquivo |
| `PessoaFisicaDocumentoSerializer` | Vínculo PF com documento aninhado |
| `PessoaFisicaDocumentoListSerializer` | Listagem simplificada |
| `PessoaJuridicaDocumentoSerializer` | Vínculo PJ com documento aninhado |
| `PessoaJuridicaDocumentoListSerializer` | Listagem simplificada |