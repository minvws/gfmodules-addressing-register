alter table organization_affiliations
    add version integer default 1 not null;

alter table organization_affiliations
    add fhir_id varchar(1024) default '' not null;


