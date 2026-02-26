# Guia de Testes Automatizados

Este documento descreve todos os padroes e convencoes que devem ser seguidos ao criar testes automatizados para os projetos. Todos os projetos seguem a mesma arquitetura de pastas e o mesmo padrao de repositorios e APIs.

---

## Estrutura de Pastas

```
tests/
├── __init__.py
├── conftest.py
├── api/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_roles.py
│   ├── test_profiles.py
│   ├── test_tenants.py
│   ├── test_sessions.py
│   └── test_modules.py
└── fixtures/
    ├── __init__.py
    ├── app.py
    ├── tenants.py
    ├── mock_fake_repository_manager.py
    ├── fake_integration_manager.py
    └── fake_repositories/
        ├── __init__.py
        ├── fake_repository_manager.py
        ├── fake_user_repository.py
        ├── fake_role_repository.py
        ├── fake_profile_repository.py
        ├── fake_tenant_repository.py
        ├── fake_session_repository.py
        ├── fake_login_attempt_repository.py
        ├── fake_validate_user_repository.py
        ├── fake_module_repository.py
        └── fake_audit_log_repository.py
```

### Regras de nomenclatura

- Cada arquivo de teste DEVE comecar com o prefixo `test_` (ex: `test_user.py`, `test_auth.py`).
- Cada funcao de teste DEVE comecar com o prefixo `test_` (ex: `test_should_create_an_user`).
- Os nomes dos testes devem seguir o padrao `test_should_<acao>` para casos de sucesso e `test_should_not_<acao>` para casos de falha.

---

## Comentarios de Lint Obrigatorios

### Em cada arquivo `__init__.py`

```python
# pyright: reportUnusedImport=false
```

### No arquivo `tests/conftest.py`

```python
# pylint: disable=W0611
# pyright: reportUnusedImport=false
```

### No arquivo `tests/fixtures/app.py`

```python
# pylint: disable=W0102
# pylint: disable=W0221
# pylint: disable=W0613
# pyright: reportIncompatibleMethodOverride=false
```

### No topo de cada arquivo de teste (`tests/api/test_*.py`)

```python
# pylint: disable=W0613
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
```

---

## Arquivos de Configuracao

### pytest.ini

O arquivo `pytest.ini` deve estar na raiz do projeto:

```ini
[pytest]
testpaths = tests
pythonpath = src
```

- `testpaths`: Define o diretorio onde os testes estao localizados.
- `pythonpath`: Adiciona `src/` ao Python path para que os imports funcionem diretamente (ex: `from domain import User`, `from application.repositories import ...`).

### .pylintrc

O arquivo `.pylintrc` deve estar na raiz do projeto. As configuracoes mais importantes para os testes:

```ini
[*]
disable=
    C0114, # missing-module-docstring
    C0115, # missing-class-docstring
    C0116, # missing-function-docstring
    W0707, # raise-missing-from
    E0611, # no-name-in-module
    W0719, # broad-exception-raised
    C0103, # invalid-name
    W0622, # redefined-builtin
    W0102, # dangerous-default-value
    W0718, # broad-exception-caught

[DESIGN]
max-args=20
max-attributes=7
max-locals=15
max-public-methods=20
max-statements=50
min-public-methods=1

[FORMAT]
indent-after-paren=4
indent-string='    '
max-line-length=120
max-module-lines=1000
```

### .coveragerc

O arquivo `.coveragerc` deve estar na raiz do projeto. Ele define quais arquivos devem ser excluidos do relatorio de cobertura:

```ini
[run]
omit =
    src/config.py
    src/main.py
    src/application/repositories/*
    src/infra/repositories/*
    src/infra/integrations/*
    src/infra/database_manager.py
    src/application/usecases/**/__init__.py
    tests/*
```

Arquivos excluidos:

- `src/config.py` e `src/main.py`: Arquivos de configuracao e entrada do app.
- `src/application/repositories/*`: Interfaces abstratas (ABC), nao ha logica a testar.
- `src/infra/repositories/*`: Implementacoes reais que usam banco de dados, substituidas por fake repositories nos testes.
- `src/infra/database_manager.py`: Gerenciador de conexao com banco de dados.
- `tests/*`: Os proprios testes nao precisam de cobertura.

### Script de execucao dos testes (run_tests.sh)

```bash
echo "Executando testes..."
pytest --cov=./src --cov-report=html -W ignore::DeprecationWarning -W ignore::SyntaxWarning

TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "Testes finalizados com sucesso!"
else
  echo "Testes finalizaram com falhas"
fi
echo "Relatório de cobertura: $(pwd)/htmlcov/index.html"

exit $TEST_EXIT_CODE
```

---

## Fake Repositories

Os fake repositories substituem os repositorios reais (que usam SQLAlchemy + banco de dados) por implementacoes em memoria usando listas Python. Eles implementam as mesmas interfaces abstratas (ABC) definidas em `src/application/repositories/`.

### Padrao de implementacao

Cada fake repository deve:

1. Implementar a interface correspondente de `application.repositories`.
2. Armazenar dados em uma lista privada `self.__data: List[Entity]`.
3. Gerar IDs auto-incrementais via metodo `__get_current_id()`.
4. Ter um metodo `clear()` para limpar os dados entre testes.
5. Exportar uma instancia singleton no final do arquivo.

### Exemplo completo - FakeUserRepository

```python
from typing import List, Optional, Dict, Any

from application.repositories import UserRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import User


class FakeUserRepository(UserRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[User] = []

    def create(self, user: User) -> User:
        user.id = self.__get_current_id()
        self.__data.append(user)
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        return next((user for user in self.__data if user.id == user_id), None)

    def find_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self.__data if user.email == email), None)

    def find_by_username(self, username: str) -> Optional[User]:
        return next((user for user in self.__data if user.username == username), None)

    def find_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        return next(
            (
                user
                for user in self.__data
                if user.email == email_or_username or user.username == email_or_username
            ),
            None,
        )

    def find_all(
        self, page: Optional[int] = None, per_page: Optional[int] = None, tenant_id: Optional[int] = None
    ):
        if tenant_id is not None:
            filtered_data = [
                user for user in self.__data if user.tenant_id == tenant_id
            ]
        else:
            filtered_data = self.__data
        if page is None or per_page is None:
            return filtered_data
        start = (page - 1) * per_page
        end = start + per_page
        return DBPaginatedResult(data=filtered_data[start:end], total_count=len(filtered_data))

    def update(self, user_id: int, data_to_update: Dict[str, Any]) -> None:
        user = self.find_by_id(user_id)
        if user:
            for key, value in data_to_update.items():
                setattr(user, key, value)

    def update_entity(self, user: User) -> User:
        existing_user = self.find_by_id(user.id)
        if existing_user:
            self.__data.remove(existing_user)
        self.__data.append(user)
        return user

    def delete(self, user_id: int) -> None:
        self.__data = [user for user in self.__data if user.id != user_id]

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(user.id for user in self.__data) + 1


fake_user_repository = FakeUserRepository()
```

### Exemplo - FakeRoleRepository

```python
from typing import List, Optional

from application.repositories import RoleRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import Role


class FakeRoleRepository(RoleRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[Role] = []

    def create(self, role: Role) -> Role:
        role.id = self.__get_current_id()
        self.__data.append(role)
        return role

    def find_by_id(self, role_id: int) -> Optional[Role]:
        return next((role for role in self.__data if role.id == role_id), None)

    def find_by_name(self, name: str) -> Optional[Role]:
        return next((role for role in self.__data if role.name == name), None)

    def find_by_id_in(self, ids: List[int]) -> List[Role]:
        return [role for role in self.__data if role.id in ids]

    def find_all(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        tenant_id: Optional[int] = None,
        module_ids: Optional[List[int]] = None,
    ):
        filtered = self.__data

        if module_ids:
            filtered = [
                role for role in filtered
                if hasattr(role, 'modules') and role.modules
                and any(module.id in module_ids for module in role.modules)
            ]

        if page is None or per_page is None:
            return list(filtered)
        start = (page - 1) * per_page
        end = start + per_page
        return DBPaginatedResult(data=filtered[start:end], total_count=len(filtered))

    def update(self, role: Role) -> Role:
        existing = self.find_by_id(role.id)
        if existing:
            self.__data.remove(existing)
        self.__data.append(role)
        return role

    def delete(self, role_id: int) -> None:
        self.__data = [role for role in self.__data if role.id != role_id]

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(role.id for role in self.__data) + 1


fake_role_repository = FakeRoleRepository()
```

### Exemplo - FakeTenantRepository (caso especial)

O tenant "system" sempre recebe `id=1`. Os demais tenants comecam com `id=2`.

```python
from typing import List, Optional

from application.repositories import TenantRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import Tenant, Module


class FakeTenantRepository(TenantRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[Tenant] = []

    def create(self, tenant: Tenant) -> Tenant:
        if tenant.identifier == "system":
            tenant.id = 1
        else:
            tenant.id = self.__get_current_id()
        self.__data.append(tenant)
        return tenant

    def find_by_id(self, tenant_id: int) -> Optional[Tenant]:
        return next((t for t in self.__data if t.id == tenant_id), None)

    def find_by_identifier(self, identifier: str) -> Optional[Tenant]:
        return next((t for t in self.__data if t.identifier == identifier), None)

    def find_all(self, page: int, per_page: int) -> DBPaginatedResult[Tenant]:
        start = (page - 1) * per_page
        end = start + per_page
        return DBPaginatedResult(data=self.__data[start:end], total_count=len(self.__data))

    def update(self, tenant: Tenant) -> Tenant:
        existing = self.find_by_id(tenant.id)
        if existing:
            self.__data.remove(existing)
        self.__data.append(tenant)
        return tenant

    def delete(self, tenant_id: int) -> None:
        self.__data = [t for t in self.__data if t.id != tenant_id]

    def assign_modules(self, tenant: Tenant, modules: List[Module]) -> Tenant:
        tenant.modules = modules
        existing = self.find_by_id(tenant.id)
        if existing:
            self.__data.remove(existing)
        self.__data.append(tenant)
        return tenant

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 2  # o id 1 is reserved for the system tenant
        return max(t.id for t in self.__data) + 1


fake_tenant_repository = FakeTenantRepository()
```

### Exemplo - FakeSessionRepository (dependencia entre repositorios)

O session repository precisa popular o atributo `session.user` que no ORM real (SQLAlchemy) seria carregado via lazy loading. Para isso, ele recebe uma referencia ao user repository.

```python
from typing import List, Optional

from application.repositories import SessionRepositoryInterface, UserRepositoryInterface
from domain import Session


class FakeSessionRepository(SessionRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[Session] = []
        self._user_repository = None

    def set_user_repository(self, user_repository: UserRepositoryInterface) -> None:
        self._user_repository = user_repository

    def create(self, session: Session) -> Session:
        session.id = self.__get_current_id()
        self._attach_user(session)
        self.__data.append(session)
        return session

    def find_by_id(self, session_id: int) -> Optional[Session]:
        return next((s for s in self.__data if s.id == session_id), None)

    def find_by_user_id(self, user_id: int) -> List[Session]:
        return [s for s in self.__data if s.user_id == user_id]

    def update(self, session: Session) -> Session:
        existing = self.find_by_id(session.id)
        if existing:
            self.__data.remove(existing)
        self._attach_user(session)
        self.__data.append(session)
        return session

    def delete(self, session_id: int) -> None:
        self.__data = [s for s in self.__data if s.id != session_id]

    def delete_by_user_id(self, user_id: int) -> None:
        self.__data = [s for s in self.__data if s.user_id != user_id]

    def clear(self) -> None:
        self.__data.clear()

    def _attach_user(self, session: Session) -> None:
        if self._user_repository and (
            not hasattr(session, "user")
            or getattr(session, "user", None) is None
        ):
            user = self._user_repository.find_by_id(session.user_id)
            if user:
                session.user = user

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(s.id for s in self.__data) + 1


fake_session_repository = FakeSessionRepository()
```

### Exemplo - FakeAuditLogRepository

O audit log repository possui o metodo `save_from_entry` que converte um `AuditEntry` em `AuditLog`:

```python
from typing import List

from application.repositories import AuditLogRepositoryInterface
from domain import AuditLog
from domain.history import AuditEntry


class FakeAuditLogRepository(AuditLogRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[AuditLog] = []

    def create(self, audit_log: AuditLog) -> AuditLog:
        audit_log.id = self.__get_current_id()
        self.__data.append(audit_log)
        return audit_log

    def save_from_entry(self, audit_entry: AuditEntry) -> AuditLog:
        audit_log = AuditLog(
            entity_type=audit_entry.entity_type,
            entity_id=audit_entry.entity_id,
            action=audit_entry.action,
            description=audit_entry.description,
            agent_username=audit_entry.agent_username,
            changes=[change.__dict__ for change in audit_entry.changes],
            created_at=audit_entry.timestamp,
        )
        return self.create(audit_log)

    def find_by_entity(self, entity_type: str, entity_id: int) -> List[AuditLog]:
        return [
            al
            for al in self.__data
            if al.entity_type == entity_type and al.entity_id == entity_id
        ]

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(al.id for al in self.__data) + 1


fake_audit_log_repository = FakeAuditLogRepository()
```

### Exemplo - FakeLoginAttemptRepository

```python
from typing import List, Optional

from application.repositories import LoginAttemptRepositoryInterface
from domain import LoginAttempt


class FakeLoginAttemptRepository(LoginAttemptRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[LoginAttempt] = []

    def create(self, login_attempt: LoginAttempt) -> LoginAttempt:
        login_attempt.id = self.__get_current_id()
        self.__data.append(login_attempt)
        return login_attempt

    def find_by_id(self, login_attempt_id: int) -> Optional[LoginAttempt]:
        return next((la for la in self.__data if la.id == login_attempt_id), None)

    def find_by_user_id(self, user_id: int) -> Optional[LoginAttempt]:
        return next((la for la in self.__data if la.user_id == user_id), None)

    def update(self, login_attempt: LoginAttempt) -> LoginAttempt:
        existing = self.find_by_id(login_attempt.id)
        if existing:
            self.__data.remove(existing)
        self.__data.append(login_attempt)
        return login_attempt

    def delete_by_user_id(self, user_id: int) -> None:
        self.__data = [la for la in self.__data if la.user_id != user_id]

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(la.id for la in self.__data) + 1


fake_login_attempt_repository = FakeLoginAttemptRepository()
```

### Exemplo - FakeValidateUserRepository

```python
from typing import List, Optional

from application.repositories import ValidateUserRepositoryInterface
from domain import ValidateUser


class FakeValidateUserRepository(ValidateUserRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[ValidateUser] = []

    def create(self, validate_user: ValidateUser) -> ValidateUser:
        validate_user.id = self.__get_current_id()
        self.__data.append(validate_user)
        return validate_user

    def find_by_id(self, validate_user_id: int) -> Optional[ValidateUser]:
        return next((vu for vu in self.__data if vu.id == validate_user_id), None)

    def find_by_user_id(self, user_id: int) -> Optional[ValidateUser]:
        return next((vu for vu in self.__data if vu.user_id == user_id), None)

    def find_by_code(self, code: int) -> Optional[ValidateUser]:
        return next((vu for vu in self.__data if vu.code == code), None)

    def delete(self, validate_user_id: int) -> None:
        self.__data = [vu for vu in self.__data if vu.id != validate_user_id]

    def delete_by_user_id(self, user_id: int) -> None:
        self.__data = [vu for vu in self.__data if vu.user_id != user_id]

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(vu.id for vu in self.__data) + 1


fake_validate_user_repository = FakeValidateUserRepository()
```

### Exemplo - FakeModuleRepository

```python
from typing import List, Optional

from application.repositories import ModuleRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import Module, Role


class FakeModuleRepository(ModuleRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[Module] = []

    def create(self, module: Module) -> Module:
        module.id = self.__get_current_id()
        self.__data.append(module)
        return module

    def find_by_id(self, module_id: int) -> Optional[Module]:
        return next((m for m in self.__data if m.id == module_id), None)

    def find_by_name(self, name: str) -> Optional[Module]:
        return next((m for m in self.__data if m.name == name), None)

    def find_by_id_in(self, ids: List[int]) -> List[Module]:
        return [m for m in self.__data if m.id in ids]

    def find_all(
        self, page: Optional[int] = None, per_page: Optional[int] = None, tenant_id: Optional[int] = None
    ):
        if page is None or per_page is None:
            return list(self.__data)
        start = (page - 1) * per_page
        end = start + per_page
        return DBPaginatedResult(data=self.__data[start:end], total_count=len(self.__data))

    def update(self, module: Module) -> Module:
        existing = self.find_by_id(module.id)
        if existing:
            self.__data.remove(existing)
        self.__data.append(module)
        return module

    def delete(self, module_id: int) -> None:
        self.__data = [m for m in self.__data if m.id != module_id]

    def assign_roles(self, module: Module, roles: List[Role]) -> Module:
        module.roles = roles
        existing = self.find_by_id(module.id)
        if existing:
            self.__data.remove(existing)
        self.__data.append(module)
        return module

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(m.id for m in self.__data) + 1


fake_module_repository = FakeModuleRepository()
```

### Exemplo - FakeProfileRepository

```python
from typing import List, Optional, Dict, Any

from application.repositories import ProfileRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import Profile


class FakeProfileRepository(ProfileRepositoryInterface):
    def __init__(self) -> None:
        self.__data: List[Profile] = []

    def create(self, profile: Profile) -> Profile:
        profile.id = self.__get_current_id()
        self.__data.append(profile)
        return profile

    def find_by_id(self, profile_id: int) -> Optional[Profile]:
        return next((p for p in self.__data if p.id == profile_id), None)

    def find_by_id_in(self, ids: List[int]) -> List[Profile]:
        return [p for p in self.__data if p.id in ids]

    def find_all(
        self, page: Optional[int] = None, per_page: Optional[int] = None, tenant_id: Optional[int] = None
    ):
        if tenant_id is not None:
            filtered = [p for p in self.__data if p.tenant_id == tenant_id]
        else:
            filtered = self.__data
        if page is None or per_page is None:
            return filtered
        start = (page - 1) * per_page
        end = start + per_page
        return DBPaginatedResult(data=filtered[start:end], total_count=len(filtered))

    def update(self, profile_id: int, data_to_update: Dict[str, Any]) -> None:
        profile = self.find_by_id(profile_id)
        if profile:
            for key, value in data_to_update.items():
                setattr(profile, key, value)

    def update_entity(self, profile: Profile) -> Profile:
        existing = self.find_by_id(profile.id)
        if existing:
            self.__data.remove(existing)
        self.__data.append(profile)
        return profile

    def delete(self, profile_id: int) -> None:
        self.__data = [p for p in self.__data if p.id != profile_id]

    def clear(self) -> None:
        self.__data.clear()

    def __get_current_id(self) -> int:
        if not self.__data:
            return 1
        return max(p.id for p in self.__data) + 1


fake_profile_repository = FakeProfileRepository()
```

---

## FakeRepositoryManager

O `FakeRepositoryManager` implementa a interface `RepositoryManagerInterface` e retorna os fake repositories via properties. Ele tambem possui o metodo `clear_all_data()` que limpa todos os repositorios.

```python
from application.repositories import (
    RepositoryManagerInterface,
    UserRepositoryInterface,
    RoleRepositoryInterface,
    ProfileRepositoryInterface,
    TenantRepositoryInterface,
    SessionRepositoryInterface,
    LoginAttemptRepositoryInterface,
    ValidateUserRepositoryInterface,
    ModuleRepositoryInterface,
    AuditLogRepositoryInterface,
)

from .fake_user_repository import fake_user_repository
from .fake_role_repository import fake_role_repository
from .fake_profile_repository import fake_profile_repository
from .fake_tenant_repository import fake_tenant_repository
from .fake_session_repository import fake_session_repository
from .fake_login_attempt_repository import fake_login_attempt_repository
from .fake_validate_user_repository import fake_validate_user_repository
from .fake_module_repository import fake_module_repository
from .fake_audit_log_repository import fake_audit_log_repository


class FakeRepositoryManager(RepositoryManagerInterface):

    @property
    def user_repository(self) -> UserRepositoryInterface:
        return fake_user_repository

    @property
    def role_repository(self) -> RoleRepositoryInterface:
        return fake_role_repository

    @property
    def profile_repository(self) -> ProfileRepositoryInterface:
        return fake_profile_repository

    @property
    def tenant_repository(self) -> TenantRepositoryInterface:
        return fake_tenant_repository

    @property
    def session_repository(self) -> SessionRepositoryInterface:
        return fake_session_repository

    @property
    def login_attempt_repository(self) -> LoginAttemptRepositoryInterface:
        return fake_login_attempt_repository

    @property
    def validate_user_repository(self) -> ValidateUserRepositoryInterface:
        return fake_validate_user_repository

    @property
    def module_repository(self) -> ModuleRepositoryInterface:
        return fake_module_repository

    @property
    def audit_log_repository(self) -> AuditLogRepositoryInterface:
        return fake_audit_log_repository

    def clear_all_data(self) -> None:
        fake_user_repository.clear()
        fake_role_repository.clear()
        fake_profile_repository.clear()
        fake_tenant_repository.clear()
        fake_session_repository.clear()
        fake_login_attempt_repository.clear()
        fake_validate_user_repository.clear()
        fake_module_repository.clear()
        fake_audit_log_repository.clear()


fake_repository_manager = FakeRepositoryManager()
fake_session_repository.set_user_repository(fake_user_repository)
```

### Pontos importantes

- A instancia `fake_repository_manager` e um singleton criado no final do arquivo.
- Dependencias entre repositorios devem ser configuradas apos a criacao do singleton (ex: `fake_session_repository.set_user_repository(fake_user_repository)`).
- O metodo `clear_all_data()` DEVE limpar todos os repositorios para garantir isolamento entre testes.

### `__init__.py` do fake_repositories

```python
# pyright: reportUnusedImport=false

from .fake_repository_manager import fake_repository_manager
from .fake_audit_log_repository import fake_audit_log_repository
from .fake_login_attempt_repository import fake_login_attempt_repository
from .fake_module_repository import fake_module_repository
from .fake_profile_repository import fake_profile_repository
from .fake_role_repository import fake_role_repository
from .fake_session_repository import fake_session_repository
from .fake_tenant_repository import fake_tenant_repository
from .fake_user_repository import fake_user_repository
from .fake_validate_user_repository import fake_validate_user_repository
```

---

## Mock do RepositoryManager (mock_fake_repository_manager.py)

Este arquivo contem a fixture `autouse` que substitui o `RepositoryManager` e o `IntegrationManager` reais pelos fakes em todos os testes. Usa `unittest.mock.patch` no metodo `__new__` das classes reais.

```python
from pytest import fixture
from unittest.mock import patch
from tests.fixtures.fake_repositories.fake_repository_manager import (
    fake_repository_manager,
)
from tests.fixtures.fake_integration_manager import fake_integration_manager


@fixture(scope="function", autouse=True)
def mock_fake_repository_manager():
    with patch(
        "infra.repositories.RepositoryManager.__new__",
        return_value=fake_repository_manager,
    ), patch(
        "infra.integrations.IntegrationManager.__new__",
        return_value=fake_integration_manager,
    ):
        yield fake_repository_manager
    fake_repository_manager.clear_all_data()
    fake_integration_manager.clear()
```

### Pontos importantes

- A fixture tem `scope="function"` e `autouse=True`, ou seja, roda automaticamente antes de cada teste.
- O patch e feito no `__new__` porque as classes de infra sao instanciadas internamente pelos controllers/use cases. NAO usar mockito `when()` em classes ABC pois causa `TypeError`.
- Apos cada teste, `clear_all_data()` e `clear()` sao chamados para garantir isolamento.
- O import path do patch deve ser o caminho do modulo como e importado no codigo da aplicacao (ex: `infra.repositories.RepositoryManager`, NAO `src.infra.repositories.RepositoryManager`).

---

## FakeIntegrationManager (fake_integration_manager.py)

Substitui integracoes externas (ex: AWS SQS para envio de emails) por implementacoes em memoria.

```python
from typing import Dict, Any

from application.integrations import (
    IntegrationManagerInterface,
    QueueIntegrationInterface,
)


class FakeQueueIntegration(QueueIntegrationInterface):
    def __init__(self) -> None:
        self.sent_emails: list[Dict[str, Any]] = []

    def send_email(self, message_body: Dict[str, Any]) -> None:
        self.sent_emails.append(message_body)

    def clear(self) -> None:
        self.sent_emails.clear()


class FakeIntegrationManager(IntegrationManagerInterface):
    def __init__(self) -> None:
        self._queue_integration = FakeQueueIntegration()

    def queue_integration(self) -> QueueIntegrationInterface:
        return self._queue_integration

    def clear(self) -> None:
        self._queue_integration.clear()


fake_integration_manager = FakeIntegrationManager()
```

### Pontos importantes

- `FakeQueueIntegration` armazena os emails enviados em `sent_emails` em vez de enviar para AWS SQS.
- Os testes podem verificar se um email foi enviado acessando `fake_integration_manager.queue_integration().sent_emails`.
- Se o projeto tiver outras integracoes (ex: storage, notification), crie fakes seguindo o mesmo padrao.

---

## Fixture Client (tests/fixtures/app.py)

A fixture `client` cria uma instancia do `TestClient` do FastAPI com suporte a JWT para autenticacao.

```python
# pylint: disable=W0102
# pylint: disable=W0221
# pylint: disable=W0613
# pyright: reportIncompatibleMethodOverride=false

from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from json import dumps
from fastapi import FastAPI
from fastapi.testclient import TestClient
import jwt
import pytest

from src.main import create_app
from src.config import JWT_SECRET_KEY


class Client(TestClient):
    """Client to test the api"""

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.token_data = {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "uid": 1,
            "roles": [],
            "email": "teste@teste.com",
            "username": "teste",
            "validated": True,
            "tenantId": 1,
            "sessionId": 1,
        }
        self.headers = {"Authorization": f"Bearer {self.__generate_token()}"}

    def get(self, url: str, headers: Dict[str, Any] = {}, params: Dict[str, Any] = {}):
        return super().get(url=url, headers={**self.headers, **headers}, params=params)

    def post(
        self,
        url: str,
        data: Dict[str, Any] = {},
        headers: Dict[str, Any] = {},
        params: Dict[str, Any] = {},
    ):
        return super().post(
            url=url,
            data=dumps(data),
            headers={**self.headers, **headers},
            params=params,
        )

    def put(
        self,
        url: str,
        data: Dict[str, Any] = {},
        headers: Dict[str, Any] = {},
        params: Dict[str, Any] = {},
    ):
        return super().put(
            url=url,
            data=dumps(data),
            headers={**self.headers, **headers},
            params=params,
        )

    def delete(
        self, url: str, headers: Dict[str, Any] = {}, params: Dict[str, Any] = {}
    ):
        return super().delete(
            url=url, headers={**self.headers, **headers}, params=params
        )

    def add_extra_data_token(self, data: Dict[str, Any]):
        self.token_data = {**self.token_data, **data}
        self.headers = {"Authorization": f"Bearer {self.__generate_token()}"}
        return self

    def clear_authorization(self):
        self.headers = {}
        return self

    def __generate_token(self):
        return jwt.encode(
            self.token_data,
            key=JWT_SECRET_KEY,
            algorithm="HS256",
        )


@pytest.fixture(scope="function")
def client():
    app = create_app()
    yield Client(app)
```

### Pontos importantes

- O `Client` gera automaticamente um JWT valido com `tenantId=1` (system tenant) e `validated=True`.
- `add_extra_data_token({"roles": ["users:create"]})`: Adiciona roles ou modifica dados do token. Retorna `self` para permitir encadeamento.
- `clear_authorization()`: Remove o header Authorization para testar endpoints sem autenticacao.
- O metodo `post` e `put` serializam o parametro `data` com `dumps()` automaticamente.
- O metodo `delete` NAO aceita parametro `data`. Para DELETE com body, use `client.request("DELETE", url, headers=client.headers, content=dumps(data))`.
- O token padrao nao possui roles, portanto qualquer endpoint que exija permissao retornara `403 FORBIDDEN` com o client padrao.

---

## Fixture Tenants (tests/fixtures/tenants.py)

A fixture `tenants` cria o tenant do sistema que e necessario para a maioria dos testes.

```python
from pytest import fixture
from domain import Tenant
from tests.fixtures.fake_repositories import fake_tenant_repository


TENANT_SYSTEM = Tenant(identifier="system", name="System Tenant")


@fixture(scope="function")
def tenants():
    fake_tenant_repository.create(TENANT_SYSTEM)
    yield
    fake_tenant_repository.clear()
```

### Pontos importantes

- A maioria dos testes precisa da fixture `tenants` porque as entidades possuem `tenant_id`.
- O system tenant (`identifier="system"`) sempre recebe `id=1`.
- A fixture `tenants` deve ser passada como parametro em cada funcao de teste que precise do tenant: `def test_should_create_user(client: Client, tenants):`.

---

## conftest.py

```python
# pylint: disable=W0611
# pyright: reportUnusedImport=false

from tests.fixtures import client, tenants
from tests.fixtures.mock_fake_repository_manager import mock_fake_repository_manager
```

O `conftest.py` importa as fixtures para que o pytest as disponibilize automaticamente para todos os testes. A fixture `mock_fake_repository_manager` e `autouse=True`, portanto nao precisa ser passada como parametro nos testes.

---

## tests/fixtures/**init**.py

```python
# pyright: reportUnusedImport=false
from .fake_repositories import fake_repository_manager
from .app import client, Client
from .tenants import tenants
```

---

## Padrao de Escrita dos Testes

### Estrutura de um arquivo de teste

Cada arquivo de teste segue a seguinte organizacao:

1. Comentarios de lint no topo.
2. Imports.
3. Constante `BASE_URL` com o path base do endpoint.
4. Funcoes helper `_create_*_in_db()` para criar dados de teste.
5. Testes agrupados por operacao com comentarios separadores.

```python
# pylint: disable=W0613
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false

from typing import cast
from http import HTTPStatus
from tests.fixtures import Client
from tests.fixtures.fake_repositories import (
    fake_user_repository,
    fake_tenant_repository,
)
from domain import User
from application.usecases.password import EncodePasswordUseCase

BASE_URL = "/auth-service/users"


def _create_user_in_db(
    username="testuser",
    password="a1234578",
    tenant_id=1,
    full_name="Test User",
    email="user@test.com",
) -> User:
    encoded_password = EncodePasswordUseCase().execute(password)
    user = User(
        username=username,
        password=encoded_password,
        tenant_id=tenant_id,
        full_name=full_name,
        email=email,
    )
    tenant = fake_tenant_repository.find_by_id(tenant_id)
    if tenant:
        user.tenant = tenant
    return fake_user_repository.create(user)


# ==================== CREATE USER ====================


def test_should_create_an_user(client: Client, tenants):
    ...


def test_should_not_create_user_without_permission(client: Client, tenants):
    ...


# ==================== LIST USERS ====================


def test_should_list_users(client: Client, tenants):
    ...
```

### Comentarios separadores

Cada grupo de testes por operacao CRUD deve ser separado por um comentario no formato:

```python
# ==================== NOME DA OPERACAO ====================
```

### Funcoes helper `_create_*_in_db()`

- Comecam com `_` (privadas).
- Criam entidades diretamente nos fake repositories (sem passar pela API).
- Devem popular os relacionamentos manualmente (ex: `user.tenant = tenant`).
- Devem ter valores padrao para todos os parametros.

### Padrao de teste para criacao (POST)

```python
def test_should_create_an_user(client: Client, tenants):
    users_in_db = fake_user_repository.find_all()
    assert len(users_in_db) == 0

    response = client.add_extra_data_token({"roles": ["users:create"]}).post(
        f"{BASE_URL}",
        data={
            "username": "testuser",
            "password": "a1234578",
            "tenantId": 1,
            "fullName": "Test User",
            "email": "test@test.com",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data["id"] is not None
    users_in_db = fake_user_repository.find_all()
    assert len(users_in_db) == 1
```

### Padrao de teste para listagem (GET com paginacao)

Os endpoints de listagem retornam um `PaginatedResponse` com os campos `data`, `count` e `page`. Os testes devem verificar esses tres campos:

```python
def test_should_list_users(client: Client, tenants):
    _create_user_in_db(username="user1", email="user1@test.com")
    _create_user_in_db(username="user2", email="user2@test.com")

    response = client.add_extra_data_token({"roles": ["users:read"]}).get(
        f"{BASE_URL}", params={"page": 1, "perPage": 20}
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data["data"]) == 2
    assert response_data["count"] == 2
    assert response_data["page"] == 1
```

**IMPORTANTE**: O parametro `page` deve comecar em `1`, NAO em `0`. O calculo de paginacao nos fake repositories usa `(page - 1) * per_page`, o que gera indice negativo com `page=0`.

### Padrao de teste para busca por ID (GET)

```python
def test_should_get_user_by_id(client: Client, tenants):
    user = _create_user_in_db()

    response = client.add_extra_data_token({"roles": ["users:read"]}).get(
        f"{BASE_URL}/{user.id}"
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data["id"] == user.id
    assert response_data["username"] == user.username
```

### Padrao de teste para atualizacao (PUT)

```python
def test_should_update_user(client: Client, tenants):
    user = _create_user_in_db()

    response = client.add_extra_data_token({"roles": ["users:update"]}).put(
        f"{BASE_URL}/{user.id}",
        data={"fullName": "Updated Name"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    updated_user = cast(User, fake_user_repository.find_by_id(user.id))
    assert updated_user.full_name == "Updated Name"
```

**IMPORTANTE**: Usar `cast()` do `typing` ao buscar a entidade no repositorio apos update para garantir type safety.

### Padrao de teste para exclusao (DELETE)

```python
def test_should_delete_user(client: Client, tenants):
    user = _create_user_in_db()
    assert len(fake_user_repository.find_all()) == 1

    response = client.add_extra_data_token({"roles": ["users:delete"]}).delete(
        f"{BASE_URL}/{user.id}"
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert len(fake_user_repository.find_all()) == 0
```

### Padrao de teste para DELETE com body

O metodo `client.delete()` NAO aceita parametro `data`. Para enviar body em DELETE, use `client.request()`:

```python
def test_should_remove_profiles_from_user(client: Client, tenants):
    profile = _create_profile_in_db()
    user = _create_user_in_db(profiles=[profile])

    c = client.add_extra_data_token({"roles": ["users:manage_profiles"]})
    response = c.request(
        "DELETE",
        f"{BASE_URL}/{user.id}/profiles",
        headers=c.headers,
        content=dumps({"profileIds": [profile.id]}),
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
```

### Padrao de teste para permissao (FORBIDDEN)

Cada operacao protegida deve ter um teste verificando que retorna `403` sem a role necessaria:

```python
def test_should_not_create_user_without_permission(client: Client, tenants):
    response = client.post(
        f"{BASE_URL}",
        data={
            "username": "testuser",
            "password": "a1234578",
            "tenantId": 1,
            "fullName": "Test User",
            "email": "test@test.com",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
```

### Padrao de teste para recurso nao encontrado (NOT FOUND)

```python
def test_should_return_not_found_for_nonexistent_user(client: Client, tenants):
    response = client.add_extra_data_token({"roles": ["users:read"]}).get(
        f"{BASE_URL}/999"
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
```

### Padrao de teste para duplicidade (CONFLICT)

```python
def test_should_not_create_user_with_duplicated_username(client: Client, tenants):
    _create_user_in_db(username="duplicated")

    response = client.add_extra_data_token({"roles": ["users:create"]}).post(
        f"{BASE_URL}",
        data={
            "username": "duplicated",
            "password": "a1234578",
            "tenantId": 1,
            "fullName": "Test User",
            "email": "other@test.com",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
```

### Padrao de teste para operacoes restritas ao system tenant

```python
def test_should_not_create_role_as_non_system_tenant(client: Client, tenants):
    response = client.add_extra_data_token(
        {"roles": ["roles:create"], "tenantId": 2}
    ).post(
        f"{BASE_URL}",
        data={"name": "admin", "moduleIds": [1]},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
```

### Padrao de teste para autenticacao (UNAUTHORIZED)

```python
def test_should_not_access_without_token(client: Client, tenants):
    response = client.clear_authorization().get(f"{BASE_URL}")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
```

### Padrao de teste para historico (audit log)

Para testar historico, a entidade deve ser criada via API (nao direto no repo) para que o audit log seja gerado:

```python
def test_should_get_user_history(client: Client, tenants):
    # Cria via API para gerar o audit log
    client.add_extra_data_token({"roles": ["users:create"]}).post(
        f"{BASE_URL}",
        data={
            "username": "audited_user",
            "password": "a1234578",
            "tenantId": 1,
            "fullName": "Audited User",
            "email": "audited@test.com",
        },
    )

    audited_user = cast(User, fake_user_repository.find_by_username("audited_user"))

    response = client.add_extra_data_token({"roles": ["users:read"]}).get(
        f"{BASE_URL}/{audited_user.id}/history"
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data) > 0
```

### Padrao de teste para auth (login)

Testes de login precisam criar o `LoginAttempt` associado ao usuario:

```python
def _create_user_in_db(
    username="testuser",
    password="a1234578",
    tenant_id=1,
    full_name="Test User",
    email="user@test.com",
) -> User:
    encoded_password = EncodePasswordUseCase().execute(password)
    user = User(
        username=username,
        password=encoded_password,
        tenant_id=tenant_id,
        full_name=full_name,
        email=email,
    )
    tenant = fake_tenant_repository.find_by_id(tenant_id)
    if tenant:
        user.tenant = tenant
    created_user = fake_user_repository.create(user)
    login_attempt = LoginAttempt(user_id=created_user.id)
    login_attempt.attempts = 0
    created_attempt = fake_login_attempt_repository.create(login_attempt)
    created_user.attempts = created_attempt
    return created_user


def test_should_login_with_username(client: Client, tenants):
    _create_user_in_db(username="loginuser", password="a1234578")

    response = client.clear_authorization().post(
        f"{BASE_URL}/login",
        data={
            "emailOrUsername": "loginuser",
            "password": "a1234578",
        },
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert "accessToken" in response_data
    assert "refreshToken" in response_data
    assert response_data["tokenType"] == "Bearer"
```

---

## Sistema de Permissoes nos Testes

O sistema de permissoes usa roles no formato `recurso:acao`. As roles sao injetadas no token JWT via `add_extra_data_token()`.

### Roles padrao por recurso

| Recurso  | Roles                                                                                                       |
| -------- | ----------------------------------------------------------------------------------------------------------- |
| users    | `users:create`, `users:read`, `users:update`, `users:delete`, `users:manage_roles`, `users:manage_profiles` |
| roles    | `roles:create`, `roles:read`, `roles:read-all`, `roles:update`, `roles:delete`                              |
| profiles | `profiles:create`, `profiles:read`, `profiles:update`, `profiles:delete`, `profiles:manage_roles`           |
| tenants  | `tenants:create`, `tenants:read`, `tenants:update`, `tenants:delete`, `tenants:assign-modules`              |
| modules  | `modules:create`, `modules:read`, `modules:update`, `modules:delete`, `modules:assign-roles`                |
| sessions | Nao requer roles especificas, apenas autenticacao (uid no token)                                            |
| auth     | Nao requer roles, endpoints publicos (login) ou apenas autenticacao (logout, refresh)                       |

### Recursos restritos ao system tenant

Operacoes de `roles`, `modules` e `tenants` sao restritas ao system tenant (`tenantId=1`). Para testar essa restricao:

```python
client.add_extra_data_token({"roles": ["roles:create"], "tenantId": 2}).post(...)
# Deve retornar 403 FORBIDDEN
```

---

## Simulacao de Relacionamentos ORM

Como os fake repositories nao possuem lazy loading do SQLAlchemy, os relacionamentos precisam ser populados manualmente.

### Relacionamentos que devem ser populados nos helpers `_create_*_in_db()`

| Entidade | Relacionamento   | Como popular                                                    |
| -------- | ---------------- | --------------------------------------------------------------- |
| User     | `user.tenant`    | `user.tenant = fake_tenant_repository.find_by_id(tenant_id)`    |
| User     | `user.attempts`  | Criar `LoginAttempt` e atribuir a `user.attempts`               |
| Session  | `session.user`   | Automatico via `FakeSessionRepository._attach_user()`           |
| Profile  | `profile.tenant` | `profile.tenant = fake_tenant_repository.find_by_id(tenant_id)` |

---

## Cuidados e Armadilhas

### Ordenacao de rotas no FastAPI

Rotas com paths fixos (ex: `/password`, `/validate-email`) DEVEM ser declaradas ANTES de rotas com parametros (ex: `/{user_id}`) no arquivo de routers. Caso contrario, o FastAPI ira capturar a rota fixa como se fosse um parametro.

```python
# CORRETO - rotas fixas primeiro
router.put("/password", ...)
router.post("/validate-email", ...)
router.get("/{user_id}", ...)

# INCORRETO - rota parametrizada captura tudo
router.get("/{user_id}", ...)
router.put("/password", ...)  # nunca sera alcancada
```

### Paginacao com page=0

NUNCA usar `page=0` nos testes. O calculo `(page - 1) * per_page` gera indice negativo. Sempre usar `page=1` como minimo.

### DELETE com body

O metodo `client.delete()` NAO aceita parametro `data`. Use `client.request("DELETE", ...)` com `content=dumps(data)`.

### Uso do `cast()`

Sempre usar `cast()` ao buscar entidades no fake repository apos operacoes de update, para garantir type safety:

```python
from typing import cast
updated_user = cast(User, fake_user_repository.find_by_id(user.id))
```

### Operador `and`/`or` em condicoes compostas

Cuidado com precedencia de operadores. `and` tem precedencia maior que `or`:

```python
# INCORRETO - precedencia errada
if self._repo and not hasattr(obj, "attr") or getattr(obj, "attr") is None:

# CORRETO - parenteses explicitos
if self._repo and (not hasattr(obj, "attr") or getattr(obj, "attr") is None):
```

---

## Checklist para Criar Testes de um Novo Projeto

1. Criar a estrutura de pastas `tests/`, `tests/api/`, `tests/fixtures/`, `tests/fixtures/fake_repositories/`.
2. Criar todos os `__init__.py` com o comentario `# pyright: reportUnusedImport=false`.
3. Criar os fake repositories para cada repositorio em `src/infra/repositories/`, seguindo a interface em `src/application/repositories/`.
4. Criar o `FakeRepositoryManager` com todas as properties e `clear_all_data()`.
5. Criar o `FakeIntegrationManager` se o projeto tiver integracoes externas.
6. Criar o `tests/fixtures/app.py` com a classe `Client` e fixture `client`.
7. Criar o `tests/fixtures/tenants.py` com a fixture `tenants`.
8. Criar o `tests/fixtures/mock_fake_repository_manager.py` com a fixture autouse.
9. Criar o `tests/conftest.py` importando as fixtures.
10. Criar os arquivos de teste em `tests/api/` para cada router.
11. Para cada endpoint, criar no minimo:
    - Teste de sucesso (happy path).
    - Teste sem permissao (403 FORBIDDEN).
    - Teste com recurso inexistente (404 NOT FOUND), quando aplicavel.
    - Teste com dados duplicados (409 CONFLICT), quando aplicavel.
    - Teste sem autenticacao (401 UNAUTHORIZED), quando aplicavel.
    - Teste de restricao ao system tenant, quando aplicavel.
12. Executar todos os testes e garantir que passam: `pytest --cov=./src --cov-report=html`.
