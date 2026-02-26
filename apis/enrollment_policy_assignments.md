# Enrollment Policy Assignments API

Base path: `/enrollment-policy-assignments`
Root path em producao: `/time-tracking-service/enrollment-policy-assignments`

Permissoes:
- `enrollment_policy_assignments:read` para obter e listar.
- `enrollment_policy_assignments:create` para criar.
- `enrollment_policy_assignments:edit` para atualizar.
- `enrollment_policy_assignments:write` para remover.

Observacoes de tenant:
- Listagem aceita `tenantId` opcional (resolve_tenant_id).
- Endpoints por ID usam tenant do usuario autenticado.

Regras gerais:
- Vincula template de jornada a uma matricula com vigencia.
- `effectiveFrom` e obrigatorio.
- `effectiveTo` opcional, mas quando informado deve ser maior ou igual a `effectiveFrom`.
- Nao e permitido sobrepor periodos para a mesma matricula.
- Matricula e template devem pertencer ao mesmo tenant da operacao.

---

## POST /enrollment-policy-assignments

Descricao:
- Cria uma atribuicao de template para matricula.

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `tenantId` | `int` | Sim | Tenant da atribuicao |
| `enrollmentId` | `int` | Sim | ID da matricula |
| `templateId` | `int` | Sim | ID do template |
| `effectiveFrom` | `date` | Sim | Inicio da vigencia |
| `effectiveTo` | `date` | Nao | Fim da vigencia |

Response:
- `201 Created`

```json
{
  "id": 200
}
```

Erros comuns:
- `400`: `Enrollment does not belong to tenant.`
- `400`: `Template does not belong to tenant.`
- `400`: `effective_to must be greater than or equal to effective_from.`
- `409`: `Assignment period overlaps with an existing assignment.`

---

## GET /enrollment-policy-assignments/{assignmentId}

Descricao:
- Busca atribuicao por ID.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `assignmentId` | `int` | Sim | ID da atribuicao |

Response:
- `200 OK`

```json
{
  "id": 200,
  "tenantId": 10,
  "enrollmentId": 123,
  "templateId": 80,
  "effectiveFrom": "2026-01-01",
  "effectiveTo": null
}
```

Erros comuns:
- `404`: `Enrollment policy assignment not found.`
- `400`: `Assignment does not belong to tenant.`

---

## GET /enrollment-policy-assignments

Descricao:
- Lista atribuicoes com filtros por matricula, template e data-alvo.

Query params:

| Campo | Tipo | Obrigatorio | Default | Descricao |
|---|---|---|---|---|
| `page` | `int` | Nao | `0` | Pagina |
| `perPage` | `int` | Nao | `20` | Itens por pagina |
| `enrollmentId` | `int` | Nao | - | Filtro por matricula |
| `templateId` | `int` | Nao | - | Filtro por template |
| `targetDate` | `date` | Nao | - | Filtra atribuicoes vigentes na data |
| `tenantId` | `int` | Nao | - | Tenant opcional para usuario tenant sistema |

Regras de filtro:
- Filtros sao cumulativos.
- `targetDate` aplica regra de vigencia (`effectiveFrom <= targetDate <= effectiveTo` ou `effectiveTo null`).

Response:
- `200 OK`

```json
{
  "data": [
    {
      "id": 200,
      "tenantId": 10,
      "enrollmentId": 123,
      "templateId": 80,
      "effectiveFrom": "2026-01-01",
      "effectiveTo": null
    }
  ],
  "count": 1,
  "page": 0
}
```

---

## PUT /enrollment-policy-assignments/{assignmentId}

Descricao:
- Atualiza template e/ou vigencia da atribuicao.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `assignmentId` | `int` | Sim | ID da atribuicao |

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `templateId` | `int` | Nao | Novo template |
| `effectiveFrom` | `date` | Nao | Novo inicio |
| `effectiveTo` | `date` | Nao | Novo fim |

Response:
- `200 OK`

```json
{
  "id": 200,
  "tenantId": 10,
  "enrollmentId": 123,
  "templateId": 80,
  "effectiveFrom": "2026-01-01",
  "effectiveTo": null
}
```

Erros comuns:
- `400`: `Assignment does not belong to tenant.`
- `400`: `Template does not belong to tenant.`
- `409`: sobreposicao de periodo.

---

## DELETE /enrollment-policy-assignments/{assignmentId}

Descricao:
- Remove uma atribuicao de template.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `assignmentId` | `int` | Sim | ID da atribuicao |

Response:
- `200 OK`

```json
{
  "message": "Enrollment policy assignment deleted successfully"
}
```

Erros comuns:
- `400`: `Assignment does not belong to tenant.`
- `404`: `Enrollment policy assignment not found.`
