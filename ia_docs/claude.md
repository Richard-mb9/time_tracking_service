# Padrões de Arquitetura do Projeto

Este documento define os padrões arquiteturais que devem ser seguidos em todos os projetos baseados nesta estrutura. Utiliza Clean Architecture com FastAPI e SQLAlchemy.

## Tecnologias Padrão

- **Linguagem:** Python
- **Framework Web:** FastAPI
- **ORM:** SQLAlchemy (classical/imperative mapping)
- **Banco de Dados:** PostgreSQL
- **Validação de Requests:** Pydantic
- **Schemas de Response:** `@dataclass` (do módulo `dataclasses`)

## Instanciação do FastAPI

Arquivo: `src/api/app.py`

```python
from fastapi import FastAPI
from infra.mappers import import_mappers
from api.routers import create_routes

URL_PREFIX = ""
API_DOC = f"{URL_PREFIX}/doc/api"
API_DOC_REDOC = f"{URL_PREFIX}/doc/redoc"
API_DOC_JSON = f"{URL_PREFIX}/doc/api.json"
API_VERSION = "V1.0.0"


def create_app():
    import_mappers()

    api = FastAPI(
        root_path="/auth-service",  # Exemplo: ajuste conforme o ambiente/proxy
        title="Auth API",
        description="Authentication and Authorization API",
        openapi_url=API_DOC_JSON,
        redoc_url=API_DOC_REDOC,
        docs_url=API_DOC,
        version=API_VERSION,
    )

    # ... exception handlers e middlewares ...

    create_routes(api, URL_PREFIX)

    return api
```

### Parâmetros do FastAPI

| Parâmetro     | Descrição                                                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `root_path`   | Prefixo de caminho usado quando a API está atrás de um proxy reverso (ex: API Gateway, Nginx). **Este é apenas um exemplo** - ajuste conforme o ambiente de deploy. |
| `title`       | Nome da API exibido na documentação                                                                                                                                 |
| `description` | Descrição da API exibida na documentação                                                                                                                            |
| `version`     | Versão da API                                                                                                                                                       |
| `docs_url`    | URL da documentação Swagger UI                                                                                                                                      |
| `redoc_url`   | URL da documentação ReDoc                                                                                                                                           |
| `openapi_url` | URL do schema OpenAPI (JSON)                                                                                                                                        |

### URLs de Documentação

Com a configuração padrão, as URLs de documentação ficam:

| Documentação | URL             |
| ------------ | --------------- |
| Swagger UI   | `/doc/api`      |
| ReDoc        | `/doc/redoc`    |
| OpenAPI JSON | `/doc/api.json` |

### Sobre o `root_path`

O `root_path` é utilizado quando a API está atrás de um proxy reverso que adiciona um prefixo ao caminho. Por exemplo:

- Se a API está em `https://api.exemplo.com/auth-service/...`
- O proxy reverso roteia `/auth-service/*` para a aplicação
- O `root_path="/auth-service"` garante que a documentação gere URLs corretas

**Importante:** O valor do `root_path` é apenas um exemplo. Deve ser configurado de acordo com o ambiente de deploy (pode vir de uma variável de ambiente).

## Regras Gerais de Código

### Comentários

Evitar comentários no código. Exceções permitidas:

- Comentários de lint (ex: `# noqa`, `# type: ignore`)
- Comentários para coverage (ex: `# pragma: no cover`)
- Comentários para desabilitar regras do pyright/mypy
- Comentários obrigatórios em arquivos `__init__.py`

### Auditoria e Campos Proibidos

- **Proibido** adicionar `updated_at`, `created_by` ou `updated_by` em **qualquer** entidade, DTO, schema, mapper, controller ou response.
- Se for necessário saber **quem** fez uma alteração ou **quando** aconteceu, use **Audit Logs** (entidades `Auditable` + `AuditLog`) e registre a ação nos fluxos de `CREATE`, `UPDATE` e `DELETE`.
- **Nunca** exponha esses campos em responses.
- Em entidades auditáveis, `get_auditable_fields` deve retornar chaves com o **nome exato dos atributos da classe** em `snake_case` (sem labels traduzidas e sem `camelCase`).
- Em entidades auditáveis, `get_auditable_fields` deve conter apenas campos úteis para o usuário final (sem `tenant_id`, `*_id` ou campos internos de infraestrutura).
- Para relacionamentos/FKs, usar a chave relacional no `get_auditable_fields` (ex.: `org_unit`) e retornar valor legível ao usuário (ex.: nome/título/código/matrícula). Se não houver valor legível, omitir o campo.
- Toda entidade auditável deve implementar `get_friendly_fields_mapping` com labels amigáveis em PT-BR; somente chaves presentes nesse mapping entram no `changes`.
- No resultado do log, `changes.field` mantém a chave técnica e `changes.path` contém o nome amigável definido no mapping.
- Não usar `filter_audit_fields` em usecases; passe o payload diretamente para `build_audit_entry`.
- Se um `AuditEntry` não tiver mudanças (`changes` vazio), o repository não deve persistir log.

### Migrations

- **Nunca crie migrations.** A responsabilidade de criar e aplicar migrations é do **usuário**.

### Nomenclatura

**Idioma:** Todo o código deve ser escrito em **inglês** (variáveis, funções, classes, comentários, etc.)

**Padrões de case:**

- **Todo o código:** `snake_case`
- **Schemas de requests e responses:** `camelCase`

**Tabelas no PostgreSQL:** Nomes sempre no **plural**

- `users` (não `user`)
- `roles` (não `role`)
- `order_items` (não `order_item`)

Exemplo de schema com camelCase:

```python
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    username: str
    email: str
    firstName: str  # camelCase
    lastName: str   # camelCase
```

Exemplo de conversão no controller:

```python
def create(self, data: CreateUserRequest):
    dto = CreateUserDTO(
        username=data.username,
        email=data.email,
        first_name=data.firstName,  # Converte camelCase para snake_case
        last_name=data.lastName,
    )
```

### Tipagem Obrigatória em Parâmetros de Métodos

Todos os parâmetros de métodos e funções devem possuir type hints. Nunca deixar um parâmetro sem tipo.

```python
# Correto
def __to_role_response(self, role: Role) -> RoleResponse:
    ...

# Incorreto - parâmetro sem tipo
def __to_role_response(self, role) -> RoleResponse:
    ...
```

### Tipagem de Variáveis

Para variáveis opcionais, usar `Optional[...]` ao invés de `X | None`:

```python
# Correto
from typing import Optional

def find_user_by_email(self, email: str) -> Optional[User]:
    ...

# Incorreto
def find_user_by_email(self, email: str) -> User | None:
    ...
```

### Uso de @overload para Retornos Condicionais

Quando um método pode retornar tipos diferentes baseado em um parâmetro (como `raise_if_is_none`), use `@overload` para que a IDE interprete corretamente o tipo de retorno:

```python
from typing import Optional, Literal, overload

from application.repositories import RepositoryManagerInterface
from application.exceptions import BadRequestError
from domain import User


class FindUserByEmailUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.user_repository = repository_manager.user_repository()

    @overload
    def execute(self, email: str) -> Optional[User]:
        pass

    @overload
    def execute(self, email: str, raise_if_is_none: Literal[True]) -> User:
        pass

    @overload
    def execute(self, email: str, raise_if_is_none: Literal[False]) -> Optional[User]:
        pass

    def execute(self, email: str, raise_if_is_none: bool = False):
        user = self.user_repository.find_user_by_email(email)
        if raise_if_is_none is True and user is None:
            raise BadRequestError("User not found!")
        return user
```

**Benefícios:**

- Quando `raise_if_is_none=True`, a IDE entende que o retorno é `User` (não opcional)
- Quando `raise_if_is_none=False` ou omitido, a IDE entende que o retorno é `Optional[User]`
- Elimina a necessidade de `cast()` no código que chama o usecase

### Schemas de Response — Usar `@dataclass`, não Pydantic

Os schemas de **response** (`*_response.py`) devem utilizar `@dataclass` do módulo `dataclasses`, **nunca** `BaseModel` do Pydantic. O Pydantic é usado apenas nos schemas de **request** (`*_request.py`).

Não usar `class Config`, `from_attributes`, `model_validate` ou qualquer recurso do Pydantic nas responses. Os objetos de response devem ser construídos manualmente no controller.

```python
# Correto — Response com @dataclass
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RoleModuleResponse:
    id: int
    name: str
    url: str
    description: Optional[str] = None

@dataclass
class RoleResponse:
    id: int
    name: str
    description: Optional[str] = None
    modules: List[RoleModuleResponse] = field(default_factory=list)
```

```python
# Incorreto — Response com Pydantic
from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
```

**Construção no controller:** Como não há `model_validate`, os responses devem ser montados manualmente:

```python
def __to_role_response(self, role: Role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        modules=[
            RoleModuleResponse(
                id=module.id,
                name=module.name,
                description=module.description,
                url=module.url,
            )
            for module in (role.modules or [])
        ],
    )
```

### Enums de Requests

Todos os enums utilizados nos **schemas de request** devem ser definidos no arquivo:

`src/api/schemas/enums.py`

Evite criar enums espalhados em outros módulos da API.

### Resposta Padrão de Criação de Entidades

Quando uma entidade for criada, a resposta da requisição deve retornar o `id` da entidade criada. Para isso, deve existir a classe `DefaultCreateResponse` no módulo de schemas da camada API.

Arquivo: `src/api/schemas/default_create_response.py`

```python
from dataclasses import dataclass


@dataclass
class DefaultCreateResponse:
    id: int
```

**Uso no controller:**

```python
from api.schemas import DefaultCreateResponse

class UsersController:
    def create(self, data: CreateUserRequest):
        # ... lógica de criação
        user = CreateUserUseCase(self.repository_manager).execute(dto)
        return DefaultCreateResponse(id=user.id)
```

**Uso no router:**

```python
@router.post("", status_code=HTTPStatus.CREATED, response_model=DefaultCreateResponse)
async def create_user(
    data: CreateUserRequest,
    db_manager: DatabaseManagerConnection = Depends(get_database_manager),
):
    return UsersController(db_manager=db_manager).create(data)
```

### Resposta Padrão de Listagem Paginada

Quando um endpoint retorna dados paginados, a resposta deve usar a classe `PaginatedResponse`. Esta classe é genérica e aceita qualquer tipo de response como parâmetro.

Arquivo: `src/api/schemas/paginated_response.py`

```python
from typing import Generic, TypeVar, List
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class PaginatedResponse(Generic[T]):
    data: List[T]
    count: int
    page: int
```

### DTO PaginatedResult

A classe `PaginatedResult` é o DTO utilizado pelos usecases para retornar resultados paginados ao controller. Ela faz a ponte entre o `DBPaginatedResult` (repository) e o `PaginatedResponse` (API schema).

Arquivo: `src/application/dtos/paginated_result.py`

```python
from typing import Generic, TypeVar, List
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    data: List[T]
    count: int
    page: int
```

### Fluxo Completo de Paginação

O sistema de paginação utiliza três classes distintas, uma para cada camada da arquitetura:

```
Repository (infra)          →  UseCase (application)       →  Controller (api)
DBPaginatedResult[Entity]   →  PaginatedResult[Entity]     →  PaginatedResponse[ResponseDTO]
(data, total_count)            (data, count, page)             (data, count, page)
```

**1. Repository** retorna `DBPaginatedResult[Entity]`:

```python
return DBPaginatedResult(data=data, total_count=total)
```

**2. UseCase** converte `DBPaginatedResult` em `PaginatedResult` (adicionando `page`):

```python
from application.dtos import PaginatedResult

result = self.user_repository.find_all(page, per_page, tenant_id)
return PaginatedResult(data=result.data, count=result.total_count, page=page)
```

**3. Controller** converte `PaginatedResult[Entity]` em `PaginatedResponse[ResponseDTO]` (mapeando entidades para responses):

```python
from api.schemas import PaginatedResponse, UserResponse

result = ListUsersUseCase(self.repository_manager).execute(page, per_page, tenant_id)
return PaginatedResponse(
    data=[self.__to_user_response(user) for user in result.data],
    count=result.count,
    page=result.page,
)
```

**4. Router** declara o `response_model` com `PaginatedResponse[ResponseDTO]`:

```python
from api.schemas import PaginatedResponse, UserResponse

@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[UserResponse],
    dependencies=[require_role("users:read")],
)
async def list_users(
    current_user: CurrentUser,
    db_manager: DBManager,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=100),
):
    return UsersController(db_manager=db_manager).list_all(
        page, perPage, current_user.tenant_id
    )
```

**Formato de resposta JSON:**

```json
{
  "data": [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com"
    }
  ],
  "count": 50,
  "page": 0
}
```

## Arquivos \_\_init\_\_.py

### Comentário Obrigatório

Todo arquivo `__init__.py` deve ter na **primeira linha** o comentário:

```python
# pyright: reportUnusedImport=false
```

### Exportação de Classes

Os arquivos `__init__.py` devem importar e exportar as classes públicas do módulo. Porém, nem todos os módulos exportam classes diretamente.

**Módulos que NÃO exportam classes no \_\_init\_\_.py (apenas marcador de pacote):**

- `src/api/__init__.py`
- `src/application/__init__.py`
- `src/infra/__init__.py`

**Módulos que EXPORTAM classes no \_\_init\_\_.py:**

`src/domain/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .user import User
from .role import Role
```

`src/application/exceptions/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .api_error import APIError
from .bad_request_error import BadRequestError
from .conflict_error import ConflictError
from .not_found_error import NotFoundError
from .access_denied_error import AccessDeniedError
from .unauthorized_error import UnauthorizedError
from .unprocessable_entity_error import UnprocessableEntityError
from .locked_error import LockedError
```

`src/application/dtos/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .paginated_result import PaginatedResult
from .create_user_dto import CreateUserDTO
```

`src/application/repositories/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .repository_manager_interface import RepositoryManagerInterface
from .user_repository_interface import UserRepositoryInterface
from .types import DBPaginatedResult
```

`src/application/repositories/types/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .db_paginated_result import DBPaginatedResult
```

### Classe DBPaginatedResult

Arquivo: `src/application/repositories/types/db_paginated_result.py`

A classe `DBPaginatedResult` é genérica e deve ser utilizada como retorno de todos os métodos de repository que realizam consultas paginadas (ex: `find_all`). Ela substitui o uso de `Tuple[List[Entity], int]`.

```python
from typing import Generic, TypeVar, List
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class DBPaginatedResult(Generic[T]):
    data: List[T]
    total_count: int
```

**Uso no repository (interface):**

```python
from application.repositories.types import DBPaginatedResult

class UserRepositoryInterface(ABC):
    @abstractmethod
    def find_all(
        self, page: int, per_page: int, tenant_id: Optional[int] = None
    ) -> DBPaginatedResult[User]:
        raise NotImplementedError
```

**Uso no repository (implementação):**

```python
def find_all(
    self, page: int, per_page: int, tenant_id: Optional[int] = None
) -> DBPaginatedResult[User]:
    query = self.session.query(User)
    if tenant_id is not None:
        query = query.filter_by(tenant_id=tenant_id)
    total = query.count()
    data = query.offset(page * per_page).limit(per_page).all()
    return DBPaginatedResult(data=data, total_count=total)
```

**Uso no use case:**

```python
result = self.user_repository.find_all(page, per_page, tenant_id)
return PaginatedResult(data=result.data, count=result.total_count, page=page)
```

`src/application/usecases/users/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .create_user_usecase import CreateUserUseCase
from .find_user_by_email_usecase import FindUserByEmailUseCase
```

`src/api/schemas/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .paginated_response import PaginatedResponse
from .create_user_request import CreateUserRequest
from .user_response import UserResponse
from .default_create_response import DefaultCreateResponse
```

`src/api/controllers/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .users_controller import UsersController
```

`src/infra/repositories/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .repository_manager import RepositoryManager
from .user_repository import UserRepository
```

`src/infra/mappers/__init__.py`:

```python
# pyright: reportUnusedImport=false
from sqlalchemy import MetaData
from sqlalchemy.orm import registry
from .mapper_config import import_mappers

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
```

## Estrutura de Pastas e Arquivos

```
src/
├── main.py                              # Entry point (importa app de api)
├── config.py                            # Configurações do ambiente
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── app.py                           # Criação do FastAPI e exception handlers
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── {dominio}_controller.py      # Orquestrador de requisições
│   ├── routers/
│   │   ├── __init__.py                  # Função create_routes
│   │   ├── {dominio}.py                 # Endpoints do domínio
│   │   └── dependencies/
│   │       ├── __init__.py
│   │       ├── get_database_manager.py  # Injeção de dependência do DB
│   │       ├── get_current_user.py      # Obtém usuário autenticado
│   │       ├── current_user.py          # Tipo CurrentUser
│   │       ├── access_token_data.py     # Dados do token de acesso
│   │       ├── role_checker.py          # PermissionChecker e require_role
│   │       └── utils.py                 # DBManager e login_required
│   └── schemas/
│       ├── __init__.py
│       ├── {acao}_{dominio}_request.py  # Modelos Pydantic de entrada
│       ├── {dominio}_response.py        # Dataclasses de saída (@dataclass)
│       ├── default_create_response.py   # Resposta genérica de criação
│       └── paginated_response.py        # Resposta genérica de listagem paginada
├── application/
│   ├── __init__.py
│   ├── dtos/
│   │   ├── __init__.py
│   │   ├── {acao}_{dominio}_dto.py      # Data Transfer Objects
│   │   └── paginated_result.py          # Resultado paginado (DTO de paginação)
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── api_error.py                 # Exceção base
│   │   ├── bad_request_error.py         # 400 BAD_REQUEST
│   │   ├── not_found_error.py           # 404 NOT_FOUND
│   │   ├── unauthorized_error.py        # 401 UNAUTHORIZED
│   │   ├── access_denied_error.py       # 403 FORBIDDEN
│   │   ├── conflict_error.py            # 409 CONFLICT
│   │   ├── unprocessable_entity_error.py # 422 UNPROCESSABLE_ENTITY
│   │   └── locked_error.py              # 423 LOCKED
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── integration_manager_interface.py  # Interface do gerenciador
│   │   └── {tipo}_integration_interface.py   # Interfaces genéricas (queue, cache, etc)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── repository_manager_interface.py  # Interface abstrata
│   │   ├── {dominio}_repository_interface.py
│   │   └── types/
│   │       ├── __init__.py
│   │       └── db_paginated_result.py       # Resultado paginado do banco
│   └── usecases/
│       ├── __init__.py
│       └── {dominio}/
│           ├── __init__.py
│           └── {acao}_{dominio}_usecase.py  # Lógica de negócio
├── domain/
│   ├── __init__.py
│   └── {entidade}.py                    # Entidades de domínio
└── infra/
    ├── __init__.py
    ├── database_manager.py              # Gerenciador de conexão PostgreSQL
    ├── integrations/
    │   ├── __init__.py
    │   ├── integration_manager.py       # Implementação do gerenciador
    │   └── {tipo}_integration.py        # Implementações concretas (queue, cache, etc)
    ├── mappers/
    │   ├── __init__.py                  # mapper_registry e metadata
    │   ├── mapper_config.py             # Função import_mappers
    │   └── {dominio}_mapper.py          # Mapeamento ORM SQLAlchemy
    └── repositories/
        ├── __init__.py
        ├── repository_manager.py        # Implementação concreta
        └── {dominio}_repository.py      # Implementação concreta
```

## Regras de Importação Entre Camadas

As importações devem ocorrer **sempre de fora para dentro** das camadas, nunca o contrário.

### Direção Permitida

```
API Layer → Application Layer → Domain Layer
API Layer → Infrastructure Layer
Infrastructure Layer → Application Layer (apenas interfaces)
Infrastructure Layer → Domain Layer (apenas para mappers)
```

### Importações por Camada

**API Layer** (`src/api/`):

- Pode importar de: `application`, `domain`, `infra`
- Responsável por: controllers, routers, schemas, tratamento de exceções

**Application Layer** (`src/application/`):

- Pode importar de: `domain`
- Pode importar de si mesma: `dtos`, `exceptions`, `repositories` (interfaces)
- Nunca importa de: `api`, `infra`

**Domain Layer** (`src/domain/`):

- Não importa de nenhuma outra camada
- Contém apenas entidades de negócio puras

**Infrastructure Layer** (`src/infra/`):

- Pode importar de: `application` (apenas interfaces), `domain`
- Nunca importa de: `api`

## TYPE_CHECKING para Importação Entre Domínios

Quando uma entidade de domínio precisa referenciar outra entidade, use `TYPE_CHECKING` para evitar importações circulares:

```python
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:  # pragma: no cover
    from .role import Role

class User:
    id: int
    roles: List["Role"]  # String annotation (forward reference)

    def __init__(self, username: str, email: str, first_name: str, last_name: str):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
```

**Regras:**

- Use `TYPE_CHECKING` para importar outras entidades de domínio
- Use string annotations (`"Role"`) nas type hints
- O bloco `TYPE_CHECKING` só é executado em tempo de verificação de tipos, não em runtime

## Referências de Chave Estrangeira nas Entidades de Domínio

**Regra obrigatória:** Toda entidade de domínio que possua uma **chave estrangeira** (`*_id`) referenciando outra entidade de domínio **deve** declarar um atributo de referência para a entidade relacionada, usando `TYPE_CHECKING` para evitar importações circulares.

O nome do atributo de referência deve ser o nome da chave estrangeira **sem o sufixo `_id`**. O tipo deve usar string annotation (forward reference).

### Exemplo

Se a entidade `EmploymentEnrollment` tem `employee_id` (FK para `Employee`), ela **deve** ter também um atributo `employee` do tipo `"Employee"`:

```python
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .employee import Employee
    from .enrollment_assignment import EnrollmentAssignment

class EmploymentEnrollment:
    id: int
    employee_id: int
    enrollment_id: int

    # Referências de FK — obrigatórias
    employee: "Employee"
    assignments: List["EnrollmentAssignment"]

    def __init__(self, employee_id: int, ...):
        self.employee_id = employee_id
        ...
```

### Regras

1. **Para toda FK `xxx_id`**, deve existir um atributo `xxx` do tipo da entidade referenciada
2. **FKs opcionais** (`Optional[int]`) devem ter referência opcional: `xxx: Optional["Entity"]`
3. **Relações one-to-many** (coleções) devem usar `List["Entity"]`
4. **Relações one-to-one** devem usar o tipo da entidade diretamente ou `Optional["Entity"]`
5. **Todas as importações** de entidades referenciadas devem estar dentro do bloco `TYPE_CHECKING`
6. **Os atributos de referência NÃO são passados no `__init__`** — eles são populados pelo ORM (SQLAlchemy) via `relationship()`
7. **O mapper correspondente** (`src/infra/mappers/`) deve configurar a `relationship()` do SQLAlchemy para que o ORM popule o atributo automaticamente

### Mapeamento FK → Atributo

| FK na entidade | Atributo de referência | Tipo |
|---|---|---|
| `employee_id: int` | `employee: "Employee"` | Obrigatório |
| `cost_center_id: Optional[int]` | `cost_center: Optional["CostCenter"]` | Opcional |
| (coleção via FK reversa) | `items: List["Item"]` | Lista |

### Exemplo completo com mapper

**Domínio** (`src/domain/enrollment_assignment.py`):

```python
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .employment_enrollment import EmploymentEnrollment
    from .org_unit import OrgUnit
    from .cost_center import CostCenter

class EnrollmentAssignment:
    id: int
    enrollment_id: int
    org_unit_id: int
    cost_center_id: Optional[int]

    # Referências de FK
    enrollment: "EmploymentEnrollment"
    org_unit: "OrgUnit"
    cost_center: Optional["CostCenter"]

    def __init__(self, enrollment_id: int, org_unit_id: int, ...):
        self.enrollment_id = enrollment_id
        self.org_unit_id = org_unit_id
        ...
```

**Mapper** (`src/infra/mappers/enrollment_assignment_mapper.py`):

```python
from sqlalchemy.orm import relationship

mapper_registry.map_imperatively(
    EnrollmentAssignment,
    enrollment_assignments,
    properties={
        "enrollment": relationship("EmploymentEnrollment"),
        "org_unit": relationship("OrgUnit"),
        "cost_center": relationship("CostCenter"),
    },
)
```

## Função import_mappers

Arquivo: `src/infra/mappers/mapper_config.py`

```python
import importlib
from pathlib import Path


def import_mappers():
    current_dir = Path(__file__).parent

    for file_path in current_dir.glob("*.py"):
        if file_path.name not in ("__init__.py", "mapper_config.py"):
            module_name = f"infra.mappers.{file_path.stem}"
            importlib.import_module(module_name)
```

**Obrigatório:** Esta função deve ser chamada no início de `create_app()` em `src/api/app.py`, antes de qualquer outra operação:

```python
def create_app():
    import_mappers()  # DEVE ser chamado primeiro
    api = FastAPI(...)
```

**Propósito:** Importa dinamicamente todos os mappers SQLAlchemy para registrar os mapeamentos ORM antes da criação da aplicação.

## Função create_routes

Arquivo: `src/api/routers/__init__.py`

```python
import os
from importlib import util
from pathlib import Path
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi

health_router = APIRouter()

@health_router.get("/ping")
def ping():
    return "pong"

def create_routes(app: FastAPI, url_prefix: str):
    # 1. Adiciona endpoint de health check
    app.include_router(health_router, prefix=f"{url_prefix}", tags=["health"])

    # 2. Descobre e carrega routers dinamicamente
    routes_directory = Path(__file__).parent
    for filename in os.listdir(routes_directory):
        if filename.endswith(".py") and filename not in ["__init__.py"]:
            module_name = filename[:-3]
            module_path = f"{routes_directory}/{filename}"

            spec = util.spec_from_file_location(module_name, str(module_path))
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "router"):
                router = getattr(module, "router")
                app.include_router(
                    router,
                    prefix=f"{url_prefix}/{module_name.replace('_', '-')}",
                    tags=[module_name.replace("_", " ").capitalize()],
                )

    # 3. Remove respostas 422 do OpenAPI (validação retorna 400)
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get("paths", {}).items():
            for _, param in method_item.items():
                responses = param.get("responses")
                if "422" in responses:
                    del responses["422"]

    return app
```

**Regras para routers:**

- Cada arquivo de router deve exportar uma variável `router` do tipo `APIRouter`
- O nome do arquivo define o prefixo da URL (underscores convertidos em hífens)
- Exemplo: `users.py` -> `/api/users`

## Conexão com Banco de Dados por Requisição

Cada requisição deve ter sua própria conexão com o banco de dados PostgreSQL.

### DatabaseManagerConnection

Arquivo: `src/infra/database_manager.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from config import HOST_DB, PASSWORD_DB, USER_DB, PORT_DB, NAME_DB

class DatabaseManagerConnection:
    def __init__(self):
        self.connect()

    def connect(self):
        self.url_db = (
            f"postgresql://{USER_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"
        )
        self.engine = create_engine(
            self.url_db, pool_size=25, max_overflow=10
        )
        self.session: scoped_session[Session] = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

    def close_session(self):
        self.session.close()
        self.engine.dispose()

    def commit(self):
        self.session.commit()
```

### Dependency Injection

Arquivo: `src/api/routers/dependencies/get_database_manager.py`

```python
from fastapi import Request
from infra.database_manager import DatabaseManagerConnection

def get_database_manager(request: Request) -> DatabaseManagerConnection:
    db_manager = DatabaseManagerConnection()

    yield db_manager
    db_manager.close_session()
```

### Utilitários de Dependência

Arquivo: `src/api/routers/dependencies/utils.py`

```python
from typing import Annotated
from fastapi import Depends

from infra.database_manager import DatabaseManagerConnection

from .get_current_user import get_current_user
from .get_database_manager import get_database_manager


login_required = Depends(get_current_user)

DBManager = Annotated[DatabaseManagerConnection, Depends(get_database_manager)]
```

**`DBManager`:** Tipo anotado que injeta automaticamente a conexão com banco de dados. As rotas não precisam mais usar `Depends(get_database_manager)` diretamente.

**`login_required`:** Dependência para endpoints que exigem autenticação, mas não validação de permissão específica.

### Uso nos Routers

```python
from api.routers.dependencies.utils import DBManager, login_required

# Endpoint SEM autenticação
@router.get("/public")
async def public_endpoint(db_manager: DBManager):
    return PublicController(db_manager=db_manager).list()

# Endpoint COM autenticação (apenas login, sem permissão específica)
@router.post("", status_code=HTTPStatus.CREATED, dependencies=[login_required])
async def create_item(
    data: CreateItemRequest,
    db_manager: DBManager,
):
    return ItemsController(db_manager=db_manager).create(data)
```

## Sistema de Permissões

O sistema de permissões utiliza o formato `recurso:ação` para controle de acesso granular.

### Formato de Permissões

```
recurso:ação
```

**Exemplos:**

- `users:create` - Permissão para criar usuários
- `users:list` - Permissão para listar usuários
- `users:update` - Permissão para atualizar usuários
- `orders:delete` - Permissão para deletar pedidos

**Wildcards:**

- `users:*` - Todas as permissões do recurso `users`
- `*` - Superadmin (acesso total a todos os recursos)

### PermissionChecker

Arquivo: `src/api/routers/dependencies/role_checker.py`

```python
from typing import List
from fastapi import Depends

from application.exceptions import AccessDeniedError
from .current_user import CurrentUser


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
        self.resource, self.action = required_permission.split(":")

    async def __call__(self, current_user: CurrentUser) -> None:
        if self._has_permission(current_user.roles):
            return

        raise AccessDeniedError("Acccess Denied")

    def _has_permission(self, user_permissions: List[str]) -> bool:
        for permission in user_permissions:
            resource, action = permission.split(":")

            # Superadmin: *
            if resource == "*":
                return True

            # Wildcard no recurso: users:*
            if resource == self.resource and action == "*":
                return True

            # Permissão exata: users:list
            if resource == self.resource and action == self.action:
                return True

        return False


def require_role(permission: str):
    return Depends(PermissionChecker(permission))
```

**Importante:** O `PermissionChecker` **não retorna** o `current_user`. Ele apenas valida se o usuário tem a permissão necessária. Para obter os dados do usuário autenticado, use a dependência `CurrentUser` como parâmetro separado no endpoint.

```python
# INCORRETO - Nunca usar require_role para obter current_user
@router.get("...")
async def my_endpoint(
    current_user: CurrentUser = require_role("users:read"),  # ERRADO!
):
    ...

# CORRETO - require_role nas dependencies, CurrentUser como parâmetro
@router.get(
    "...",
    dependencies=[require_role("users:read")],
)
async def my_endpoint(
    current_user: CurrentUser,  # CORRETO!
    db_manager: DBManager,
):
    ...
```

### Uso com require_role

Quando um endpoint exige validação de permissão específica, use `require_role`:

```python
from http import HTTPStatus
from typing import Optional
from fastapi import APIRouter, Query
from api.routers.dependencies.utils import DBManager
from api.routers.dependencies.role_checker import require_role
from api.routers.dependencies import CurrentUser
from api.schemas import (
    CreateUserRequest,
    DefaultCreateResponse,
    UserResponse,
    PaginatedResponse,
)

@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("users:create")],
)
async def create_user(
    data: CreateUserRequest,
    db_manager: DBManager,
):
    return UsersController(db_manager=db_manager).create(data)


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[UserResponse],
    dependencies=[require_role("users:read")],
)
async def list_users(
    current_user: CurrentUser,
    db_manager: DBManager,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=100),
):
    return UsersController(db_manager=db_manager).list_all(
        page, perPage, current_user.tenant_id
    )
```

### Quando usar cada tipo de autenticação

| Cenário                             | Dependência                                   |
| ----------------------------------- | --------------------------------------------- |
| Endpoint público (sem autenticação) | Nenhuma                                       |
| Apenas autenticação (login)         | `dependencies=[login_required]`               |
| Autenticação + permissão específica | `dependencies=[require_role("recurso:ação")]` |

## Tratamento de Erros de Validação Pydantic

Erros de validação Pydantic devem retornar **status 400** (BAD_REQUEST), não 422.

Arquivo: `src/api/app.py`

```python
from http import HTTPStatus
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@api.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = exc.errors()
    response = {}
    for error in errors:
        key = error["loc"][1]
        response[key] = error["msg"]
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"detail": response},
    )
```

**Formato de resposta:**

```json
{
  "detail": {
    "campo": "mensagem de erro"
  }
}
```

## Sistema de Exceções

### Classe Base APIError

Arquivo: `src/application/exceptions/api_error.py`

```python
from http import HTTPStatus

class APIError(Exception):
    def __init__(self, status_code: HTTPStatus, message: str):
        super().__init__()
        self.status_code = status_code
        self.message = message
```

### Exception Handler

Arquivo: `src/api/app.py`

```python
@api.exception_handler(APIError)
def http_exception_handler(request: Request, error: APIError):
    return JSONResponse(
        content={"detail": error.message},
        status_code=error.status_code
    )
```

### Exceções Customizadas

Todas as exceções customizadas seguem o padrão de lançar `APIError` no `__init__`:

```python
from http import HTTPStatus
from .api_error import APIError

class BadRequestError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.BAD_REQUEST, message)
```

**Exceções disponíveis:**
| Classe | Status Code | HTTP Status |
|--------|-------------|-------------|
| BadRequestError | 400 | BAD_REQUEST |
| UnauthorizedError | 401 | UNAUTHORIZED |
| AccessDeniedError | 403 | FORBIDDEN |
| NotFoundError | 404 | NOT_FOUND |
| ConflictError | 409 | CONFLICT |
| UnprocessableEntityError | 422 | UNPROCESSABLE_ENTITY |
| LockedError | 423 | LOCKED |

### Uso na Camada Application

```python
from application.exceptions import ConflictError, BadRequestError

class CreateUserUseCase:
    def execute(self, data: CreateUserDTO):
        user = self._find_by_email(data.email)
        if user is not None:
            raise ConflictError("A user with this email address already exists.")
        return self.user_repository.create_user(...)
```

## Mapeamento SQLAlchemy (Classical Mapping)

Os mappers usam mapeamento imperativo (classical mapping), não decorators.

Arquivo: `src/infra/mappers/__init__.py`

```python
# pyright: reportUnusedImport=false
from sqlalchemy import MetaData
from sqlalchemy.orm import registry
from .mapper_config import import_mappers

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
```

Arquivo: `src/infra/mappers/{dominio}_mapper.py`

```python
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import relationship

from domain import User
from . import mapper_registry

users = Table(
    "users",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False, index=True),
    Column("email", String, nullable=False, index=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
)

mapper_registry.map_imperatively(
    User,
    users,
    properties={
        "roles": relationship("Roles"),
    },
)
```

## Padrão de Controllers

Os controllers orquestram a chamada de usecases e transformam dados entre schemas e DTOs. O controller **não** é responsável pelo commit - essa responsabilidade é do repository.

**Regra importante:** Controllers **NÃO podem** acessar diretamente métodos dos repositories. O controller deve apenas instanciar o `RepositoryManager` e passá-lo para os usecases. Toda lógica de acesso a dados deve ser feita através dos usecases.

```python
# INCORRETO - Controller acessando repository diretamente
class UsersController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)
        self.user_repository = self.repository_manager.user_repository()  # ERRADO!

    def find_by_email(self, email: str):
        user = self.user_repository.find_user_by_email(email)  # ERRADO!
        ...

# CORRETO - Controller usando usecase
class UsersController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def find_by_email(self, email: str):
        user = FindUserByEmailUseCase(self.repository_manager).execute(
            email=email, raise_if_is_none=True
        )  # CORRETO!
        ...
```

```python
from typing import Optional
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager
from application.dtos import CreateUserDTO
from application.usecases.users import CreateUserUseCase, FindUserByEmailUseCase, ListUsersUseCase
from api.schemas import (
    CreateUserRequest,
    DefaultCreateResponse,
    UserResponse,
    PaginatedResponse,
)
from domain import User

class UsersController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def create(self, data: CreateUserRequest):
        dto = CreateUserDTO(
            username=data.username,
            email=data.email,
            first_name=data.firstName,
            last_name=data.lastName,
        )
        user = CreateUserUseCase(self.repository_manager).execute(dto)
        return DefaultCreateResponse(id=user.id)

    def list_all(
        self, page: int, per_page: int, tenant_id: Optional[int] = None
    ) -> PaginatedResponse[UserResponse]:
        result = ListUsersUseCase(self.repository_manager).execute(
            page, per_page, tenant_id
        )
        return PaginatedResponse(
            data=[self.__to_user_response(user) for user in result.data],
            count=result.count,
            page=result.page,
        )

    def find_by_email(self, email: str):
        # Com @overload no usecase, raise_if_is_none=True retorna User (não Optional)
        user = FindUserByEmailUseCase(self.repository_manager).execute(
            email=email, raise_if_is_none=True
        )
        return self.__to_user_response(user)

    def __to_user_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            firstName=user.first_name,
            lastName=user.last_name,
        )
```

## Padrão de Usecases

Cada usecase deve ter uma única responsabilidade e receber o repository_manager no construtor.

```python
from application.repositories import RepositoryManagerInterface
from application.dtos import CreateUserDTO
from application.exceptions import ConflictError
from domain import User

class CreateUserUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.user_repository = repository_manager.user_repository

    def execute(self, data: CreateUserDTO) -> User:
        existing_user = self.user_repository.find_user_by_email(data.email)
        if existing_user is not None:
            raise ConflictError("A user with this email address already exists.")

        user = User(
            username=data.username,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return self.user_repository.create_user(user)
```

## Padrão de Repositories

### Interface (Application Layer)

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from domain import User
from application.repositories.types import DBPaginatedResult

class UserRepositoryInterface(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self, page: int, per_page: int, tenant_id: Optional[int] = None
    ) -> DBPaginatedResult[User]:
        raise NotImplementedError
```

### Padrão de Listagem Unificado

Cada repository deve ter um único método `find_all()` que centraliza toda a lógica de listagem paginada. Não devem existir métodos separados como `find_paginated`, `find_paginated_by_tenant_id`, etc.

**Regras:**

1. O método `find_all()` recebe `page` e `per_page` como parâmetros obrigatórios
2. Filtros opcionais são adicionados como parâmetros com valor padrão `None`
3. O retorno é sempre `DBPaginatedResult[Entity]` (dados paginados + total). A classe `DBPaginatedResult` está em `src/application/repositories/types/db_paginated_result.py`
4. O método `find_by_id_in()` permanece separado pois serve um propósito diferente (busca em lote por IDs, sem paginação)
5. Quando múltiplos filtros são fornecidos, eles devem ser aplicados cumulativamente (não mutuamente exclusivos)

**Exemplos de assinaturas por complexidade:**

```python
# Sem filtros (ex: TenantRepository)
def find_all(self, page: int, per_page: int) -> DBPaginatedResult[Tenant]

# Com um filtro opcional (ex: UserRepository, ProfileRepository, ModuleRepository)
def find_all(
    self, page: int, per_page: int, tenant_id: Optional[int] = None
) -> DBPaginatedResult[User]

# Com múltiplos filtros opcionais (ex: RoleRepository)
def find_all(
    self, page: int, per_page: int,
    tenant_id: Optional[int] = None,
    module_ids: Optional[List[int]] = None,
) -> DBPaginatedResult[Role]
```

**Implementação na infra (SQLAlchemy):**

```python
from application.repositories.types import DBPaginatedResult

def find_all(
    self, page: int, per_page: int,
    tenant_id: Optional[int] = None,
    module_ids: Optional[List[int]] = None,
) -> DBPaginatedResult[Role]:
    query = self.session.query(Role)

    if tenant_id is not None:
        subquery = (
            self.session.query(modules_roles.c.role_id)
            .join(tenants_modules, modules_roles.c.module_id == tenants_modules.c.module_id)
            .filter(tenants_modules.c.tenant_id == tenant_id)
            .distinct()
            .subquery()
        )
        query = query.filter(Role.id.in_(subquery))

    if module_ids:
        subquery = (
            self.session.query(modules_roles.c.role_id)
            .filter(modules_roles.c.module_id.in_(module_ids))
            .distinct()
            .subquery()
        )
        query = query.filter(Role.id.in_(subquery))

    total = query.count()
    data = query.offset(page * per_page).limit(per_page).all()
    return DBPaginatedResult(data=data, total_count=total)
```

**Use case de listagem:**

```python
from application.repositories import RepositoryManagerInterface
from application.dtos import PaginatedResult
from domain import User

class ListUsersUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.user_repository = repository_manager.user_repository

    def execute(
        self, page: int, per_page: int, tenant_id: Optional[int] = None
    ) -> PaginatedResult[User]:
        result = self.user_repository.find_all(page, per_page, tenant_id)
        return PaginatedResult(data=result.data, count=result.total_count, page=page)
```

### Implementação (Infrastructure Layer)

O repository é responsável pelo commit da transação.

```python
from typing import Optional, List
from application.repositories import UserRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain.user import User
from infra.database_manager import DatabaseManagerConnection

class UserRepository(UserRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection) -> None:
        self.session = db_manager.session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def find_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()

    def find_all(
        self, page: int, per_page: int, tenant_id: Optional[int] = None
    ) -> DBPaginatedResult[User]:
        query = self.session.query(User)
        if tenant_id is not None:
            query = query.filter_by(tenant_id=tenant_id)
        total = query.count()
        data = query.offset(page * per_page).limit(per_page).all()
        return DBPaginatedResult(data=data, total_count=total)
```

## Padrão de Integrations

O módulo de integrations segue o mesmo padrão do RepositoryManager, permitindo integração com serviços externos como filas (SQS, RabbitMQ), cache (Redis), APIs externas, etc.

### Princípios

1. **Interfaces genéricas:** As interfaces devem ter nomes genéricos para permitir troca de tecnologias sem impacto nos usecases
2. **Inversão de dependência:** Usecases conhecem apenas as interfaces (application layer), não as implementações (infra layer)
3. **Injeção via controller:** O IntegrationManager deve ser instanciado no controller e injetado no usecase

**Exemplos de nomes de interfaces:**

- `QueueIntegrationInterface` (não `SqsIntegrationInterface` ou `RabbitMqIntegrationInterface`)
- `CacheIntegrationInterface` (não `RedisIntegrationInterface`)
- `LogIntegrationInterface`
- `PaymentGatewayIntegrationInterface`
- `NotificationIntegrationInterface`

### Interface IntegrationManager (Application Layer)

Arquivo: `src/application/integrations/integration_manager_interface.py`

```python
from abc import ABC, abstractmethod
from .queue_integration_interface import QueueIntegrationInterface


class IntegrationManagerInterface(ABC):

    @abstractmethod
    def queue_integration(self) -> QueueIntegrationInterface:
        raise NotImplementedError("Should implement method: queue_integration")
```

### Interface de Integração (Application Layer)

Arquivo: `src/application/integrations/queue_integration_interface.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any


class QueueIntegrationInterface(ABC):

    @abstractmethod
    def send_email(self, message_body: Dict[str, Any]) -> None:
        raise NotImplementedError
```

### Implementação IntegrationManager (Infrastructure Layer)

Arquivo: `src/infra/integrations/integration_manager.py`

```python
from application.integrations import IntegrationManagerInterface, QueueIntegrationInterface
from .queue_integration import QueueIntegration


class IntegrationManager(IntegrationManagerInterface):
    def __init__(self):
        self._queue_integration = None

    def queue_integration(self) -> QueueIntegrationInterface:
        if self._queue_integration is None:
            self._queue_integration = QueueIntegration()
        return self._queue_integration
```

### Uso no Controller

Quando um usecase precisa de integrações externas, o controller deve instanciar o IntegrationManager e injetá-lo:

```python
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager
from infra.integrations import IntegrationManager
from application.usecases.users import CreateUserWithNotificationUseCase

class UsersController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)
        self.integration_manager = IntegrationManager()

    def create_with_notification(self, data: CreateUserRequest):
        dto = CreateUserDTO(...)
        user = CreateUserWithNotificationUseCase(
            repository_manager=self.repository_manager,
            integration_manager=self.integration_manager,
        ).execute(dto)
        return DefaultCreateResponse(id=user.id)
```

### Uso no Usecase

O usecase recebe a interface do IntegrationManager, não a implementação concreta:

```python
from application.repositories import RepositoryManagerInterface
from application.integrations import IntegrationManagerInterface
from application.dtos import CreateUserDTO
from domain import User


class CreateUserWithNotificationUseCase:
    def __init__(
        self,
        repository_manager: RepositoryManagerInterface,
        integration_manager: IntegrationManagerInterface,
    ):
        self.user_repository = repository_manager.user_repository()
        self.queue_integration = integration_manager.queue_integration()

    def execute(self, data: CreateUserDTO) -> User:
        user = User(
            username=data.username,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        created_user = self.user_repository.create_user(user)

        # Enviar notificação via fila
        self.queue_integration.send_email({
            "to": user.email,
            "subject": "Welcome!",
            "body": f"Hello {user.first_name}!",
        })

        return created_user
```

### **init**.py das Integrations

`src/application/integrations/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .integration_manager_interface import IntegrationManagerInterface
from .queue_integration_interface import QueueIntegrationInterface
```

`src/infra/integrations/__init__.py`:

```python
# pyright: reportUnusedImport=false
from .integration_manager import IntegrationManager
from .queue_integration import QueueIntegration
```

## Configurações de Ambiente

Arquivo: `src/config.py`

```python
from typing import Literal, cast
from decouple import config
from dotenv import load_dotenv, find_dotenv

ENVIRONMENT: Literal["HML", "PRD", "local", "test"] = cast(
    Literal["HML", "PRD", "local", "test"], config("ENVIRONMENT", default="local")
)
dotenv = find_dotenv(f".env.{ENVIRONMENT.lower()}")
load_dotenv(dotenv)

USER_DB = config("USER_DB", default=None)
PASSWORD_DB = config("PASSWORD_DB", default=None)
HOST_DB = config("HOST_DB", default=None)
NAME_DB = config("NAME_DB", default=None)
PORT_DB = config("PORT_DB", default=None)
```

Arquivos de ambiente: `.env.local`, `.env.hml`, `.env.prd`, `.env.test`

### Variáveis de Ambiente para Autenticação JWT e Tenancy

As seguintes variáveis são **obrigatórias** para o funcionamento de autenticação e validação de tenant:

| Variável           | Descrição                                                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `JWT_SECRET_KEY`   | Chave secreta para assinar e decodificar o **access token**. Deve ser uma string segura e única.                              |
| `SYSTEM_TENANT_ID` | ID do tenant de sistema. Quando `current_user.tenant_id == SYSTEM_TENANT_ID`, o endpoint pode respeitar o `tenantId` enviado. |

Exemplo de definição nos arquivos `.env.*`:

```env
JWT_SECRET_KEY=uma_chave_segura
SYSTEM_TENANT_ID=1
```

Trecho correspondente em `src/config.py`:

```python
JWT_SECRET_KEY = cast(str, config("JWT_SECRET_KEY"))
SYSTEM_TENANT_ID = int(config("SYSTEM_TENANT_ID", cast=int))
```

## Autenticação JWT

### Estrutura do Access Token

O access token é um JWT que contém as seguintes informações no payload:

```python
{
    "sessionId": int,      # ID da sessão ativa
    "uid": int,            # ID do usuário
    "roles": List[str],    # Lista de permissões (ex: ["users:list", "users:create"])
    "email": str,          # Email do usuário
    "username": str,       # Username do usuário
    "validated": bool,     # Se o usuário foi validado
    "tenantId": int,       # ID do tenant
}
```

### Obtendo Dados do Usuário Autenticado

#### Tipo `CurrentUser`

Arquivo: `src/api/routers/dependencies/current_user.py`

`CurrentUser` é um tipo anotado que injeta automaticamente os dados do usuário autenticado via `Depends(get_current_user)`. Ao declarar um parâmetro com esse tipo, o FastAPI extrai e valida o JWT do header `Authorization` e retorna uma instância de `AccessTokenData`.

```python
from typing import Annotated
from fastapi import Depends

from .get_current_user import get_current_user, AccessTokenData


CurrentUser = Annotated[AccessTokenData, Depends(get_current_user)]
```

**Uso nos endpoints:**

```python
from api.routers.dependencies import CurrentUser

@router.get("/meu-endpoint")
async def meu_endpoint(current_user: CurrentUser):
    # current_user é uma instância de AccessTokenData
    user_id = current_user.user_id
    email = current_user.email
    username = current_user.username
    roles = current_user.roles
    tenant_id = current_user.tenant_id
    validated = current_user.validated
    session_id = current_user.session_id

    return {"user_id": user_id}
```

**Importante:** `CurrentUser` é a forma padrão de obter os dados do usuário autenticado. Nunca usar `require_role` para esse propósito — `require_role` serve apenas para validar permissões via `dependencies=[...]`.

#### Estrutura do `AccessTokenData`

Arquivo: `src/api/routers/dependencies/access_token_data.py`

```python
@dataclass
class AccessTokenData:
    session_id: int
    user_id: int
    roles: List[str]
    username: str
    validated: bool
    tenant_id: int
    email: Optional[str]
```

#### Função `get_current_user`

A função que extrai e valida o token está em `src/api/routers/dependencies/get_current_user.py`:

```python
def get_current_user(request: Request) -> AccessTokenData:
    authorization = request.headers.get("Authorization")

    if authorization is None:
        raise UnauthorizedError("Authorization header is missing")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid authorization header format")

    token = parts[1]

    try:
        payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=["HS256"])

        return AccessTokenData(
            session_id=payload["sessionId"],
            user_id=payload["uid"],
            roles=payload["roles"],
            email=payload["email"],
            username=payload["username"],
            validated=payload["validated"],
            tenant_id=payload["tenantId"],
        )

    except ExpiredSignatureError:
        raise UnauthorizedError("Access Token is expired")
    except InvalidSignatureError:
        raise UnauthorizedError("Invalid Access Token")
    except (ValueError, KeyError, DecodeError):
        raise UnauthorizedError("Invalid Access Token")
```

### Validação de Tenant com `resolve_tenant_id`

Arquivo: `src/api/routers/dependencies/tenancy.py`

Use esta dependência em endpoints onde existe validação de tenant com possibilidade de `tenantId` opcional (normalmente listagens e buscas).

```python
from typing import Optional

from config import SYSTEM_TENANT_ID
from api.routers.dependencies.access_token_data import AccessTokenData


def resolve_tenant_id(
    current_user: AccessTokenData, tenant_id: Optional[int]
) -> Optional[int]:
    if current_user.tenant_id == SYSTEM_TENANT_ID:
        return tenant_id
    return current_user.tenant_id
```

Dependências do `resolve_tenant_id`:

- `current_user: AccessTokenData` (obtido via `CurrentUser`, com `tenant_id` vindo do JWT)
- `SYSTEM_TENANT_ID` (variável de ambiente carregada em `src/config.py`)
- `tenantId` do endpoint (`Optional[int]`, query param)

Regra de negócio aplicada:

- Se o usuário **não** é tenant de sistema, sempre usar `current_user.tenant_id` (ignora `tenantId` da query)
- Se o usuário **é** tenant de sistema (`current_user.tenant_id == SYSTEM_TENANT_ID`), usar o `tenantId` informado na query (ou `None` se não informado)

Import recomendado no router:

```python
from api.routers.dependencies import CurrentUser, DBManager, require_role, resolve_tenant_id
```

Exemplo de uso em endpoint de listagem/busca:

```python
from typing import Optional
from http import HTTPStatus
from fastapi import APIRouter

from api.controllers import EmployeesController
from api.schemas import EmployeeResponse, PaginatedResponse
from api.routers.dependencies import CurrentUser, DBManager, require_role, resolve_tenant_id

router = APIRouter()


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[EmployeeResponse],
    dependencies=[require_role("employees:read")],
)
async def list_employees(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = 0,
    perPage: int = 20,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return EmployeesController(db_manager=db_manager, access_token=current_user).list(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
    )
```

Exemplo em endpoint sem override de tenant (create/update/get por ID):

```python
@router.put(
    "/{employeeId}",
    status_code=HTTPStatus.OK,
    dependencies=[require_role("employees:write")],
)
async def update_employee(
    employeeId: int,
    data: UpdateEmployeeRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return EmployeesController(db_manager=db_manager, access_token=current_user).update(
        employeeId, data, current_user.tenant_id
    )
```

Padrão de assinatura em controller/usecase para listagens:

```python
# controller
def list(
    self,
    requester_tenant_id: Optional[int],
    page: int,
    per_page: int,
) -> PaginatedResponse[EmployeeResponse]:
    ...

# usecase
def execute(
    self,
    page: int,
    per_page: int,
    tenant_id: Optional[int],
) -> PaginatedResult[Employee]:
    ...
```

## Resumo das Regras Principais

1. **Importações sempre de fora para dentro** - API -> Application -> Domain
2. **TYPE_CHECKING para importações entre domínios** - Evita dependências circulares
3. **import_mappers() deve ser chamado primeiro** em create_app()
4. **create_routes() carrega routers automaticamente** - Basta criar arquivo com variável `router`
5. **Uma conexão de banco por requisição** - Usando Depends e yield
6. **Erros de validação retornam 400** - Não 422
7. **Exceções na application layer usam classes de exceptions/** - Que herdam de APIError
8. **Classical mapping no SQLAlchemy** - Não usar decorators
9. **Controllers orquestram, Usecases executam lógica** - Separação clara de responsabilidades
10. **Repositories têm interface na application e implementação na infra** - Inversão de dependência
11. **Commit é responsabilidade do repository** - Não do controller ou usecase
12. **Evitar comentários** - Exceto para lint, coverage ou pyright
13. **Código em inglês** - Toda nomenclatura deve ser em inglês
14. **snake_case no código, camelCase nos schemas** - Requests e responses usam camelCase
15. **Tabelas no PostgreSQL no plural** - users, roles, order_items
16. **Usar Optional[X] para tipos opcionais** - Não usar X | None
17. **Criação de entidade retorna id** - Usar DefaultCreateResponse
18. **\_\_init\_\_.py com pyright na primeira linha** - `# pyright: reportUnusedImport=false`
19. **\_\_init\_\_.py exportam classes dos módulos** - Exceto api/, application/ e infra/ raiz
20. **Controllers não acessam repositories diretamente** - Apenas instanciam RepositoryManager e passam para usecases
21. **Usar DBManager para injeção de dependência do banco** - Não usar Depends(get_database_manager) diretamente nos routers
22. **Usar login_required para autenticação sem permissão específica** - dependencies=[login_required]
23. **Usar require_role para validação de permissões** - dependencies=[require_role("recurso:ação")]
24. **Formato de permissões: recurso:ação** - Ex: users:create, orders:list
25. **Usar @overload para retornos condicionais** - Quando tipo de retorno depende de parâmetro booleano
26. **Integrations seguem o mesmo padrão de repositories** - Interface na application, implementação na infra
27. **Interfaces de integração com nomes genéricos** - QueueIntegrationInterface, não SqsIntegrationInterface
28. **Logs de auditoria apenas em entidades especificadas** - Não adicionar audit logs em entidades que não foram explicitamente solicitadas
29. **`audit_entity_type` sempre minúsculo** - Ex: `"user"`, `"profile"`, nunca `"User"` ou `"Profile"`
30. **`build_audit_entry` deve ser chamado ANTES de alterar a entidade** - Para capturar o estado antigo corretamente (exceto em CREATE, onde é chamado após o create para ter o id)
31. **Schemas de response usam `@dataclass`** - Nunca usar Pydantic (`BaseModel`) em responses, apenas em requests
32. **Todos os parâmetros de métodos devem ter type hints** - Nunca deixar parâmetros sem tipo definido
33. **Repositories paginados retornam `DBPaginatedResult[Entity]`** - Nunca retornar `Tuple[List[Entity], int]`, usar `DBPaginatedResult` de `application.repositories.types`
34. **Documentacao de APIs obrigatoria** - Toda alteracao que impactar a interface de uma API deve ser refletida no respectivo arquivo `apis/{NomeDominio}.md`. Novos modulos de routers exigem criacao de novo arquivo de documentacao
35. **`get_auditable_fields` usa nomes reais de atributos** - As chaves devem ser os atributos da entidade em `snake_case` (ex.: `start_date`, `job_functions`), nunca labels traduzidas
36. **`get_friendly_fields_mapping` é obrigatório e em PT-BR** - O método define os campos permitidos no log e o nome amigável exibido em `changes.path`
37. **Não auditar IDs/FKs técnicas e campos internos** - Não incluir `tenant_id`, `*_id`, `storage_key`, checksums e outros campos técnicos no `get_auditable_fields`
38. **Para relacionamentos, auditar valor legível** - Preferir `name`/`title`/`code`/`matricula` da entidade relacionada; se não houver valor legível, omitir o campo
39. **Não usar `filter_audit_fields` nos usecases** - O filtro de campos auditáveis já é aplicado em `build_audit_entry` via `get_friendly_fields_mapping`
40. **Não persistir audit log sem mudanças** - `save_from_entry` deve retornar `None` quando `changes` estiver vazio
41. **Referências de FK obrigatórias nas entidades de domínio** - Toda FK `xxx_id` deve ter um atributo `xxx` do tipo da entidade referenciada, usando `TYPE_CHECKING` para importação e string annotation para tipagem. O mapper deve configurar a `relationship()` correspondente
42. **Cada entidade deve ter seus próprios endpoints** - Entidades distintas (ex.: Employee e Person) devem ser tratadas em endpoints separados, mesmo que compartilhem o mesmo módulo de rotas. Nunca misturar campos de entidades diferentes em um mesmo endpoint de criação ou atualização. Cada entidade deve ter seus próprios usecases, DTOs, schemas de request/response e controller (ou métodos de controller separados). Na criação, se uma entidade depende de outra, os dados da entidade dependente podem ser enviados como objeto aninhado no request, mas a lógica de cada entidade deve estar em usecases distintos. Na atualização, cada entidade deve ter seu próprio endpoint de PUT. No response, entidades relacionadas devem ser retornadas como objetos aninhados (ex.: `person` dentro de `EmployeeResponse`), nunca achatadas no mesmo nível
43. **Validação de tenant em listagens deve usar `resolve_tenant_id`** - Quando houver `tenantId` opcional no endpoint, resolver o tenant efetivo via `resolve_tenant_id(current_user, tenantId)` e repassar `Optional[int]` para controller/usecase/repository

## Documentacao de APIs (pasta `apis/`)

O projeto mantem documentacao detalhada de todas as APIs na pasta `apis/` na raiz do projeto. Essa documentacao serve como referencia para o frontend e demais consumidores do servico.

### Regra Obrigatoria

**Toda alteracao que impactar a interface de uma API deve ser refletida no respectivo arquivo dentro da pasta `apis/`.** Isso inclui:

- Adicionar, remover ou renomear campos de request ou response
- Alterar regras de validacao ou obrigatoriedade de campos
- Adicionar, remover ou alterar endpoints
- Alterar status codes de resposta
- Alterar mensagens de erro
- Alterar regras de negocio que afetem o comportamento da API
- Alterar filtros de listagem ou busca

### Quando criar um novo arquivo

Criar um novo arquivo `apis/{NomeDominio}.md` sempre que um **novo modulo de routers** for criado. O nome do arquivo deve seguir o padrao PascalCase do dominio (ex: `Employees.md`, `CostCenter.md`, `EnrollmentAssignments.md`).

### Quando atualizar um arquivo existente

Atualizar o arquivo correspondente em `apis/` sempre que:

1. **Um endpoint for adicionado ou removido** do router
2. **Um campo for adicionado ou removido** de um request ou response schema
3. **Uma regra de negocio for alterada** em um usecase que afete o comportamento visivel da API
4. **Um filtro de listagem for adicionado ou removido**
5. **Um status code ou mensagem de erro for alterado**
6. **Um relacionamento entre dominios for alterado** de forma que impacte os dados retornados ou aceitos pela API

### Estrutura padrao do arquivo

Cada arquivo de documentacao deve conter:

```markdown
# {Nome do Dominio} API

Base path: `/{rota-base}`

Permissoes:
- `{recurso}:write` para criar, atualizar e deletar.
- `{recurso}:read` para obter, listar e historico.

Observacoes de tenant:
- O parametro `tenantId` e opcional e segue o padrao do servico (via `resolve_tenant_id`).

Regras gerais:
- (regras de negocio gerais do dominio)

---

## POST /{rota-base}
(descricao, request body com tabela de campos, response, erros comuns)

## GET /{rota-base}/{id}
(descricao, path params, response com exemplo JSON, erros comuns)

## GET /{rota-base}
(descricao, query params com tabela, regras de filtro, response)

## PUT /{rota-base}/{id}
(descricao, path params, request body com tabela, response, erros comuns)

## DELETE /{rota-base}/{id}
(descricao, path params, response, erros comuns)

## GET /{rota-base}/{id}/history
(descricao, path params, response com exemplo JSON)
```

### Conteudo obrigatorio por endpoint

Para cada endpoint documentado, incluir:

| Item | Descricao |
|------|-----------|
| **Metodo e rota** | `POST /rota`, `GET /rota/{id}`, etc. |
| **Descricao** | O que o endpoint faz |
| **Path params** | Parametros de caminho (quando aplicavel) |
| **Query params** | Tabela com nome, tipo, obrigatoriedade, default e descricao (quando aplicavel) |
| **Request body** | Tabela com nome do campo, tipo, obrigatoriedade e descricao (quando aplicavel) |
| **Response** | Status code, nome do schema e exemplo JSON |
| **Regras de filtro** | Como os filtros se comportam (LIKE, igualdade, OR, AND) (quando aplicavel) |
| **Erros comuns** | Lista de status codes e mensagens de erro possiveis |

### Exemplos de arquivos existentes

Consulte os arquivos na pasta `apis/` para referencia:

- `apis/Employees.md` - Funcionarios (com sub-rotas de endereco)
- `apis/EmploymentEnrollments.md` - Vinculos empregatícios
- `apis/EnrollmentAssignments.md` - Lotacao (movimentacao funcional)
- `apis/costCenter.md` - Centros de custo
- `apis/JobPosition.md` - Cargos

### Idioma

A documentacao de APIs deve ser escrita em **portugues** (sem acentos), pois serve como referencia para o time de frontend.

## Sistema de Logs de Auditoria (Audit Logs)

Para detalhes completos sobre o sistema de auditoria, consulte o arquivo [claude/auditLog.md](claude/auditLog.md).
