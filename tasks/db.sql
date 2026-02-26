CREATE TABLE IF NOT EXISTS employee_enrollment (
    id               SERIAL      PRIMARY KEY,
    tenant_id        INTEGER     NOT NULL,
    employee_id      INTEGER     NOT NULL,  -- ID global vindo do sistema externo
    matricula        TEXT NOT NULL,  -- matrícula / código do vínculo externo
    active_from      DATE        NOT NULL,
    active_to        DATE        NULL,
    is_active        BOOLEAN     NOT NULL DEFAULT 1,

    created_at       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Unicidade da matrícula dentro do tenant
    CONSTRAINT uq_enrollment_tenant_matricula
        UNIQUE (tenant_id, matricula),

    -- Opcional: evitar duplicidade do mesmo vínculo para o mesmo funcionário
    CONSTRAINT uq_enrollment_tenant_employee_matricula
        UNIQUE (tenant_id, employee_id, matricula)
);

CREATE INDEX IF NOT EXISTS idx_enrollment_tenant
ON employee_enrollment (tenant_id);

CREATE INDEX IF NOT EXISTS idx_enrollment_employee
ON employee_enrollment (tenant_id, employee_id);

CREATE INDEX IF NOT EXISTS idx_enrollment_active_period
ON employee_enrollment (tenant_id, active_from, active_to);


-- =========================================================
-- 2) Templates (políticas de jornada)
-- =========================================================
CREATE TABLE IF NOT EXISTS work_policy_template (
  id                 SERIAL      PRIMARY KEY,
  tenant_id           INTEGER     NOT NULL,
  name               TEXT        NOT NULL,
  daily_work_minutes  INTEGER     NOT NULL,
  break_minutes       INTEGER     NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_template_tenant_name
  ON work_policy_template (tenant_id, name);

CREATE INDEX IF NOT EXISTS idx_template_tenant
  ON work_policy_template (tenant_id);

-- =========================================================
-- 3) Atribuição de template por matrícula (com vigência)
-- =========================================================
CREATE TABLE IF NOT EXISTS enrollment_policy_assignment (
  id            SERIAL      PRIMARY KEY,
  tenant_id      INTEGER     NOT NULL,
  enrollment_id  INTEGER     NOT NULL,
  template_id    INTEGER     NOT NULL,
  effective_from DATE        NOT NULL,
  effective_to   DATE        NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT fk_assignment_enrollment
    FOREIGN KEY (enrollment_id)
    REFERENCES employee_enrollment (id)
    ON DELETE CASCADE,

  CONSTRAINT fk_assignment_template
    FOREIGN KEY (template_id)
    REFERENCES work_policy_template (id)
    ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_assignment_enrollment_effective
  ON enrollment_policy_assignment (enrollment_id, effective_from);

-- =========================================================
-- 4) Batidas (vinculadas à matrícula)
-- =========================================================
CREATE TABLE IF NOT EXISTS time_punch (
  id            SERIAL      PRIMARY KEY,
  tenant_id      INTEGER     NOT NULL,
  enrollment_id  INTEGER     NOT NULL,
  punched_at     TIMESTAMPTZ NOT NULL,
  punch_type     TEXT        NOT NULL,

  source         TEXT        NOT NULL DEFAULT 'web',
  note           TEXT        NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT fk_punch_enrollment
    FOREIGN KEY (enrollment_id)
    REFERENCES employee_enrollment (id)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_punch_enrollment_time
  ON time_punch (enrollment_id, punched_at);

-- Evita duplicação exata de batida no mesmo instante para a mesma matrícula
CREATE UNIQUE INDEX IF NOT EXISTS uq_punch_enrollment_time_type
  ON time_punch (enrollment_id, punched_at, punch_type);

-- =========================================================
-- 5) Solicitações de ajuste (esqueci de bater ponto)
-- =========================================================
CREATE TABLE IF NOT EXISTS time_adjustment_request (
  id             SERIAL      PRIMARY KEY,
  tenant_id       INTEGER     NOT NULL,
  enrollment_id   INTEGER     NOT NULL,
  request_date    DATE        NOT NULL,
  type            TEXT        NOT NULL, -- ex.: ADD_PUNCH/EDIT_PUNCH/JUSTIFY_ABSENCE
  status          TEXT        NOT NULL DEFAULT 'PENDING', -- Ex.: PENDING/APPROVED/REJECTED (controlar na aplicação)
  reason          TEXT        NOT NULL,
  created_by      INTEGER     NOT NULL, -- ID do usuário (auth/employee)
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  decided_at      TIMESTAMPTZ NULL,
  decided_by      INTEGER     NULL,
  decision_reason TEXT        NULL,

  CONSTRAINT fk_adjustment_enrollment
    FOREIGN KEY (enrollment_id)
    REFERENCES employee_enrollment (id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS time_adjustment_item (
  id                 SERIAL      PRIMARY KEY,
  tenant_id           INTEGER     NOT NULL,
  request_id          INTEGER     NOT NULL,
  proposed_punch_type TEXT        NULL,
  proposed_punched_at TIMESTAMPTZ NULL,
  original_punch_id   INTEGER     NULL,
  note               TEXT        NULL,

  CONSTRAINT fk_adjustment_item_request
    FOREIGN KEY (request_id)
    REFERENCES time_adjustment_request (id)
    ON DELETE CASCADE,

  CONSTRAINT fk_adjustment_item_original_punch
    FOREIGN KEY (original_punch_id)
    REFERENCES time_punch (id)
    ON DELETE SET NULL
);

-- =========================================================
-- 6) Resumo diário (apuração materializada)
-- =========================================================
CREATE TABLE IF NOT EXISTS daily_attendance_summary (
  id              SERIAL      PRIMARY KEY,
  tenant_id        INTEGER     NOT NULL,
  enrollment_id    INTEGER     NOT NULL,
  work_date        DATE        NOT NULL,
  expected_minutes INTEGER     NOT NULL,
  worked_minutes   INTEGER     NOT NULL,
  break_minutes    INTEGER     NOT NULL,
  overtime_minutes INTEGER     NOT NULL,
  deficit_minutes  INTEGER     NOT NULL,
  status           TEXT        NOT NULL DEFAULT 'OK',
  calculated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT fk_daily_enrollment
    FOREIGN KEY (enrollment_id)
    REFERENCES employee_enrollment (id)
    ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_daily_enrollment_date
  ON daily_attendance_summary (enrollment_id, work_date);

-- =========================================================
-- 7) Banco de horas (ledger)
-- =========================================================
CREATE TABLE IF NOT EXISTS bank_hours_ledger (
  id            SERIAL      PRIMARY KEY,
  tenant_id      INTEGER     NOT NULL,
  enrollment_id  INTEGER     NOT NULL,
  event_date     DATE        NOT NULL,
  minutes_delta  INTEGER     NOT NULL,
  source         TEXT        NOT NULL, -- ex.: DAILY_APURACAO/MANUAL_ADJUST
  reference_id   INTEGER     NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT fk_bank_enrollment
    FOREIGN KEY (enrollment_id)
    REFERENCES employee_enrollment (id)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bank_enrollment_date
  ON bank_hours_ledger (enrollment_id, event_date);
