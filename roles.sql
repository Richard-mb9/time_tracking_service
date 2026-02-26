WITH required_permissions (name, description) AS (
    VALUES (
            'bank_hours_ledgers:create',
            'Criar Lancamentos de Banco de Horas'
        ),
        (
            'bank_hours_ledgers:read',
            'Visualizar Lancamentos de Banco de Horas'
        ),
        (
            'bank_hours_ledgers:*',
            'Total Acesso a Lancamentos de Banco de Horas'
        ),
        (
            'daily_attendance_summaries:read',
            'Visualizar Resumos Diarios de Frequencia'
        ),
        (
            'daily_attendance_summaries:edit',
            'Recalcular Resumos Diarios de Frequencia'
        ),
        (
            'daily_attendance_summaries:*',
            'Total Acesso a Resumos Diarios de Frequencia'
        ),
        (
            'enrollment_policy_assignments:create',
            'Criar Atribuicoes de Politicas de Jornada'
        ),
        (
            'enrollment_policy_assignments:read',
            'Visualizar Atribuicoes de Politicas de Jornada'
        ),
        (
            'enrollment_policy_assignments:edit',
            'Editar Atribuicoes de Politicas de Jornada'
        ),
        (
            'enrollment_policy_assignments:write',
            'Remover Atribuicoes de Politicas de Jornada'
        ),
        (
            'enrollment_policy_assignments:*',
            'Total Acesso a Atribuicoes de Politicas de Jornada'
        ),
        (
            'time_adjustment_requests:create',
            'Criar Solicitacoes de Ajuste de Ponto'
        ),
        (
            'time_adjustment_requests:read',
            'Visualizar Solicitacoes de Ajuste de Ponto'
        ),
        (
            'time_adjustment_requests:edit',
            'Decidir/Aplicar Solicitacoes de Ajuste de Ponto'
        ),
        (
            'time_adjustment_requests:write',
            'Cancelar/Remover Solicitacoes de Ajuste de Ponto'
        ),
        (
            'time_adjustment_requests:*',
            'Total Acesso a Solicitacoes de Ajuste de Ponto'
        ),
        (
            'time_punches:create',
            'Criar Batidas de Ponto'
        ),
        (
            'time_punches:read',
            'Visualizar Batidas de Ponto'
        ),
        (
            'time_punches:write',
            'Remover Batidas de Ponto'
        ),
        (
            'time_punches:*',
            'Total Acesso a Batidas de Ponto'
        ),
        (
            'work_policy_templates:create',
            'Criar Templates de Jornada'
        ),
        (
            'work_policy_templates:read',
            'Visualizar Templates de Jornada'
        ),
        (
            'work_policy_templates:edit',
            'Editar Templates de Jornada'
        ),
        (
            'work_policy_templates:write',
            'Remover Templates de Jornada'
        ),
        (
            'work_policy_templates:*',
            'Total Acesso a Templates de Jornada'
        ),
        (
            'time-management:read',
            'Acesso a Gestão de Ponto'
        )
),
permissions_to_insert AS (
    SELECT rp.name,
        rp.description
    FROM required_permissions rp
    WHERE NOT EXISTS (
            SELECT 1
            FROM roles r
            WHERE r.name = rp.name
        )
),
numbered_permissions AS (
    SELECT COALESCE(
            (
                SELECT MAX(id)
                FROM roles
            ),
            0
        ) + ROW_NUMBER() OVER (
            ORDER BY p.name
        ) AS id,
        p.name,
        p.description
    FROM permissions_to_insert p
)
INSERT INTO roles (id, name, description)
SELECT id,
    name,
    description
FROM numbered_permissions;