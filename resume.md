# Resumo das alteracoes para adaptacao do frontend

## 1) Mudanca principal em Work Policy Template

O template de jornada nao possui mais os campos unicos:

- `dailyWorkMinutes`
- `breakMinutes`

Agora o template usa lista por dia da semana:

- `workDayPolicies[]`
  - `weekDay`: `MONDAY | TUESDAY | WEDNESDAY | THURSDAY | FRIDAY | SATURDAY | SUNDAY`
  - `dailyWorkMinutes`
  - `breakMinutes`

### Impacto de API (work-policy-templates)

- `POST /work-policy-templates`
  - remove: `dailyWorkMinutes`, `breakMinutes`
  - adiciona: `workDayPolicies[]`
- `PUT /work-policy-templates/{templateId}`
  - remove: `dailyWorkMinutes`, `breakMinutes`
  - adiciona: `workDayPolicies[]` (quando enviado, substitui toda a lista atual)
- `GET /work-policy-templates/{templateId}` e `GET /work-policy-templates`
  - response agora retorna `workDayPolicies[]` com `id`, `weekDay`, `dailyWorkMinutes`, `breakMinutes`

### Validacoes novas de template

- `workDayPolicies` deve ter pelo menos 1 item
- nao pode repetir `weekDay`
- `dailyWorkMinutes > 0`
- `breakMinutes >= 0`
- `breakMinutes <= dailyWorkMinutes`

## 2) Novo modulo de calendario de feriados

Foi criado o router `holiday-calendars` com CRUD completo e vinculo de funcionario.

### Endpoints novos

- `POST /holiday-calendars`
- `GET /holiday-calendars/{holidayCalendarId}`
- `GET /holiday-calendars`
- `PUT /holiday-calendars/{holidayCalendarId}`
- `DELETE /holiday-calendars/{holidayCalendarId}`
- `GET /holiday-calendars/employees/{employeeId}/assignment`
- `PUT /holiday-calendars/employees/{employeeId}/assignment`
- `DELETE /holiday-calendars/employees/{employeeId}/assignment`

### Schemas principais

- `CreateHolidayCalendarRequest`
  - `tenantId`, `name`, `effectiveFrom`, `effectiveTo`, `national`, `city?`, `uf?`, `holidays[]`
- `UpdateHolidayCalendarRequest`
  - `name?`, `effectiveFrom?`, `effectiveTo?`, `national?`, `city?`, `uf?`, `holidays?`
- `HolidayCalendarResponse`
  - `id`, `tenantId`, `name`, `effectiveFrom`, `effectiveTo`, `national`, `city`, `uf`, `holidays[]`
- `AssignEmployeeHolidayCalendarRequest`
  - `holidayCalendarId`
- `EmployeeHolidayCalendarAssignmentResponse`
  - `id`, `employeeId`, `holidayCalendarId`

### Permissoes novas

- `holiday_calendars:create`
- `holiday_calendars:read`
- `holiday_calendars:edit`
- `holiday_calendars:delete`
- `holiday_calendars:*`

### Regras novas de calendario

- `effectiveFrom` e `effectiveTo` sao obrigatorios
- `effectiveTo >= effectiveFrom`
- se `national=true`, `city` e `uf` devem ser `null`
- se `national=false`, `city` e `uf` sao obrigatorios
- listagem de calendarios ganhou filtros opcionais por:
  - `effectiveFrom`
  - `effectiveTo`
  - `national`

## 3) Mudanca na regra de calculo diario (daily attendance)

O recálculo (`daily-attendance-summaries/recalculate`) mudou:

- passa a buscar jornada esperada pelo dia da semana dentro do template vigente
- se nao houver jornada configurada para o dia da semana, `expectedMinutes = 0`
- verifica se o funcionario possui calendario de feriados vinculado
- se a data for feriado nesse calendario, `expectedMinutes = 0`
- se houver trabalho com `expectedMinutes = 0`, gera banco de horas positivo
- quando `expectedMinutes = 0` e nao ha batidas, status pode ficar `OK` (sem obrigacao de jornada)

## 4) Impacto direto na interface frontend

### Tela de template de jornada

- trocar campos simples de minutos por grade/lista semanal (`workDayPolicies`)
- permitir selecionar os dias da semana trabalhados
- validar dias duplicados no client

### Nova tela/modulo de calendarios de feriado

- CRUD de calendario com lista de feriados (`date` + `name`)
- filtro por `name`, `city`, `uf`
- tela para vincular/desvincular calendario por `employeeId`

### Telas de resumo diario e banco de horas

- considerar que `expectedMinutes` pode ser `0` em:
  - dias sem jornada configurada
  - feriados do calendario vinculado
- exibir corretamente saldo positivo quando houver trabalho nesses dias

## 5) Alteracoes internas de dados (backend)

Foram introduzidas/alteradas entidades de dominio:

- `WorkPolicyTemplate` (agora com `work_day_policies`)
- `WorkDayPolicy` (novo)
- `HolidayCalendar` (novo)
- `Holiday` (novo)
- `EmployeeHolidayCalendarAssignment` (novo)

Observacao importante:

- nenhuma migration foi criada (conforme solicitado)
- para aplicar, o banco deve ser resetado e recriado com a nova estrutura

## 6) Documentacao atualizada

Arquivos atualizados/criados em `apis/`:

- `apis/work_policy_templates.md` (atualizado)
- `apis/daily_attendance_summaries.md` (atualizado)
- `apis/holiday_calendars.md` (novo)

## 7) Ajuste adicional: batidas somente IN e OUT

Foi aplicado o ajuste solicitado para restringir os tipos de batida:

- tipos aceitos agora: `IN` e `OUT`
- tipos removidos: `BREAK_START` e `BREAK_END`

### Impacto tecnico

- enums da API e dominio foram atualizados para aceitar apenas `IN` e `OUT`
- validacao de sequencia de batidas foi simplificada para alternancia `IN` -> `OUT`
- validacao de sequencia final em aplicacao de ajustes de ponto foi reativada com a regra `IN`/`OUT`
- criacao de batida agora valida se existe atribuicao de template de jornada vigente para o funcionario na data

### Impacto no calculo diario

- `workedMinutes` continua vindo da soma dos intervalos trabalhados (`IN` ate `OUT`)
- `breakMinutes` agora e derivado dos gaps entre um `OUT` e o proximo `IN` no mesmo dia

### Impacto de API/documentacao

- `apis/time_punches.md` atualizado com enums e regras novas
- `apis/time_adjustment_requests.md` atualizado para `proposedPunchType` com `IN`/`OUT`
- `POST /time-punches` agora retorna erro quando nao existe template de jornada vigente para a data
