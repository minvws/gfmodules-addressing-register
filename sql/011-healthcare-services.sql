ALTER TABLE healthcare_services
  ADD COLUMN latest boolean NOT NULL DEFAULT true;

alter table healthcare_services
    add version integer default 1 not null;

alter table healthcare_services
    add fhir_id varchar(1024) default '' not null;

