# Bank Hours Ledgers API

Base path: `/bank-hours-ledgers`
Root path em producao: `/time-tracking-service/bank-hours-ledgers`

Permissoes:
- `bank_hours_ledgers:read` para obter, listar e consultar saldo.
- `bank_hours_ledgers:create` para criar lancamentos manuais.

Observacoes de tenant:
- Listagem aceita `tenantId` opcional (resolve_tenant_id).
- Endpoint por ID usa tenant do usuario autenticado.

Regras gerais:
- O banco de horas segue modelo ledger (movimentacoes).
- Cada lancamento possui `minutesDelta` (positivo ou negativo).
- Fontes suportadas: `DAILY_APURATION`, `MANUAL_ADJUST`, `ADJUSTMENT_REQUEST`.
- Nao e permitido criar lancamento com `minutesDelta = 0`.

---

## POST /bank-hours-ledgers

Descricao:
- Cria lancamento manual de banco de horas.

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `tenantId` | `int` | Sim | Tenant do lancamento |
| `employeeId` | `int` | Sim | ID do funcionario |
| `matricula` | `string` | Sim | Matricula do funcionario |
| `eventDate` | `date` | Sim | Data do evento |
| `minutesDelta` | `int` | Sim | Minutos de credito/debito |
| `source` | `string` enum | Sim | `DAILY_APURATION`, `MANUAL_ADJUST`, `ADJUSTMENT_REQUEST` |
| `referenceId` | `int` | Nao | Referencia externa (ex: resumo diario) |

Exemplo request:
```json
{
  "tenantId": 10,
  "employeeId": 501,
  "matricula": "MAT-0001",
  "eventDate": "2026-02-25",
  "minutesDelta": 30,
  "source": "MANUAL_ADJUST",
  "referenceId": null
}
```

Response:
- `201 Created`

```json
{
  "id": 3001
}
```

Erros comuns:
- `400`: `matricula is required.`
- `400`: `minutes_delta cannot be zero.`

---

## GET /bank-hours-ledgers/{entryId}

Descricao:
- Busca lancamento por ID.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `entryId` | `int` | Sim | ID do lancamento |

Response:
- `200 OK`

```json
{
  "id": 3001,
  "tenantId": 10,
  "employeeId": 501,
  "matricula": "MAT-0001",
  "eventDate": "2026-02-25",
  "minutesDelta": 30,
  "source": "MANUAL_ADJUST",
  "referenceId": null
}
```

Erros comuns:
- `404`: `Bank hours ledger entry not found.`
- `400`: `Ledger entry does not belong to tenant.`

---

## GET /bank-hours-ledgers

Descricao:
- Lista lancamentos por tenant/funcionario/matricula/periodo/fonte.

Query params:

| Campo | Tipo | Obrigatorio | Default | Descricao |
|---|---|---|---|---|
| `page` | `int` | Nao | `0` | Pagina |
| `perPage` | `int` | Nao | `20` | Itens por pagina |
| `employeeId` | `int` | Nao | - | Filtro por funcionario |
| `matricula` | `string` | Nao | - | Filtro por matricula |
| `startDate` | `date` | Nao | - | Inicio do periodo |
| `endDate` | `date` | Nao | - | Fim do periodo |
| `source` | `string` enum | Nao | - | Filtra por origem |
| `tenantId` | `int` | Nao | - | Tenant opcional para usuario tenant sistema |

Regras de filtro:
- Filtros sao cumulativos.
- Ordenacao por `eventDate desc`, depois `id desc`.

Response:
- `200 OK`

```json
{
  "data": [
    {
      "id": 3001,
      "tenantId": 10,
      "employeeId": 501,
      "matricula": "MAT-0001",
      "eventDate": "2026-02-25",
      "minutesDelta": 30,
      "source": "MANUAL_ADJUST",
      "referenceId": null
    }
  ],
  "count": 1,
  "page": 0
}
```

---

## GET /bank-hours-ledgers/balance

Descricao:
- Retorna saldo acumulado de banco de horas ate uma data.

Query params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `employeeId` | `int` | Sim | ID do funcionario |
| `matricula` | `string` | Sim | Matricula do funcionario |
| `untilDate` | `date` | Sim | Data limite para consolidacao do saldo |

Response:
- `200 OK`

```json
{
  "employeeId": 501,
  "matricula": "MAT-0001",
  "untilDate": "2026-02-25",
  "balanceMinutes": 120
}
```
