drop table healthcare_services;

create table public.healthcare_services
(
    id          uuid                     default gen_random_uuid() not null
        primary key,
    fhir_id     uuid                                               not null,
    version     integer                  default 1                 not null,
    latest      boolean                  default true              not null,
    deleted     boolean                  default false             not null,
    data        jsonb,
    bundle_meta jsonb                                              not null,
    created_at  timestamp with time zone default (now() AT TIME ZONE 'Europe/Amsterdam'::text),
    modified_at timestamp with time zone default (now() AT TIME ZONE 'Europe/Amsterdam'::text)
);

alter table public.organizations
    owner to addressing_dba;

