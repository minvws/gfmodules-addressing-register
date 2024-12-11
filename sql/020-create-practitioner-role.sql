CREATE TABLE practitioner_roles
(
  id                     uuid         NOT NULL DEFAULT gen_random_uuid(),
  fhir_id                uuid         NOT NULL,
  version                INT          NOT NULL DEFAULT 1,
  latest                 BOOLEAN      NOT NULL DEFAULT TRUE,
  deleted                BOOLEAN      NOT NULL DEFAULT FALSE,
  data                   JSONB,
  bundle_meta            JSONB NOT NULL,
  created_at             TIMESTAMP with time zone DEFAULT (NOW() AT TIME ZONE 'UTC'),
  modified_at            TIMESTAMP with time zone DEFAULT (NOW() AT TIME ZONE 'UTC'),

  PRIMARY KEY (id)
);

alter table public.practitioner_roles owner to addressing_dba;
