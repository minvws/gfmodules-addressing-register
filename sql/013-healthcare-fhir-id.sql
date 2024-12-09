alter table healthcare_services
    alter column fhir_id type varchar(1024) using fhir_id::varchar(1024);

alter table healthcare_services
    alter column fhir_id drop default;
