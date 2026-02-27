# Time Punches API

Base path: `/time-punches`
Root path em producao: `/time-tracking-service/time-punches`

Permissoes:
- `time_punches:read` para consultar batidas.
- `time_punches:create` para criar batidas.
- `time_punches:write` para remover batidas.

Observacoes de tenant:
- Listagem aceita `tenantId` opcional (resolve_tenant_id).
- Endpoints por ID usam tenant do usuario autenticado.

Regras gerais:
- Batida e vinculada a `employeeId` + `matricula`.
- Tipos validos: `IN`, `OUT`.
- Nao permite duplicidade exata (`employeeId + matricula + punchedAt + punchType`).
- Valida sequencia de eventos para evitar conflitos:
  - `IN` nao pode repetir sem `OUT`.
  - `OUT` exige jornada aberta.
- Intervalos passam a ser representados por pares `OUT` (saida) e `IN` (retorno).
- Se `allowMultiEnrollmentPerDay=false`, bloqueia batidas em outra matricula do mesmo funcionario no mesmo dia.
- O funcionario so pode registrar batida se tiver uma atribuicao de template de jornada vigente na data.
- Ao criar/remover batida, o sistema reapura resumo diario automaticamente.

---

## POST /time-punches

Descricao:
- Registra uma nova batida.

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `tenantId` | `int` | Sim | Tenant da operacao |
| `employeeId` | `int` | Sim | ID do funcionario |
| `matricula` | `string` | Sim | Matricula do funcionario |
| `punchedAt` | `datetime` ISO-8601 | Sim | Data/hora da batida |
| `punchType` | `string` enum | Sim | `IN`, `OUT` |
| `source` | `string` | Nao (default `web`) | Origem da batida |
| `note` | `string` | Nao | Observacao livre |
| `allowMultiEnrollmentPerDay` | `bool` | Nao (default `true`) | Permite batidas em outras matriculas no mesmo dia |

Exemplo request:
```json
{
  "tenantId": 10,
  "employeeId": 501,
  "matricula": "MAT-0001",
  "punchedAt": "2026-02-25T08:00:00Z",
  "punchType": "IN",
  "source": "web",
  "note": "Entrada normal",
  "allowMultiEnrollmentPerDay": true
}
```

Response:
- `201 Created`

```json
{
  "id": 9001
}
```

Erros comuns:
- `400`: `matricula is required.`
- `400`: `Employee does not have a work policy assignment for this date.`
- `400`: conflitos de sequencia (`Invalid sequence: ...`).
- `400`: `Employee cannot register punches in multiple matriculas in the same day.`
- `409`: `There is already a punch with the same date, time and type.`

---

## GET /time-punches/{punchId}

Descricao:
- Busca batida por ID.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `punchId` | `int` | Sim | ID da batida |

Response:
- `200 OK`

```json
{
  "id": 9001,
  "tenantId": 10,
  "employeeId": 501,
  "matricula": "MAT-0001",
  "punchedAt": "2026-02-25T08:00:00Z",
  "punchType": "IN",
  "source": "web",
  "note": "Entrada normal"
}
```

Erros comuns:
- `404`: `Time punch not found.`
- `400`: `Punch does not belong to tenant.`

---

## GET /time-punches

Descricao:
- Lista batidas com filtros e paginacao.

Query params:

| Campo | Tipo | Obrigatorio | Default | Descricao |
|---|---|---|---|---|
| `page` | `int` | Nao | `0` | Pagina |
| `perPage` | `int` | Nao | `20` | Itens por pagina |
| `employeeId` | `int` | Nao | - | Filtro por funcionario |
| `matricula` | `string` | Nao | - | Filtro por matricula |
| `startAt` | `datetime` | Nao | - | Inicio do intervalo |
| `endAt` | `datetime` | Nao | - | Fim do intervalo |
| `punchType` | `string` enum | Nao | - | `IN`, `OUT` |
| `tenantId` | `int` | Nao | - | Tenant opcional para usuario tenant sistema |

Regras de filtro:
- Filtros sao cumulativos.
- Ordenacao por `punchedAt` desc.

Response:
- `200 OK`

```json
{
  "data": [
    {
      "id": 9001,
      "tenantId": 10,
      "employeeId": 501,
      "matricula": "MAT-0001",
      "punchedAt": "2026-02-25T08:00:00Z",
      "punchType": "IN",
      "source": "web",
      "note": "Entrada normal"
    }
  ],
  "count": 1,
  "page": 0
}
```

---

## DELETE /time-punches/{punchId}

Descricao:
- Remove batida por ID e reapura o dia da matricula.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---|---|
| `punchId` | `int` | Sim | ID da batida |

Response:
- `200 OK`

```json
{
  "message": "Time punch deleted successfully"
}
```

Erros comuns:
- `404`: `Time punch not found.`
- `400`: `Punch does not belong to tenant.`
