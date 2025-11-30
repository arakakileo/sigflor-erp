# CLAUDE.md

This file provides guidance to Claude Code when working with the Sigflor ERP codebase.

## Project Overview

**Sigflor** is an ERP system for reforestation companies (setor de reflorestamento), built with Django + Django REST Framework. The MVP focuses on the HR (RH) module with supporting modules for Occupational Health & Safety (SST) and Housing (Alojamento).

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.13+ |
| Backend Framework | Django 5.x + Django REST Framework |
| Database | PostgreSQL |
| Auth | JWT (SimpleJWT) |
| Package Manager | Poetry |
| Infrastructure | Docker |

## Project Structure

```
XipaDoce/
├── src/sigflor_server/
│   ├── apps/
│   │   ├── comum/          # Core module (shared entities)
│   │   │   ├── models/
│   │   │   ├── serializers/
│   │   │   ├── services/
│   │   │   ├── selectors/
│   │   │   ├── views/
│   │   │   ├── validators/
│   │   │   └── permissions.py
│   │   ├── rh/             # HR module
│   │   │   ├── models/
│   │   │   ├── serializers/
│   │   │   ├── services/
│   │   │   ├── selectors/
│   │   │   └── views/
│   │   ├── sst/            # Occupational Health & Safety (incomplete)
│   │   └── alojamento/     # Housing (not yet created)
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── exceptions.py   # Custom DRF exception handler
│   └── manage.py
├── docs/                   # Documentation
├── tests/
├── pyproject.toml
└── poetry.lock
```

## Development Commands

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run migrations
cd src/sigflor_server
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Make migrations after model changes
python manage.py makemigrations

# Run tests
pytest
```

## Architecture Pattern

The project follows a **layered architecture** with strict separation of concerns:

```
Views (API) → Serializers → Services → Selectors → Models
```

| Layer | Responsibility |
|-------|----------------|
| **Views** | HTTP request/response handling, orchestration only |
| **Serializers** | Data validation, transformation, formatting |
| **Services** | ALL business logic lives here (create, update, delete operations) |
| **Selectors** | Read operations, optimized queries with select_related/prefetch_related |
| **Models** | Data structure, ORM, database constraints |

**Important:** Never put business logic in Views or Serializers. Always use Services.

## Key Design Patterns

### 1. Soft Delete (Global)
All models inherit from `SoftDeleteModel` in `comum/models/base.py`. Records are never physically deleted - they use `deleted_at` timestamp.

```python
# Wrong
obj.delete()  # This actually soft-deletes

# To query including deleted
Model.all_objects.all()

# To query only active (default)
Model.objects.all()
```

### 2. UUID Primary Keys
All models use UUID as primary key, not auto-increment integers.

### 3. Audit Fields
All models have: `created_at`, `updated_at`, `created_by`, `updated_by`

### 4. No Generic Foreign Keys (GFKs)
GFKs are prohibited. Use explicit junction tables instead.

### 5. RBAC Permissions
- `Permissao`: Atomic permissions with pattern `modulo_entidade_acao` (e.g., `rh_funcionario_visualizar`)
- `Papel`: Groups of permissions (roles)
- `Usuario.allowed_filiais`: M2M for regional access control
- Permission checks happen in Services layer

### 6. Projeto (Project) as Cost Center
`Projeto` is the central entity connecting:
- `Empresa` (company that invoices)
- `Cliente` (client that pays)
- `Filial` (branch where work is executed)

The `empresa` field is auto-filled from `cliente.empresa_gestora` on save.

## Core Entities (comum module)

| Entity | Purpose |
|--------|---------|
| PessoaFisica | Individual person records |
| PessoaJuridica | Legal entity records |
| Usuario | System users with RBAC |
| Empresa | Companies in the group |
| Cliente | Clients (who pay) |
| Filial | Operational branches |
| Projeto | Cost center (ties Empresa+Cliente+Filial) |
| Contrato/SubContrato | Commercial contracts |
| Endereco | Addresses (linked to entities) |
| Contato | Contacts (linked to entities) |
| Documento | Documents (linked to entities) |
| Anexo | File attachments |
| Deficiencia | Disabilities registry |
| Exame | Master exam types |

## RH Module Entities

| Entity | Purpose |
|--------|---------|
| Funcionario | Employees |
| Cargo | Job positions |
| CargoDocumento | Required docs per position (TODO) |
| Dependente | Employee dependents |
| Equipe | Teams linked to projects |
| EquipeFuncionario | Team membership |

## API Endpoints

```
/api/comum/empresas/
/api/comum/clientes/
/api/comum/filiais/
/api/comum/contratos/
/api/comum/projetos/
/api/comum/exames/
/api/comum/usuarios/
...

/api/rh/funcionarios/
/api/rh/cargos/
/api/rh/dependentes/
/api/rh/equipes/
```

## Code Style Guidelines

1. **Language:** All code comments, docstrings, and variable names in Portuguese (PT-BR)
2. **Imports:** Group by stdlib, third-party, local; use absolute imports
3. **Services:** Always accept `user` parameter for permission checks
4. **Selectors:** Always use `select_related`/`prefetch_related` for related objects
5. **Serializers:** Use `read_only_fields` for computed/auto-filled fields

## Current Development Status

See `PROJETO_SIGFLOR_MVP_RH_STATUS.md` for detailed progress tracking.

**Completed:**
- Core module structure (models, serializers, services, views)
- Projeto and Exame entities
- Funcionario with regional permission structure
- Equipe/EquipeFuncionario models
- Custom DRF exception handler
- RBAC permission classes

**In Progress (Priority 1):**
- Funcionario views integration with permissions
- CargoDocumento model
- Dependente full CRUD with business logic
- Equipe serializers, services, views

**TODO (Priority 2):**
- SST module (ASO, CargoExame, ExameRealizado)
- Alojamento module

## Documentation

Detailed documentation is in `/docs`:
- `01_visao_geral.md` - System overview
- `02_arquitetura.md` - Architecture decisions
- `03_estrutura_diretorios.md` - Directory structure
- `04_dicionario_de_dados.md` - Data dictionary
- `05_fluxos_de_negocio.md` - Business flows
- `core/` - Core module entity docs
- `rh/` - HR module entity docs
- `sst/` - SST module entity docs
- `alojamento/` - Housing module docs

## Common Patterns

### Creating a new entity

1. Create model in `models/entity_name.py`
2. Import in `models/__init__.py`
3. Create serializer in `serializers/entity_name.py`
4. Create service in `services/entity_name.py`
5. Create selector functions in `selectors/__init__.py`
6. Create view in `views/entity_name.py`
7. Register URLs in `urls.py`
8. Run `makemigrations` and `migrate`

### Service method pattern

```python
class EntityService:
    @staticmethod
    def create(*, user, **data):
        # 1. Check permissions
        # 2. Validate business rules
        # 3. Create object
        # 4. Return created object
        pass

    @staticmethod
    def update(*, user, instance, **data):
        # 1. Check permissions (including regional)
        # 2. Validate business rules
        # 3. Update object
        # 4. Return updated object
        pass
```

### Selector pattern

```python
def entity_list(*, user=None, filters=None):
    queryset = Entity.objects.select_related('related_field')
    if user and not user.is_superuser:
        queryset = queryset.filter(filial__in=user.allowed_filiais.all())
    if filters:
        queryset = queryset.filter(**filters)
    return queryset
```
