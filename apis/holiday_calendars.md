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
- `effectiveFrom` e obrigatorio.
- `effectiveTo` e obrigatorio.
- `effectiveTo` deve ser maior ou igual a `effectiveFrom`.
- `national` e opcional (default `false`).
- quando `national=true`, `city` e `uf` devem ser nulos.
- quando `national=false`, `city` e `uf` sao obrigatorios (`uf` deve ser uma UF valida).
- `holidays` aceita zero ou mais feriados.
- Nao e permitido repetir a mesma `date` dentro de `holidays`.
- Cada vinculo de calendario e identificado por `employeeId` + `matricula` dentro do tenant.

---

## POST /holiday-calendars

Descricao:

- Cria um calendario de feriados para um tenant.

Request body:

| Campo           | Tipo          | Obrigatorio           | Descricao                                                        |
| --------------- | ------------- | --------------------- | ---------------------------------------------------------------- |
| `tenantId`      | `int`         | Sim                   | Tenant dono do calendario                                        |
| `name`          | `string`      | Sim                   | Nome do calendario                                               |
| `effectiveFrom` | `date`        | Sim                   | Inicio de vigencia do calendario                                 |
| `effectiveTo`   | `date`        | Sim                   | Fim de vigencia do calendario                                    |
| `national`      | `bool`        | Nao (default `false`) | Indica calendario nacional                                       |
| `city`          | `string`      | Condicional           | Obrigatorio quando `national=false`; nulo quando `national=true` |
| `uf`            | `string` enum | Condicional           | Obrigatorio quando `national=false`; nulo quando `national=true` |
| `holidays`      | `array`       | Sim                   | Lista de feriados                                                |

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
  "effectiveFrom": "2026-01-01",
  "effectiveTo": "2026-12-31",
  "national": false,
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
- `400`: `effective_to must be greater than or equal to effective_from.`
- `400`: `city and uf must be null when national is true.`
- `400`: `Holiday calendar city is required when national is false.`
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
  "effectiveFrom": "2026-01-01",
  "effectiveTo": "2026-12-31",
  "national": false,
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

| Campo           | Tipo          | Obrigatorio | Default | Descricao                                         |
| --------------- | ------------- | ----------- | ------- | ------------------------------------------------- |
| `page`          | `int`         | Nao         | `0`     | Pagina (base 0)                                   |
| `perPage`       | `int`         | Nao         | `20`    | Itens por pagina (`1..1000`)                      |
| `name`          | `string`      | Nao         | -       | Filtro por nome (`ILIKE`)                         |
| `city`          | `string`      | Nao         | -       | Filtro por cidade (`ILIKE`)                       |
| `uf`            | `string` enum | Nao         | -       | Filtro por UF                                     |
| `effectiveFrom` | `date`        | Nao         | -       | Filtro por `effectiveFrom` (igualdade)            |
| `effectiveTo`   | `date`        | Nao         | -       | Filtro por `effectiveTo` (igualdade)              |
| `national`      | `bool`        | Nao         | -       | Filtro por calendario nacional                    |
| `tenantId`      | `int`         | Nao         | -       | Tenant opcional para usuario de tenant de sistema |

Response:

- `200 OK`

```json
{
  "data": [
    {
      "id": 91,
      "tenantId": 10,
      "name": "Calendario Sao Paulo",
      "effectiveFrom": "2026-01-01",
      "effectiveTo": "2026-12-31",
      "national": false,
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

| Campo           | Tipo          | Obrigatorio | Descricao                                                         |
| --------------- | ------------- | ----------- | ----------------------------------------------------------------- |
| `name`          | `string`      | Nao         | Novo nome                                                         |
| `effectiveFrom` | `date`        | Nao         | Novo inicio de vigencia                                           |
| `effectiveTo`   | `date`        | Nao         | Novo fim de vigencia                                              |
| `national`      | `bool`        | Nao         | Novo tipo de abrangencia                                          |
| `city`          | `string`      | Nao         | Nova cidade (obrigatorio no estado final quando `national=false`) |
| `uf`            | `string` enum | Nao         | Nova UF (obrigatorio no estado final quando `national=false`)     |
| `holidays`      | `array`       | Nao         | Nova lista completa de feriados (substitui a lista atual)         |

Response:

- `200 OK`

```json
{
  "id": 91,
  "tenantId": 10,
  "name": "Calendario Sao Paulo Atualizado",
  "effectiveFrom": "2026-01-01",
  "effectiveTo": "2026-12-31",
  "national": false,
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
- `400`: `effective_to must be greater than or equal to effective_from.`
- `400`: `city and uf must be null when national is true.`
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

- Consulta o calendario de feriados vinculado ao funcionario (`employeeId` + `matricula`) no tenant atual.

Path params:

| Campo        | Tipo  | Obrigatorio | Descricao         |
| ------------ | ----- | ----------- | ----------------- |
| `employeeId` | `int` | Sim         | ID do funcionario |

Query params:

| Campo | Tipo | Obrigatorio | Descricao |
| --- | --- | --- | --- |
| `matricula` | `string` | Sim | Matricula do funcionario |

Response:

- `200 OK`

```json
{
  "id": 55,
  "employeeId": 501,
  "matricula": "MAT-0001",
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
| `matricula`         | `string` | Sim      | Matricula do funcionario         |
| `holidayCalendarId` | `int` | Sim         | ID do calendario a ser vinculado |

Response:

- `200 OK`

```json
{
  "id": 55,
  "employeeId": 501,
  "matricula": "MAT-0001",
  "holidayCalendarId": 91
}
```

Erros comuns:

- `400`: `Holiday calendar does not belong to tenant.`
- `404`: `Holiday calendar not found.`

---

## PUT /holiday-calendars/{holidayCalendarId}/employees/assignments

Descricao:

- Cria ou atualiza em lote o vinculo de um calendario para varios funcionarios.

Path params:

| Campo | Tipo | Obrigatorio | Descricao |
| --- | --- | --- | --- |
| `holidayCalendarId` | `int` | Sim | ID do calendario a ser vinculado |

Request body:

| Campo | Tipo | Obrigatorio | Descricao |
| --- | --- | --- | --- |
| `employees` | `array` | Sim | Lista de funcionarios para vinculo |

Campos de `employees[]`:

| Campo | Tipo | Obrigatorio | Descricao |
| --- | --- | --- | --- |
| `employeeId` | `int` | Sim | ID do funcionario |
| `matricula` | `string` | Sim | Matricula do funcionario |

Response:

- `200 OK`

```json
[
  {
    "id": 55,
    "employeeId": 501,
    "matricula": "MAT-0001",
    "holidayCalendarId": 91
  },
  {
    "id": 56,
    "employeeId": 502,
    "matricula": "MAT-0002",
    "holidayCalendarId": 91
  }
]
```

Erros comuns:

- `400`: `employees list is required.`
- `400`: `matricula is required.`
- `400`: `Duplicated employeeId and matricula in employees list.`
- `400`: `Holiday calendar does not belong to tenant.`
- `404`: `Holiday calendar not found.`

---

## DELETE /holiday-calendars/employees/{employeeId}/assignment

Descricao:

- Remove o vinculo de calendario de feriados do funcionario (`employeeId` + `matricula`).

Path params:

| Campo        | Tipo  | Obrigatorio | Descricao         |
| ------------ | ----- | ----------- | ----------------- |
| `employeeId` | `int` | Sim         | ID do funcionario |

Query params:

| Campo | Tipo | Obrigatorio | Descricao |
| --- | --- | --- | --- |
| `matricula` | `string` | Sim | Matricula do funcionario |

Response:

- `200 OK`

```json
{
  "message": "Employee holiday calendar assignment removed successfully"
}
```

Erros comuns:

- `404`: `Employee holiday calendar assignment not found.`
