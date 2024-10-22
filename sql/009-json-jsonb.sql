ALTER TABLE organization_affiliations ALTER COLUMN data SET DATA TYPE jsonb USING data::jsonb;
ALTER TABLE locations ALTER COLUMN data SET DATA TYPE jsonb USING data::jsonb;
ALTER TABLE healthcare_services ALTER COLUMN data SET DATA TYPE jsonb USING data::jsonb;
