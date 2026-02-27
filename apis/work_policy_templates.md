# Work Policy Templates API

Base path: `/work-policy-templates`
Root path em producao: `/time-tracking-service/work-policy-templates`

Permissoes:
- `work_policy_templates:read` para obter e listar.
- `work_policy_templates:create` para criar.
- `work_policy_templates:edit` para atualizar.
- `work_policy_templates:write` para remover.

Observacoes de tenant:
- Listagem aceita `tenantId` opcional (resolve_tenant_id).
- Endpoints por ID usam tenant do usuario autenticado.

Regras gerais:
- `name` e obrigatorio e unico por tenant.
- `workDayPolicies` define a jornada por dia da semana.
- Cada dia da semana pode aparecer apenas uma vez em `workDayPolicies`.
- `dailyWorkMinutes` deve ser inteiro maior que zero.
- `breakMinutes` deve ser inteiro maior ou igual a zero.
- `breakMinutes` nao pode ser maior que `dailyWorkMinutes`.
- E obrigatorio informar pelo menos um item em `workDayPolicies`.

---

## POST /work-policy-templates

Descricao:
- Cria um template de jornada para um tenant.

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `tenantId` | `int` | Sim | Tenant dono do template |
| `name` | `string` | Sim | Nome amigavel do template |
| `workDayPolicies` | `array` | Sim | Lista de jornadas por dia da semana |

Campos de `workDayPolicies[]`:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `weekDay` | `string` enum | Sim | `MONDAY`, `TUESDAY`, `WEDNESDAY`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY` |
| `dailyWorkMinutes` | `int` | Sim | Carga esperada para o dia em minutos |
| `breakMinutes` | `int` | Sim | Intervalo padrao para o dia em minutos |

Exemplo request:
```json
{
  "tenantId": 10,
  "name": "Jornada Hibrida",
  "workDayPolicies": [
    {
      "weekDay": "MONDAY",
      "dailyWorkMinutes": 480,
      "breakMinutes": 60
    },
    {
      "weekDay": "TUESDAY",
      "dailyWorkMinutes": 300,
      "breakMinutes": 30
    }
  ]
}
```

Response:
- `201 Created`

```json
{
  "id": 80
}
```

Erros comuns:
- `400`: `Template name is required.`
- `400`: `daily_work_minutes must be greater than zero.`
- `400`: `break_minutes must be less than daily_work_minutes.`
- `409`: `Template name already exists for this tenant.`

---

## GET /work-policy-templates/{templateId}

Descricao:
- Busca um template por ID.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `templateId` | `int` | Sim | ID do template |

Response:
- `200 OK`

```json
{
  "id": 80,
  "tenantId": 10,
  "name": "Jornada Hibrida",
  "workDayPolicies": [
    {
      "id": 301,
      "weekDay": "MONDAY",
      "dailyWorkMinutes": 480,
      "breakMinutes": 60
    },
    {
      "id": 302,
      "weekDay": "TUESDAY",
      "dailyWorkMinutes": 300,
      "breakMinutes": 30
    }
  ]
}
```

Erros comuns:
- `404`: `Work policy template not found.`
- `400`: `Template does not belong to tenant.`

---

## GET /work-policy-templates

Descricao:
- Lista templates com paginacao e filtro por nome.

Query params:

| Campo | Tipo | Obrigatorio | Default | Descricao |
|---|---|---|---|---|
| `page` | `int` | Nao | `0` | Pagina (base 0) |
| `perPage` | `int` | Nao | `20` | Itens por pagina (`1..1000`) |
| `name` | `string` | Nao | - | Filtro por nome (`ILIKE`) |
| `tenantId` | `int` | Nao | - | Tenant opcional para usuario de tenant de sistema |

Response:
- `200 OK`

```json
{
  "data": [
    {
      "id": 80,
      "tenantId": 10,
      "name": "Jornada Hibrida",
      "workDayPolicies": [
        {
          "id": 301,
          "weekDay": "MONDAY",
          "dailyWorkMinutes": 480,
          "breakMinutes": 60
        },
        {
          "id": 302,
          "weekDay": "TUESDAY",
          "dailyWorkMinutes": 300,
          "breakMinutes": 30
        }
      ]
    }
  ],
  "count": 1,
  "page": 0
}
```

---

## PUT /work-policy-templates/{templateId}

Descricao:
- Atualiza um template existente.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `templateId` | `int` | Sim | ID do template |

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `name` | `string` | Nao | Novo nome |
| `workDayPolicies` | `array` | Nao | Nova lista completa de jornada por dia da semana (substitui a lista atual) |

Response:
- `200 OK`

```json
{
  "id": 80,
  "tenantId": 10,
  "name": "Jornada Hibrida",
  "workDayPolicies": [
    {
      "id": 301,
      "weekDay": "MONDAY",
      "dailyWorkMinutes": 480,
      "breakMinutes": 60
    },
    {
      "id": 302,
      "weekDay": "TUESDAY",
      "dailyWorkMinutes": 300,
      "breakMinutes": 30
    }
  ]
}
```

Erros comuns:
- `400`: `Template does not belong to tenant.`
- `400`: validacoes de minutos.
- `409`: `Template name already exists for this tenant.`

---

## DELETE /work-policy-templates/{templateId}

Descricao:
- Remove um template.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `templateId` | `int` | Sim | ID do template |

Response:
- `200 OK`

```json
{
  "message": "Work policy template deleted successfully"
}
```

Erros comuns:
- `400`: `Template does not belong to tenant.`
- `404`: `Work policy template not found.`
