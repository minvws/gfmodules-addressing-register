DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS organizations_history CASCADE;
DROP TABLE IF EXISTS practice_codes CASCADE;
DROP TABLE IF EXISTS affiliation_roles CASCADE;
DROP TABLE IF EXISTS endpoint_payloads CASCADE;
DROP TABLE IF EXISTS endpoint_payload_types CASCADE;
DROP TABLE IF EXISTS endpoints_contact_points CASCADE;
DROP TABLE IF EXISTS contact_points CASCADE;;
DROP TABLE IF EXISTS contact_point_use CASCADE;
DROP TABLE IF EXISTS contact_point_systems CASCADE;
DROP TABLE IF EXISTS endpoints_environments CASCADE;
DROP TABLE IF EXISTS endpoint_headers CASCADE;
DROP TABLE IF EXISTS endpoints CASCADE;
DROP TABLE IF EXISTS connection_types CASCADE;
DROP TABLE IF EXISTS environments CASCADE;
DROP TABLE IF EXISTS statuses CASCADE;
DROP TABLE IF EXISTS organization_contacts CASCADE;
DROP TABLE IF EXISTS organization_type_associations CASCADE;
DROP TABLE IF EXISTS contact_types CASCADE;
DROP TABLE IF EXISTS organization_types CASCADE;

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
ADD COLUMN fhir_id uuid NOT NULL default gen_random_uuid(),
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at AT TIME ZONE 'Europe/Paris',
ALTER COLUMN modified_at TYPE TIMESTAMP WITH TIME ZONE USING modified_at AT TIME ZONE 'Europe/Paris';
