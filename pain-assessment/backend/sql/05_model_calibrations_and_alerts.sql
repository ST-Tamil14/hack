-- Migration 05: Model Calibrations and Monitoring Alerts Schema

-- 1. Create Model Calibrations Table
create table if not exists public.model_calibrations (
    id uuid primary key default gen_random_uuid(),

    model_name varchar(100) not null,
    model_version varchar(50) not null,
    modality varchar(50) not null,

    calibration_method varchar(100) not null,
    dataset_name varchar(150),

    temperature numeric,
    threshold_low numeric,
    threshold_moderate numeric,
    threshold_high numeric,

    calibration_error numeric,
    brier_score numeric,
    expected_calibration_error numeric,

    sample_count integer,
    notes text,

    calibrated_by uuid references auth.users(id) on delete set null,
    created_at timestamptz default now()
);

alter table public.model_calibrations enable row level security;

create index if not exists model_calibrations_model_idx
on public.model_calibrations(model_name);

create index if not exists model_calibrations_modality_idx
on public.model_calibrations(modality);


-- 2. Create Monitoring Alerts Table
create table if not exists public.monitoring_alerts (
    id uuid primary key default gen_random_uuid(),

    patient_id uuid not null references public.patients(id) on delete cascade,
    episode_id uuid references public.pain_episodes(id) on delete set null,

    alert_type varchar(100) not null,
    severity varchar(50) not null
        check (severity in (
            'informational',
            'review_recommended',
            'urgent_review'
        )),

    message text not null,

    score numeric check (
        score is null
        or (score >= 0 and score <= 1)
    ),

    confidence numeric check (
        confidence is null
        or (confidence >= 0 and confidence <= 1)
    ),

    status varchar(50) not null default 'open'
        check (status in (
            'open',
            'acknowledged',
            'resolved',
            'dismissed'
        )),

    clinician_label varchar(50)
        check (
            clinician_label is null
            or clinician_label in (
                'true_positive',
                'false_positive',
                'true_negative',
                'false_negative',
                'uncertain'
            )
        ),
    clinician_feedback text,

    acknowledged_by uuid references auth.users(id) on delete set null,
    acknowledged_at timestamptz,
    resolved_by uuid references auth.users(id) on delete set null,
    resolved_at timestamptz,

    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

alter table public.monitoring_alerts enable row level security;

create index if not exists monitoring_alerts_patient_idx
on public.monitoring_alerts(patient_id);

create index if not exists monitoring_alerts_status_idx
on public.monitoring_alerts(status);

create index if not exists monitoring_alerts_created_at_idx
on public.monitoring_alerts(created_at);
