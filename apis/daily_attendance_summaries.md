# Daily Attendance Summaries API

Base path: `/daily-attendance-summaries`
Root path em producao: `/time-tracking-service/daily-attendance-summaries`

Permissoes:
- `daily_attendance_summaries:read` para obter e listar.
- `daily_attendance_summaries:edit` para recalculo.

Observacoes de tenant:
- Listagem aceita `tenantId` opcional (resolve_tenant_id).
- Endpoint por ID usa tenant do usuario autenticado.

Regras gerais:
- Resumo diario e materializado por matricula e data.
- Recalculo considera:
  - batidas do dia,
  - template vigente na data,
  - pendencias de ajuste.
- Status possiveis: `OK`, `INCOMPLETE`, `PENDING_ADJUSTMENT`, `NO_POLICY`.
- Quando status `OK`, o sistema pode gerar/atualizar lancamento automatico de banco de horas (`DAILY_APURATION`).

---

## POST /daily-attendance-summaries/recalculate

Descricao:
- Reprocessa o resumo diario para uma matricula e data especifica.

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `tenantId` | `int` | Sim | Tenant da operacao |
| `enrollmentId` | `int` | Sim | Matricula alvo |
| `workDate` | `date` | Sim | Data de apuracao |

Exemplo request:
```json
{
  "tenantId": 10,
  "enrollmentId": 123,
  "workDate": "2026-02-25"
}
```

Response:
- `200 OK`

```json
{
  "id": 700,
  "tenantId": 10,
  "enrollmentId": 123,
  "workDate": "2026-02-25",
  "expectedMinutes": 480,
  "workedMinutes": 485,
  "breakMinutes": 60,
  "overtimeMinutes": 5,
  "deficitMinutes": 0,
  "status": "OK"
}
```

Erros comuns:
- `400`: `Enrollment does not belong to tenant.`
- `404`: `Employee enrollment not found.`

---

## GET /daily-attendance-summaries/{summaryId}

Descricao:
- Busca resumo diario por ID.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `summaryId` | `int` | Sim | ID do resumo |

Response:
- `200 OK`

```json
{
  "id": 700,
  "tenantId": 10,
  "enrollmentId": 123,
  "workDate": "2026-02-25",
  "expectedMinutes": 480,
  "workedMinutes": 485,
  "breakMinutes": 60,
  "overtimeMinutes": 5,
  "deficitMinutes": 0,
  "status": "OK"
}
```

Erros comuns:
- `404`: `Daily attendance summary not found.`
- `400`: `Summary does not belong to tenant.`

---

## GET /daily-attendance-summaries

Descricao:
- Lista resumos diarios por periodo, matricula e status.

Query params:

| Campo | Tipo | Obrigatorio | Default | Descricao |
|---|---|---|---|---|
| `page` | `int` | Nao | `0` | Pagina |
| `perPage` | `int` | Nao | `20` | Itens por pagina |
| `enrollmentId` | `int` | Nao | - | Filtro por matricula |
| `startDate` | `date` | Nao | - | Inicio por data de trabalho |
| `endDate` | `date` | Nao | - | Fim por data de trabalho |
| `status` | `string` enum | Nao | - | `OK`, `INCOMPLETE`, `PENDING_ADJUSTMENT`, `NO_POLICY` |
| `tenantId` | `int` | Nao | - | Tenant opcional para usuario tenant sistema |

Regras de filtro:
- Filtros cumulativos (AND).
- Ordenacao por `workDate desc`.

Response:
- `200 OK`

```json
{
  "data": [
    {
      "id": 700,
      "tenantId": 10,
      "enrollmentId": 123,
      "workDate": "2026-02-25",
      "expectedMinutes": 480,
      "workedMinutes": 485,
      "breakMinutes": 60,
      "overtimeMinutes": 5,
      "deficitMinutes": 0,
      "status": "OK"
    }
  ],
  "count": 1,
  "page": 0
}
```
