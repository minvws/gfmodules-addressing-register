-- https://hl7.org/fhir/r4/organizationaffiliation.html
CREATE TABLE organization_affiliations
(
  id          uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  data        json,
  created_at  timestamp            DEFAULT now(),
  modified_at timestamp            DEFAULT now(),

  PRIMARY KEY (id)
);

CREATE TABLE locations
(
  id          uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  data        json,
  created_at  timestamp            DEFAULT now(),
  modified_at timestamp            DEFAULT now(),

  PRIMARY KEY (id)
);

CREATE TABLE healthcare_services
(
  id          uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  data        json,
  created_at  timestamp            DEFAULT now(),
  modified_at timestamp            DEFAULT now(),

  PRIMARY KEY (id)
)
