# Holiday Calendars API

Base path: `/holiday-calendars`
Root path em producao: `/time-tracking-service/holiday-calendars`

Permissoes:

- `holiday_calendars:read` para obter e listar.
- `holiday_calendars:create` para criar.
- `holiday_calendars:edit` para atualizar e vincular funcionario.
- `holiday_calendars:delete` para remover e desvincular funcionario.

Observacoes de tenant:

- Listagem aceita `tenantId` opcional (resolve_tenant_id).
- Endpoints por ID usam tenant do usuario autenticado.
- Vinculo funcionario-calendario tambem respeita tenant do usuario autenticado.

Regras gerais:

- `name` e obrigatorio e unico por tenant.
- `city` e obrigatorio.
- `uf` e obrigatorio e deve ser um valor valido de UF.
- `holidays` aceita zero ou mais feriados.
- Nao e permitido repetir a mesma `date` dentro de `holidays`.
- Cada funcionario possui no maximo um calendario vinculado por tenant.

---

## POST /holiday-calendars

Descricao:

- Cria um calendario de feriados para um tenant.

Request body:

| Campo      | Tipo          | Obrigatorio | Descricao                        |
| ---------- | ------------- | ----------- | -------------------------------- |
| `tenantId` | `int`         | Sim         | Tenant dono do calendario        |
| `name`     | `string`      | Sim         | Nome do calendario               |
| `city`     | `string`      | Sim         | Cidade de referencia             |
| `uf`       | `string` enum | Sim         | UF (`AC`, `AL`, `AP`, ..., `TO`) |
| `holidays` | `array`       | Sim         | Lista de feriados                |

Campos de `holidays[]`:

| Campo  | Tipo     | Obrigatorio | Descricao       |
| ------ | -------- | ----------- | --------------- |
| `date` | `date`   | Sim         | Data do feriado |
| `name` | `string` | Sim         | Nome do feriado |

Exemplo request:

```json
{
  "tenantId": 10,
  "name": "Calendario Sao Paulo",
  "city": "Sao Paulo",
  "uf": "SP",
  "holidays": [
    {
      "date": "2026-01-01",
      "name": "Confraternizacao Universal"
    },
    {
      "date": "2026-04-21",
      "name": "Tiradentes"
    }
  ]
}
```

Response:

- `201 Created`

```json
{
  "id": 91
}
```

Erros comuns:

- `400`: `Holiday calendar name is required.`
- `400`: `Holiday calendar city is required.`
- `400`: `Holiday name is required.`
- `400`: `Duplicated holiday date in holiday calendar.`
- `409`: `Holiday calendar name already exists for this tenant.`

---

## GET /holiday-calendars/{holidayCalendarId}

Descricao:

- Busca calendario de feriados por ID.

Path params:

| Campo               | Tipo  | Obrigatorio | Descricao        |
| ------------------- | ----- | ----------- | ---------------- |
| `holidayCalendarId` | `int` | Sim         | ID do calendario |

Response:

- `200 OK`

```json
{
  "id": 91,
  "tenantId": 10,
  "name": "Calendario Sao Paulo",
  "city": "Sao Paulo",
  "uf": "SP",
  "holidays": [
    {
      "id": 601,
      "date": "2026-01-01",
      "name": "Confraternizacao Universal"
    },
    {
      "id": 602,
      "date": "2026-04-21",
      "name": "Tiradentes"
    }
  ]
}
```

Erros comuns:

- `404`: `Holiday calendar not found.`
- `400`: `Holiday calendar does not belong to tenant.`

---

## GET /holiday-calendars

Descricao:

- Lista calendarios de feriados com paginacao e filtros.

Query params:

| Campo      | Tipo          | Obrigatorio | Default | Descricao                                         |
| ---------- | ------------- | ----------- | ------- | ------------------------------------------------- |
| `page`     | `int`         | Nao         | `0`     | Pagina (base 0)                                   |
| `perPage`  | `int`         | Nao         | `20`    | Itens por pagina (`1..1000`)                      |
| `name`     | `string`      | Nao         | -       | Filtro por nome (`ILIKE`)                         |
| `city`     | `string`      | Nao         | -       | Filtro por cidade (`ILIKE`)                       |
| `uf`       | `string` enum | Nao         | -       | Filtro por UF                                     |
| `tenantId` | `int`         | Nao         | -       | Tenant opcional para usuario de tenant de sistema |

Response:

- `200 OK`

```json
{
  "data": [
    {
      "id": 91,
      "tenantId": 10,
      "name": "Calendario Sao Paulo",
      "city": "Sao Paulo",
      "uf": "SP",
      "holidays": [
        {
          "id": 601,
          "date": "2026-01-01",
          "name": "Confraternizacao Universal"
        }
      ]
    }
  ],
  "count": 1,
  "page": 0
}
```

---

## PUT /holiday-calendars/{holidayCalendarId}

Descricao:

- Atualiza dados do calendario de feriados.

Path params:

| Campo               | Tipo  | Obrigatorio | Descricao        |
| ------------------- | ----- | ----------- | ---------------- |
| `holidayCalendarId` | `int` | Sim         | ID do calendario |

Request body:

| Campo      | Tipo          | Obrigatorio | Descricao                                                 |
| ---------- | ------------- | ----------- | --------------------------------------------------------- |
| `name`     | `string`      | Nao         | Novo nome                                                 |
| `city`     | `string`      | Nao         | Nova cidade                                               |
| `uf`       | `string` enum | Nao         | Nova UF                                                   |
| `holidays` | `array`       | Nao         | Nova lista completa de feriados (substitui a lista atual) |

Response:

- `200 OK`

```json
{
  "id": 91,
  "tenantId": 10,
  "name": "Calendario Sao Paulo Atualizado",
  "city": "Sao Paulo",
  "uf": "SP",
  "holidays": [
    {
      "id": 701,
      "date": "2026-01-01",
      "name": "Confraternizacao Universal"
    }
  ]
}
```

Erros comuns:

- `400`: `Holiday calendar does not belong to tenant.`
- `400`: `Duplicated holiday date in holiday calendar.`
- `409`: `Holiday calendar name already exists for this tenant.`

---

## DELETE /holiday-calendars/{holidayCalendarId}

Descricao:

- Remove calendario de feriados.

Path params:

| Campo               | Tipo  | Obrigatorio | Descricao        |
| ------------------- | ----- | ----------- | ---------------- |
| `holidayCalendarId` | `int` | Sim         | ID do calendario |

Response:

- `200 OK`

```json
{
  "message": "Holiday calendar deleted successfully"
}
```

Erros comuns:

- `400`: `Holiday calendar does not belong to tenant.`
- `404`: `Holiday calendar not found.`

---

## GET /holiday-calendars/employees/{employeeId}/assignment

Descricao:

- Consulta o calendario de feriados vinculado ao funcionario no tenant atual.

Path params:

| Campo        | Tipo  | Obrigatorio | Descricao         |
| ------------ | ----- | ----------- | ----------------- |
| `employeeId` | `int` | Sim         | ID do funcionario |

Response:

- `200 OK`

```json
{
  "id": 55,
  "employeeId": 501,
  "holidayCalendarId": 91
}
```

Erros comuns:

- `404`: `Employee holiday calendar assignment not found.`

---

## PUT /holiday-calendars/employees/{employeeId}/assignment

Descricao:

- Cria ou atualiza o vinculo de calendario de feriados para o funcionario.

Path params:

| Campo        | Tipo  | Obrigatorio | Descricao         |
| ------------ | ----- | ----------- | ----------------- |
| `employeeId` | `int` | Sim         | ID do funcionario |

Request body:

| Campo               | Tipo  | Obrigatorio | Descricao                        |
| ------------------- | ----- | ----------- | -------------------------------- |
| `holidayCalendarId` | `int` | Sim         | ID do calendario a ser vinculado |

Response:

- `200 OK`

```json
{
  "id": 55,
  "employeeId": 501,
  "holidayCalendarId": 91
}
```

Erros comuns:

- `400`: `Holiday calendar does not belong to tenant.`
- `404`: `Holiday calendar not found.`

---

## DELETE /holiday-calendars/employees/{employeeId}/assignment

Descricao:

- Remove o vinculo de calendario de feriados do funcionario.

Path params:

| Campo        | Tipo  | Obrigatorio | Descricao         |
| ------------ | ----- | ----------- | ----------------- |
| `employeeId` | `int` | Sim         | ID do funcionario |

Response:

- `200 OK`

```json
{
  "message": "Employee holiday calendar assignment removed successfully"
}
```

Erros comuns:

- `404`: `Employee holiday calendar assignment not found.`
