# Sistema de Logs de Auditoria (Audit Logs)

O sistema de auditoria registra alterações realizadas em entidades do sistema, permitindo rastrear **quem** fez **o quê** e **quando**. Os logs são gravados apenas em operações de **escrita** no banco de dados: `INSERT`, `UPDATE` e `DELETE`.

**Importante:** Nem todas as entidades possuem logs de auditoria. Os logs devem ser adicionados **apenas nas entidades em que for explicitamente solicitado**. Se não foi especificado que uma entidade deve ter auditoria, ela não deve ter.

## Regra Obrigatória: Sem Campos de Auditoria nas Entidades

- **Proibido** adicionar `updated_at`, `created_by` ou `updated_by` em entidades, DTOs, schemas, mappers, controllers ou responses.
- Para rastrear **quem** fez a ação e **quando** ela ocorreu, **use Audit Logs** (`Auditable` + `AuditLog`) e registre a ação nos fluxos de `CREATE`, `UPDATE` e `DELETE`.

## Estrutura de Pastas

```
src/domain/
├── audit_log.py                    # Entidade AuditLog (mapeada para tabela audit_logs)
└── history/
    ├── __init__.py                 # Exporta AuditEntry, Auditable, FieldChange, ChangeType
    ├── audit_entry.py              # Dataclass AuditEntry (entrada padronizada)
    ├── auditable.py                # Mixin ABC Auditable (classe base para entidades auditáveis)
    ├── field_change.py             # Dataclass FieldChange (mudança individual de campo)
    └── change_type.py              # Enum ChangeType (tipos de valor)
```

## Módulos do Core de Auditoria

### `src/domain/history/change_type.py` — Enum de tipos de valor

```python
from enum import Enum

class ChangeType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    OBJECT = "object"
    DATE = "date"
    NULL = "null"
```

### `src/domain/history/field_change.py` — Mudança individual de campo

```python
from dataclasses import dataclass
from typing import Any, Dict
from datetime import datetime
from .change_type import ChangeType

@dataclass
class FieldChange:
    field: str          # Nome do campo (ex: "email", "city")
    path: str           # Caminho completo (ex: "email", "address.city")
    old_value: Any      # Valor anterior
    new_value: Any      # Novo valor
    value_type: ChangeType  # Tipo do valor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "path": self.path,
            "oldValue": self._serialize_value(self.old_value),
            "newValue": self._serialize_value(self.new_value),
            "valueType": self.value_type.value,
        }

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
```

### `src/domain/history/audit_entry.py` — Entrada de auditoria padronizada

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal
from datetime import datetime
from .field_change import FieldChange

@dataclass
class AuditEntry:
    entity_type: str
    entity_id: Any
    action: Literal["CREATE", "UPDATE", "DELETE"]
    description: str
    agent_username: str
    timestamp: datetime
    changes: List[FieldChange] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entityType": self.entity_type,
            "entityId": self.entity_id,
            "action": self.action,
            "description": self.description,
            "agentUserEmail": self.agent_username,
            "timestamp": self.timestamp.isoformat(),
            "changes": [c.to_dict() for c in self.changes],
        }
```

## Descrição dos Logs (campo `description`)

O campo `description` é exibido para usuários e **sempre** deve estar em **português (PT-BR)**.

Regras práticas:
- Use frases curtas e objetivas, com verbo no passado: **"Criação de ..."**, **"Atualização de ..."**, **"Exclusão de ..."**.
- Mencione o nome da entidade em português (evite termos em inglês).
- Para ações específicas, deixe explícito o que ocorreu.

Exemplos:
- "Criação de unidade organizacional"
- "Atualização da unidade organizacional atual do vínculo empregatício"
- "Desativação automática de dependente do funcionário"

### `src/domain/history/auditable.py` — Mixin para entidades auditáveis

Esta é a classe base abstrata que toda entidade auditável deve herdar. Ela fornece o método `build_audit_entry` que compara o estado antigo com o novo e gera automaticamente a lista de mudanças.

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Literal, Union
from .audit_entry import AuditEntry

class Auditable(ABC):

    @property
    @abstractmethod
    def audit_entity_type(self) -> str:
        """Nome da entidade para auditoria (sempre minúsculo)."""
        raise NotImplementedError

    @property
    @abstractmethod
    def audit_entity_id(self) -> int:
        """ID da entidade."""
        raise NotImplementedError

    @abstractmethod
    def get_auditable_fields(self) -> Dict[str, Any]:
        """Retorna dict com campos auditáveis e seus valores atuais."""
        raise NotImplementedError

    @abstractmethod
    def get_friendly_fields_mapping(self) -> Dict[str, str]:
        """Mapeia chave técnica -> nome amigável exibido em changes.path."""
        raise NotImplementedError

    def build_audit_entry(
        self,
        new_state: Union["Auditable", Dict[str, Any]],
        action: Literal["CREATE", "UPDATE", "DELETE"],
        description: str,
        agent_username: str,
    ) -> AuditEntry:
        """Constrói entrada de auditoria comparando estados.

        Args:
            new_state: Outra instância Auditable OU dict parcial com campos alterados.
            action: CREATE, UPDATE ou DELETE
            description: Descrição legível da ação
            agent_username: Username de quem realizou a ação

        Comportamento:
            - CREATE: salva apenas newValue (oldValue = None)
            - UPDATE: salva apenas campos que mudaram
            - DELETE: salva apenas oldValue (newValue = None)
            - Campos fora de get_friendly_fields_mapping são ignorados
        """
        ...
```

**Importante sobre `new_state`:**
- Para `CREATE`: passe a própria entidade (`self`) como `new_state`
- Para `UPDATE` com dict parcial: passe `{"campo": novo_valor}` — o método faz merge com o estado atual e detecta diferenças
- Para `UPDATE` com entidade completa: passe a entidade com os novos valores
- Para `DELETE`: passe a própria entidade como `new_state`
- Não use `filter_audit_fields` no usecase: o filtro por campos auditáveis já ocorre dentro de `build_audit_entry` via `get_friendly_fields_mapping`

### Regras Obrigatórias para `get_auditable_fields` e `get_friendly_fields_mapping`

**O que deve ser feito:**
- `get_auditable_fields` deve retornar apenas campos úteis para o usuário final.
- As chaves de `get_auditable_fields` devem ser os nomes reais dos atributos da classe (`snake_case`).
- `get_friendly_fields_mapping` deve mapear essas chaves para nomes amigáveis em **PT-BR**, sem termos técnicos.
- As chaves existentes em `get_auditable_fields` e `get_friendly_fields_mapping` devem ser consistentes entre si.

**Como fazer (especialmente para FKs):**
- Para relacionamento, use a chave relacional (ex.: `org_unit`, `employee`, `salary_band`) e não a FK técnica (`org_unit_id`, `employee_id`, `salary_band_id`).
- Retorne valores primitivos legíveis no `get_auditable_fields` (ex.: `name`, `title`, `code`, `matricula`), nunca o objeto inteiro.
- Se não houver valor legível para o usuário final na entidade relacionada, não inclua esse campo no log.

**O que não deve ser feito:**
- Não incluir `tenant_id`, `*_id`, `storage_key`, checksums ou outros campos técnicos/internos no `get_auditable_fields`.
- Não usar labels traduzidas como chave no `get_auditable_fields`.
- Não usar labels técnicas em inglês no `get_friendly_fields_mapping` quando houver equivalente amigável em PT-BR.

### `src/domain/audit_log.py` — Entidade mapeada para o banco

```python
from typing import Any, Dict, List, Optional
from datetime import datetime

class AuditLog:
    id: int
    entity_type: str
    entity_id: int
    action: str
    description: str
    agent_username: str
    changes: List[Dict[str, Any]]
    created_at: datetime

    def __init__(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        description: str,
        agent_username: str,
        changes: List[Dict[str, Any]],
        created_at: Optional[datetime] = None,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.action = action
        self.description = description
        self.agent_username = agent_username
        self.changes = changes
        self.created_at = created_at or datetime.now()
```

## Mapper da Tabela `audit_logs`

Arquivo: `src/infra/mappers/audit_log_mapper.py`

```python
from sqlalchemy import Table, Column, String, DateTime, Index, BigInteger, Integer
from sqlalchemy.dialects.postgresql import JSONB
from domain import AuditLog
from . import mapper_registry

audit_logs = Table(
    "audit_logs",
    mapper_registry.metadata,
    Column("id", BigInteger, primary_key=True),
    Column("entity_type", String(50), nullable=False),
    Column("entity_id", Integer, nullable=False),
    Column("action", String(10), nullable=False),
    Column("description", String(255), nullable=False),
    Column("agent_username", String(255), nullable=False, index=True),
    Column("changes", JSONB, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

Index("idx_audit_entity_lookup", audit_logs.c.entity_type, audit_logs.c.entity_id)

mapper_registry.map_imperatively(AuditLog, audit_logs)
```

## Repository de Audit Logs

**Interface** (`src/application/repositories/audit_log_repository_interface.py`):

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from domain import AuditLog
from domain.history import AuditEntry

class AuditLogRepositoryInterface(ABC):

    @abstractmethod
    def create(self, audit_log: AuditLog) -> AuditLog:
        raise NotImplementedError

    @abstractmethod
    def save_from_entry(self, audit_entry: AuditEntry) -> Optional[AuditLog]:
        raise NotImplementedError

    @abstractmethod
    def find_by_entity(self, entity_type: str, entity_id: int) -> List[AuditLog]:
        raise NotImplementedError
```

**Implementação** (`src/infra/repositories/audit_log_repository.py`):

O método `save_from_entry` converte um `AuditEntry` (gerado pelo `build_audit_entry`) em `AuditLog` e persiste no banco.
Se `audit_entry.changes` estiver vazio, ele retorna `None` e **não persiste** log.

O método `find_by_entity` busca todos os logs de uma entidade específica, ordenados por data decrescente.

## Como Tornar uma Entidade Auditável

**Passo 1:** A entidade deve herdar de `Auditable`:

```python
from typing import Any, Dict, Optional, TYPE_CHECKING
from .history import Auditable

if TYPE_CHECKING:  # pragma: no cover
    from .employee import Employee

class Profile(Auditable):
    id: int
    employee: Optional["Employee"]

    def __init__(self, name: str, employee: Optional["Employee"] = None):
        self.name = name
        self.employee = employee

    @property
    def audit_entity_type(self) -> str:
        return "profile"  # SEMPRE minúsculo

    @property
    def audit_entity_id(self) -> int:
        return self.id

    def get_friendly_fields_mapping(self) -> Dict[str, str]:
        return {
            "name": "Nome",
            "employee": "Funcionário",
        }

    def get_auditable_fields(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "employee": (
                self.employee.person.full_name
                if hasattr(self.employee, "person")
                and self.employee.person is not None
                and hasattr(self.employee.person, "full_name")
                else None
            ),
        }
```

**Observações sobre `get_auditable_fields`:**
- Retorne apenas campos que devem ser rastreados (nunca inclua senhas ou tokens)
- As chaves devem ser **exatamente** os nomes dos atributos da entidade, em `snake_case`
- Não use labels traduzidas nas chaves (ex.: `"Nome"`, `"Data de Início"`) e não use `camelCase`
- Para relações (ex.: `employee`, `org_unit`, `salary_band`), use o nome do atributo relacional e retorne valores legíveis para o usuário (ex.: nome/título/código/matrícula), não objetos
- Não inclua FKs técnicas (`*_id`, `tenant_id`) e nem campos internos/infra no log
- Se não houver um valor legível no relacionamento, não inclua o campo
- Para campos aninhados, use notação de ponto com nomes reais dos atributos: `"address.city": self.address.city`
- Toda entidade auditável deve implementar `get_friendly_fields_mapping` com labels amigáveis em PT-BR
- Apenas campos presentes no `get_friendly_fields_mapping` serão incluídos em `changes`

## Como Usar nos Use Cases

### CREATE — Audit após a criação (para ter o id)

```python
class CreateProfileUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.profile_repository = repository_manager.profile_repository
        self.audit_log_repository = repository_manager.audit_log_repository

    def execute(
        self, data: CreateProfileDTO, requesting_username: Optional[str] = None
    ) -> Profile:
        profile = Profile(name=data.name)
        self.profile_repository.create(profile)

        # Após create, a entidade já tem id
        audit_entry = profile.build_audit_entry(
            new_state=profile,
            action="CREATE",
            description="Criação de novo perfil",
            agent_username=requesting_username or "",
        )
        self.audit_log_repository.save_from_entry(audit_entry)
        return profile
```

### UPDATE com dict parcial — Audit ANTES da alteração

```python
class UpdateProfileUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.profile_repository = repository_manager.profile_repository
        self.audit_log_repository = repository_manager.audit_log_repository

    def execute(self, profile_id: int, data: UpdateProfileDTO, requesting_username: Optional[str] = None):
        profile = self.__find_by_id(profile_id, raise_if_not_found=True)

        data_to_update = {}
        if data.name is not None:
            data_to_update["name"] = data.name

        if data_to_update:
            # ANTES do update — captura estado antigo
            audit_entry = profile.build_audit_entry(
                new_state=data_to_update,
                action="UPDATE",
                description="Atualização de dados do perfil",
                agent_username=requesting_username or "",
            )
            self.profile_repository.update(profile_id, data_to_update)
            self.audit_log_repository.save_from_entry(audit_entry)
```

### UPDATE com relações (ex: roles) — Audit ANTES de alterar a propriedade

```python
class UpdateProfileRolesUseCase:
    def execute(self, profile_id: int, role_ids: List[int], requesting_username: Optional[str] = None):
        profile = self.__find_profile_by_id(profile_id, raise_if_not_found=True)
        roles = self.__find_roles_by_id_in(role_ids)

        # ANTES de alterar profile.roles
        audit_entry = profile.build_audit_entry(
            new_state={"roles": [role.name for role in roles]},
            action="UPDATE",
            description="Atualização de permissões do perfil",
            agent_username=requesting_username or "",
        )

        profile.roles = roles  # Agora sim altera
        self.profile_repository.update_entity(profile)
        self.audit_log_repository.save_from_entry(audit_entry)
```

### DELETE — Audit ANTES da exclusão

```python
class DeleteProfileUseCase:
    def execute(self, profile_id: int, requesting_username: Optional[str] = None):
        profile = self.__find_by_id(profile_id, raise_if_not_found=True)

        # ANTES do delete — captura estado atual
        audit_entry = profile.build_audit_entry(
            new_state=profile,
            action="DELETE",
            description="Remoção de perfil",
            agent_username=requesting_username or "",
        )
        self.profile_repository.delete(profile_id)
        self.audit_log_repository.save_from_entry(audit_entry)
```

## Passando `requesting_username` — Controller e Router

O `requesting_username` identifica quem realizou a ação. Ele vem do `access_token` do usuário autenticado.

**Controller:** Recebe `access_token` no construtor e extrai o username:

```python
from typing import Optional
from api.routers.dependencies.access_token_data import AccessTokenData

class ProfilesController:
    def __init__(
        self,
        db_manager: DatabaseManagerConnection,
        access_token: Optional[AccessTokenData] = None,
    ):
        self.repository_manager = RepositoryManager(db_manager=db_manager)
        self.access_token = access_token

    @property
    def _requesting_username(self) -> Optional[str]:
        return self.access_token.username if self.access_token else None

    def create(self, data: CreateProfileRequest, requester_tenant_id: int):
        # ...
        profile = CreateProfileUseCase(self.repository_manager).execute(
            dto, requesting_username=self._requesting_username
        )
```

**Router:** Passa `access_token=current_user` nas rotas de escrita:

```python
@router.post("", status_code=HTTPStatus.CREATED, dependencies=[require_role("profiles:create")])
async def create_profile(data: CreateProfileRequest, current_user: CurrentUser, db_manager: DBManager):
    return ProfilesController(db_manager=db_manager, access_token=current_user).create(
        data, current_user.tenant_id
    )
```

## Endpoint de Histórico

Cada entidade auditável deve ter um endpoint GET para listar seu histórico de alterações.

**Schema de resposta** (`src/api/schemas/audit_log_response.py`):

```python
from typing import Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class AuditLogChangeResponse:
    field: str
    path: str
    valueType: str
    oldValue: Optional[Any] = None
    newValue: Optional[Any] = None

@dataclass
class AuditLogResponse:
    id: int
    entityType: str
    entityId: int
    action: str
    description: str
    agentUsername: str
    createdAt: datetime
    changes: List[AuditLogChangeResponse] = field(default_factory=list)
```

**Use Case** (`src/application/usecases/audit_logs/list_audit_logs_usecase.py`):

```python
from typing import List
from application.repositories import RepositoryManagerInterface
from domain import AuditLog

class ListAuditLogsUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.audit_log_repository = repository_manager.audit_log_repository

    def execute(self, entity_type: str, entity_id: int) -> List[AuditLog]:
        return self.audit_log_repository.find_by_entity(entity_type, entity_id)
```

**Rota no router:**

```python
@router.get(
    "/{entity_id}/history",
    status_code=HTTPStatus.OK,
    response_model=list[AuditLogResponse],
    dependencies=[require_role("entidade:read")],
)
async def get_entity_history(entity_id: int, current_user: CurrentUser, db_manager: DBManager):
    return EntityController(db_manager=db_manager).history(entity_id)
```

**Método no controller:**

```python
def history(self, entity_id: int) -> list[AuditLogResponse]:
    logs = ListAuditLogsUseCase(self.repository_manager).execute("entity_type", entity_id)
    return [self.__to_audit_log_response(log) for log in logs]

def __to_audit_log_response(self, log: AuditLog) -> AuditLogResponse:
    return AuditLogResponse(
        id=log.id,
        entityType=log.entity_type,
        entityId=log.entity_id,
        action=log.action,
        description=log.description,
        agentUsername=log.agent_username,
        changes=[
            AuditLogChangeResponse(
                field=c.get("field", ""),
                path=c.get("path", ""),
                oldValue=c.get("oldValue"),
                newValue=c.get("newValue"),
                valueType=c.get("valueType", "string"),
            )
            for c in log.changes
        ],
        createdAt=log.created_at,
    )
```

## Formato da Resposta da API

Os logs são retornados em `camelCase` como todas as responses da API.

### Exemplo CREATE

```json
{
    "id": 1,
    "entityType": "user",
    "entityId": 42,
    "action": "CREATE",
    "description": "Criação de novo usuário",
    "agentUsername": "admin",
    "createdAt": "2025-01-30T14:30:00",
    "changes": [
        {
            "field": "username",
            "path": "username",
            "oldValue": null,
            "newValue": "joao.silva",
            "valueType": "string"
        },
        {
            "field": "roles",
            "path": "roles",
            "oldValue": null,
            "newValue": ["user"],
            "valueType": "list"
        }
    ]
}
```

### Exemplo UPDATE

Apenas os campos que **realmente mudaram** são incluídos no array `changes`.

```json
{
    "id": 2,
    "entityType": "user",
    "entityId": 42,
    "action": "UPDATE",
    "description": "Dados do usuário atualizados",
    "agentUsername": "admin",
    "createdAt": "2025-01-30T15:00:00",
    "changes": [
        {
            "field": "full_name",
            "path": "full_name",
            "oldValue": "João Silva",
            "newValue": "João Silva Santos",
            "valueType": "string"
        }
    ]
}
```

### Exemplo DELETE

```json
{
    "id": 3,
    "entityType": "user",
    "entityId": 42,
    "action": "DELETE",
    "description": "Usuário excluído",
    "agentUsername": "admin",
    "createdAt": "2025-01-30T17:00:00",
    "changes": [
        {
            "field": "username",
            "path": "username",
            "oldValue": "joao.silva",
            "newValue": null,
            "valueType": "string"
        }
    ]
}
```

### Exemplo com campos aninhados

Quando a entidade possui campos aninhados, o `path` indica a hierarquia completa.

```json
{
    "id": 4,
    "entityType": "company",
    "entityId": 10,
    "action": "UPDATE",
    "description": "Endereço da empresa atualizado",
    "agentUsername": "admin",
    "createdAt": "2025-01-30T18:00:00",
    "changes": [
        {
            "field": "city",
            "path": "address.city",
            "oldValue": "São Paulo",
            "newValue": "Rio de Janeiro",
            "valueType": "string"
        }
    ]
}
```

## Resumo das Regras de Auditoria

1. **Apenas em operações de escrita** — INSERT, UPDATE, DELETE
2. **`audit_entity_type` sempre minúsculo** — `"user"`, `"profile"`, nunca `"User"`
3. **`build_audit_entry` ANTES de alterar** — Exceto em CREATE (após create para ter o id)
4. **Não auditar campos sensíveis** — Senhas, tokens, etc.
5. **Apenas em entidades especificadas** — Não adicionar auditoria por conta própria
6. **`requesting_username` vem do `access_token`** — Passado do router → controller → usecase
7. **Endpoint de histórico** — `GET /{entidade}/{id}/history` para cada entidade auditável
8. **Listas são comparadas por conteúdo** — A ordem dos itens não importa. `["admin", "user"]` é igual a `["user", "admin"]`
9. **`description` sempre em português** — Frases curtas e claras, no passado, com o nome da entidade
10. **`get_auditable_fields` com nomes reais dos atributos** — Chaves em `snake_case`, sem labels de exibição
11. **`get_friendly_fields_mapping` é obrigatório e em PT-BR** — Mapeia chave técnica para nome amigável exibido em `changes.path`
12. **Não auditar IDs/FKs técnicas e campos internos** — Evitar `tenant_id`, `*_id`, chaves de storage/checksum etc.
13. **Para relações, usar valor legível ao usuário** — Exibir `name`/`title`/`code`/`matricula`; se não houver valor legível, omitir
14. **Sem `filter_audit_fields` nos usecases** — Passe o `new_state` direto para `build_audit_entry`
15. **Sem log vazio** — Se `changes` estiver vazio, `save_from_entry` retorna `None` e não persiste
