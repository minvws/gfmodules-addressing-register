CREATE TYPE fhir_interactions AS ENUM ('create', 'update', 'delete');

CREATE TABLE organizations_history
(
    id              uuid              NOT NULL DEFAULT gen_random_uuid(),
    organization_id uuid              NOT NULL,
    interaction     fhir_interactions NOT NULL,
    data            json,
    create_at       timestamp,
    modified_at     timestamp,

    PRIMARY KEY (id)
);
