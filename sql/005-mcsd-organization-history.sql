CREATE TYPE fhir_interactions AS ENUM ('create', 'update', 'delete');

CREATE TABLE organizations_history
(
    id              uuid              NOT NULL DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL,
    ura_number      VARCHAR NOT NULL,
    interaction     fhir_interactions NOT NULL,
    data            json,
    created_at      timestamp,
    modified_at     timestamp,

    PRIMARY KEY (id),
    CONSTRAINT organization_history_organizations_fk FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
