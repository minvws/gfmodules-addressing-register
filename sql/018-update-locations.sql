ALTER TABLE locations ADD COLUMN latest boolean NOT NULL DEFAULT true;
ALTER TABLE locations ADD version integer DEFAULT 1 NOT NULL;
ALTER TABLE locations ADD COLUMN bundle_meta JSONB;
ALTER TABLE locations ADD COLUMN deleted boolean NOT NULL DEFAULT false;
