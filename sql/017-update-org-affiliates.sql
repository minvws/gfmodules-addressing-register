ALTER TABLE organization_affiliations ADD COLUMN deleted boolean NOT NULL DEFAULT false;

ALTER TABLE organization_affiliations
ALTER COLUMN fhir_id DROP DEFAULT,
ALTER COLUMN fhir_id TYPE uuid USING fhir_id::uuid,
ALTER COLUMN fhir_id SET DEFAULT gen_random_uuid();
