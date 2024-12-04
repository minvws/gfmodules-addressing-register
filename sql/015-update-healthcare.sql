alter table healthcare_services
    alter column created_at set default (now() AT TIME ZONE 'Europe/UTC'::text);

alter table healthcare_services
    alter column modified_at set default (now() AT TIME ZONE 'Europe/UTC'::text);
