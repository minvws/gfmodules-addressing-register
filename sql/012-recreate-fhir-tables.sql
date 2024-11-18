DROP TABLE IF EXISTS practice_codes;
DROP TABLE IF EXISTS affiliation_roles;
DROP TABLE IF EXISTS endpoint_payloads;
DROP TABLE IF EXISTS endpoint_payload_types;
DROP TABLE IF EXISTS endpoints_contact_points;
DROP TABLE IF EXISTS contact_points;
DROP TABLE IF EXISTS contact_point_use;
DROP TABLE IF EXISTS contact_point_systems;
DROP TABLE IF EXISTS endpoints_environments;
DROP TABLE IF EXISTS endpoint_headers;
DROP TABLE IF EXISTS endpoints;
DROP TABLE IF EXISTS connection_types;
DROP TABLE IF EXISTS environments;
DROP TABLE IF EXISTS statuses;
DROP TABLE IF EXISTS organization_contacts;
DROP TABLE IF EXISTS organization_type_associations;
DROP TABLE IF EXISTS contact_types;
DROP TABLE IF EXISTS organization_types;
DROP TABLE IF EXISTS organizations_history;
DROP TABLE IF EXISTS organizations;

-- https://hl7.org/fhir/organization.html
CREATE TABLE organizations
(
  id                     uuid         NOT NULL DEFAULT gen_random_uuid(),
  fhir_id                uuid         NOT NULL,
  ura_number             VARCHAR      NOT NULL,
  version                INT          NOT NULL DEFAULT 1,
  latest                 BOOLEAN      NOT NULL DEFAULT TRUE,
  deleted                BOOLEAN      NOT NULL DEFAULT FALSE,
  data                   JSONB,
  bundle_meta            JSONB NOT NULL,
  created_at             TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'Europe/Paris'),
  modified_at            TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'Europe/Paris'),

  PRIMARY KEY (id)
);

-- https://hl7.org/fhir/endpoint.html#Endpoint
CREATE TABLE endpoints
(
  id                     uuid         NOT NULL DEFAULT gen_random_uuid(),
  fhir_id                uuid         NOT NULL,
  version                INT          NOT NULL DEFAULT 1,
  latest                 BOOLEAN      NOT NULL DEFAULT TRUE,
  deleted                BOOLEAN      NOT NULL DEFAULT FALSE,
  data                   JSONB,
  bundle_meta            JSONB NOT NULL,
  created_at             TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'Europe/Paris'),
  modified_at            TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'Europe/Paris'),

  PRIMARY KEY (id)

);

ALTER TABLE supplier_endpoints
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'Europe/Paris',
ALTER COLUMN modified_at TYPE TIMESTAMP WITH TIME ZONE USING modified_at AT TIME ZONE 'Europe/Paris';

ALTER TABLE organization_affiliations
ADD COLUMN bundle_meta JSONB,
ALTER COLUMN modified_at TYPE TIMESTAMP WITH TIME ZONE USING modified_at AT TIME ZONE 'Europe/Paris',
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'Europe/Paris';

ALTER TABLE locations
ADD COLUMN fhir_id uuid NOT NULL default gen_random_uuid(),
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'Europe/Paris',
ALTER COLUMN modified_at TYPE TIMESTAMP WITH TIME ZONE USING modified_at AT TIME ZONE 'Europe/Paris';

ALTER TABLE healthcare_services
ALTER COLUMN fhir_id TYPE uuid USING fhir_id::uuid,
ALTER COLUMN fhir_id SET NOT NULL,
ALTER COLUMN fhir_id DROP DEFAULT,
ALTER COLUMN fhir_id SET DEFAULT gen_random_uuid(),
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'Europe/Paris',
ALTER COLUMN modified_at TYPE TIMESTAMP WITH TIME ZONE USING modified_at AT TIME ZONE 'Europe/Paris';
