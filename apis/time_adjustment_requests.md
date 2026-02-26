# Time Adjustment Requests API

Base path: `/time-adjustment-requests`
Root path em producao: `/time-tracking-service/time-adjustment-requests`

Permissoes:
- `time_adjustment_requests:read` para obter e listar.
- `time_adjustment_requests:create` para criar solicitacao.
- `time_adjustment_requests:edit` para decidir e aplicar.
- `time_adjustment_requests:write` para cancelar/remover.

Observacoes de tenant:
- Listagem aceita `tenantId` opcional (resolve_tenant_id).
- Endpoints por ID usam tenant do usuario autenticado.

Workflow de status:
- `PENDING` (inicial)
- `APPROVED`
- `REJECTED`
- `APPLIED`

Regras gerais:
- Solicita ajuste para uma matricula e uma data (`requestDate`).
- Deve conter ao menos um item.
- Item novo exige `proposedPunchType` e `proposedPunchedAt`.
- `proposedPunchedAt` deve pertencer ao `requestDate`.
- Se `originalPunchId` informado, a batida original deve pertencer a matricula da solicitacao.
- Decisao so e permitida para status `PENDING`.
- Aplicacao so e permitida para status `APPROVED`.
- Aplicacao reapura dias afetados.

---

## POST /time-adjustment-requests

Descricao:
- Cria solicitacao de ajuste de ponto.

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `tenantId` | `int` | Sim | Tenant da solicitacao |
| `enrollmentId` | `int` | Sim | Matricula alvo |
| `requestDate` | `date` | Sim | Data do ajuste |
| `requestType` | `string` enum | Sim | `ADD_PUNCH`, `EDIT_PUNCH`, `JUSTIFY_ABSENCE`, `REMOVE_PUNCH` |
| `reason` | `string` | Sim | Justificativa textual |
| `requesterUserId` | `int` | Sim | Usuario solicitante |
| `items` | `array` | Sim | Itens de ajuste |

Campos de cada item (`items[]`):

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `proposedPunchType` | `string` enum | Condicional | Tipo proposto (`IN`, `OUT`, `BREAK_START`, `BREAK_END`) |
| `proposedPunchedAt` | `datetime` | Condicional | Data/hora proposta |
| `originalPunchId` | `int` | Condicional | Batida original (edicao/remocao) |
| `note` | `string` | Nao | Observacao do item |

Regra condicional:
- Para incluir nova batida (`originalPunchId` ausente), `proposedPunchType` e `proposedPunchedAt` sao obrigatorios.

Exemplo request:
```json
{
  "tenantId": 10,
  "enrollmentId": 123,
  "requestDate": "2026-02-25",
  "requestType": "ADD_PUNCH",
  "reason": "Esqueci de registrar entrada",
  "requesterUserId": 901,
  "items": [
    {
      "proposedPunchType": "IN",
      "proposedPunchedAt": "2026-02-25T08:00:00Z",
      "originalPunchId": null,
      "note": "Entrada esquecida"
    }
  ]
}
```

Response:
- `201 Created`

```json
{
  "id": 450
}
```

Erros comuns:
- `400`: `Inactive enrollment cannot receive adjustments.`
- `400`: `At least one adjustment item is required.`
- `400`: validacoes dos itens (`proposed` obrigatorio, data divergente, duplicado).
- `404`: `Time punch not found.` (quando `originalPunchId` invalido)

---

## GET /time-adjustment-requests/{requestId}

Descricao:
- Busca solicitacao por ID, incluindo itens.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `requestId` | `int` | Sim | ID da solicitacao |

Response:
- `200 OK`

```json
{
  "id": 450,
  "tenantId": 10,
  "enrollmentId": 123,
  "requestDate": "2026-02-25",
  "requestType": "ADD_PUNCH",
  "status": "PENDING",
  "reason": "Esqueci de registrar entrada",
  "requesterUserId": 901,
  "decidedAt": null,
  "decidedByUserId": null,
  "decisionReason": null,
  "items": [
    {
      "id": 1,
      "requestId": 450,
      "proposedPunchType": "IN",
      "proposedPunchedAt": "2026-02-25T08:00:00Z",
      "originalPunchId": null,
      "note": "Entrada esquecida"
    }
  ]
}
```

Erros comuns:
- `404`: `Time adjustment request not found.`
- `400`: `Request does not belong to tenant.`

---

## GET /time-adjustment-requests

Descricao:
- Lista solicitacoes com filtros e paginacao.

Query params:

| Campo | Tipo | Obrigatorio | Default | Descricao |
|---|---|---|---|---|
| `page` | `int` | Nao | `0` | Pagina |
| `perPage` | `int` | Nao | `20` | Itens por pagina |
| `enrollmentId` | `int` | Nao | - | Filtro por matricula |
| `status` | `string` enum | Nao | - | `PENDING`, `APPROVED`, `REJECTED`, `APPLIED` |
| `startDate` | `date` | Nao | - | Inicio por `requestDate` |
| `endDate` | `date` | Nao | - | Fim por `requestDate` |
| `tenantId` | `int` | Nao | - | Tenant opcional para usuario tenant sistema |

Response:
- `200 OK`

```json
{
  "data": [
    {
      "id": 450,
      "tenantId": 10,
      "enrollmentId": 123,
      "requestDate": "2026-02-25",
      "requestType": "ADD_PUNCH",
      "status": "PENDING",
      "reason": "Esqueci de registrar entrada",
      "requesterUserId": 901,
      "decidedAt": null,
      "decidedByUserId": null,
      "decisionReason": null,
      "items": []
    }
  ],
  "count": 1,
  "page": 0
}
```

---

## PATCH /time-adjustment-requests/{requestId}/decision

Descricao:
- Aprova ou rejeita solicitacao pendente.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `requestId` | `int` | Sim | ID da solicitacao |

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `status` | `string` enum | Sim | `APPROVED` ou `REJECTED` |
| `decidedByUserId` | `int` | Sim | Usuario que decidiu |
| `decisionReason` | `string` | Condicional | Obrigatorio quando `status=REJECTED` |

Exemplo request:
```json
{
  "status": "APPROVED",
  "decidedByUserId": 902,
  "decisionReason": null
}
```

Response:
- `200 OK`
- Retorna payload completo de `TimeAdjustmentRequestResponse`.

Erros comuns:
- `400`: `Only pending requests can be decided.`
- `400`: `Decision status must be APPROVED or REJECTED.`
- `400`: `decision_reason is required for rejection.`

---

## PATCH /time-adjustment-requests/{requestId}/apply

Descricao:
- Aplica solicitacao aprovada, materializando itens em batidas e reapurando dias afetados.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `requestId` | `int` | Sim | ID da solicitacao |

Comportamento:
- Se `originalPunchId` + `proposed*`: atualiza batida existente.
- Se `originalPunchId` sem `proposed*`: remove batida existente.
- Sem `originalPunchId` + `proposed*`: cria nova batida.
- Atualiza status para `APPLIED`.
- Reprocessa resumo diario para todas as datas impactadas.

Response:
- `200 OK`
- Retorna payload completo de `TimeAdjustmentRequestResponse` com status final.

Erros comuns:
- `400`: `Only approved requests can be applied.`
- `400`: sequencia final invalida de batidas.
- `404`: `Time punch not found.` (item com referencia invalida)

---

## DELETE /time-adjustment-requests/{requestId}

Descricao:
- Cancela e remove solicitacao pendente.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `requestId` | `int` | Sim | ID da solicitacao |

Response:
- `200 OK`

```json
{
  "message": "Time adjustment request deleted successfully"
}
```

Erros comuns:
- `400`: `Only pending requests can be cancelled.`
- `400`: `Request does not belong to tenant.`
- `404`: `Time adjustment request not found.`
