# Employee Enrollments API

Base path: `/employee-enrollments`
Root path em producao: `/time-tracking-service/employee-enrollments`

Permissoes:
- `employee_enrollments:read` para obter e listar.
- `employee_enrollments:create` para criar.
- `employee_enrollments:edit` para atualizar.
- `employee_enrollments:write` para remover.

Observacoes de tenant:
- Endpoints de listagem aceitam `tenantId` opcional.
- O tenant efetivo segue a regra `resolve_tenant_id(current_user, tenantId)`.
- Endpoints por ID (`GET/PUT/DELETE`) usam o `tenant_id` do usuario autenticado.

Regras gerais:
- Matricula (`enrollmentCode`) e obrigatoria.
- `activeFrom` deve ser menor ou igual a `activeTo` quando `activeTo` for informado.
- `enrollmentCode` deve ser unico por tenant.
- Matricula inativa nao deve receber batidas ou ajustes (validado em outros modulos).

---

## POST /employee-enrollments

Descricao:
- Cria uma matricula (vinculo) no tenant informado.

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `tenantId` | `int` | Sim | Tenant dono da matricula |
| `employeeId` | `int` | Sim | ID global do funcionario no sistema externo |
| `enrollmentCode` | `string` | Sim | Codigo da matricula (unicidade por tenant) |
| `activeFrom` | `date` (`YYYY-MM-DD`) | Sim | Inicio de vigencia |
| `activeTo` | `date` (`YYYY-MM-DD`) | Nao | Fim de vigencia |
| `isActive` | `bool` | Nao (default `true`) | Situacao atual da matricula |

Exemplo request:
```json
{
  "tenantId": 10,
  "employeeId": 501,
  "enrollmentCode": "MAT-0001",
  "activeFrom": "2026-01-01",
  "activeTo": null,
  "isActive": true
}
```

Response:
- `201 Created`

```json
{
  "id": 123
}
```

Erros comuns:
- `400`: `Enrollment code is required.`
- `400`: `active_to must be greater than or equal to active_from.`
- `409`: `Enrollment code already exists for this tenant.`

---

## GET /employee-enrollments/{enrollmentId}

Descricao:
- Retorna os dados de uma matricula.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `enrollmentId` | `int` | Sim | ID da matricula |

Response:
- `200 OK`

```json
{
  "id": 123,
  "tenantId": 10,
  "employeeId": 501,
  "enrollmentCode": "MAT-0001",
  "activeFrom": "2026-01-01",
  "activeTo": null,
  "isActive": true
}
```

Erros comuns:
- `404`: `Employee enrollment not found.`
- `400`: `Enrollment does not belong to tenant.`

---

## GET /employee-enrollments

Descricao:
- Lista matriculas com paginacao e filtros opcionais.

Query params:

| Campo | Tipo | Obrigatorio | Default | Descricao |
|---|---|---|---|---|
| `page` | `int` | Nao | `0` | Pagina (base 0) |
| `perPage` | `int` | Nao | `20` | Itens por pagina (`1..100`) |
| `employeeId` | `int` | Nao | - | Filtra por funcionario |
| `enrollmentCode` | `string` | Nao | - | Filtro por trecho do codigo (`ILIKE`) |
| `isActive` | `bool` | Nao | - | Filtra por status |
| `tenantId` | `int` | Nao | - | Tenant opcional para usuario de tenant de sistema |

Regras de filtro:
- Filtros sao cumulativos (AND).
- `enrollmentCode` usa busca parcial case-insensitive.

Response:
- `200 OK`

```json
{
  "data": [
    {
      "id": 123,
      "tenantId": 10,
      "employeeId": 501,
      "enrollmentCode": "MAT-0001",
      "activeFrom": "2026-01-01",
      "activeTo": null,
      "isActive": true
    }
  ],
  "count": 1,
  "page": 0
}
```

---

## PUT /employee-enrollments/{enrollmentId}

Descricao:
- Atualiza campos da matricula.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `enrollmentId` | `int` | Sim | ID da matricula |

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `employeeId` | `int` | Nao | Novo ID do funcionario |
| `enrollmentCode` | `string` | Nao | Novo codigo da matricula |
| `activeFrom` | `date` | Nao | Nova data de inicio |
| `activeTo` | `date` | Nao | Nova data de fim |
| `isActive` | `bool` | Nao | Novo status |

Response:
- `200 OK`

```json
{
  "id": 123,
  "tenantId": 10,
  "employeeId": 501,
  "enrollmentCode": "MAT-0001",
  "activeFrom": "2026-01-01",
  "activeTo": null,
  "isActive": true
}
```

Erros comuns:
- `400`: `Enrollment does not belong to tenant.`
- `400`: `Enrollment code is required.`
- `400`: `active_to must be greater than or equal to active_from.`
- `409`: `Enrollment code already exists for this tenant.`

---

## DELETE /employee-enrollments/{enrollmentId}

Descricao:
- Remove a matricula.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `enrollmentId` | `int` | Sim | ID da matricula |

Response:
- `200 OK`

```json
{
  "message": "Employee enrollment deleted successfully"
}
```

Erros comuns:
- `400`: `Enrollment does not belong to tenant.`
- `404`: `Employee enrollment not found.`
