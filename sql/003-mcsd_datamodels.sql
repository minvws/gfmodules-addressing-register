-- https://hl7.org/fhir/organization.html
CREATE TABLE organizations
(
  id                     uuid         NOT NULL DEFAULT gen_random_uuid(),
  active                 BOOLEAN      NOT NULL,
  name                   VARCHAR(150) NOT NULL,
  description            TEXT,
  parent_organization_id uuid,
  created_at             TIMESTAMP             DEFAULT NOW(),
  modified_at            TIMESTAMP             DEFAULT NOW(),

  PRIMARY KEY (id)
);

-- https://hl7.org/fhir/valueset-organization-type.html
-- TODO: fill data in seed
CREATE TABLE organization_types
(
  id          uuid         NOT NULL DEFAULT gen_random_uuid(),
  code        VARCHAR(10)  NOT NULL UNIQUE,
  definition  VARCHAR(255) NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP             DEFAULT NOW(),
  modified_at TIMESTAMP             DEFAULT NOW(),

  PRIMARY KEY (id)
);

-- https://terminology.hl7.org/5.1.0/ValueSet-contactentity-type.html
-- TODO: fill data in seed
CREATE TABLE contact_types
(
  id          uuid         NOT NULL DEFAULT gen_random_uuid(),
  code        VARCHAR(10)  NOT NULL UNIQUE,
  definition  VARCHAR(255) NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP             DEFAULT NOW(),
  modified_at TIMESTAMP             DEFAULT NOW(),

  PRIMARY KEY (id)
);

-- association between organization and organization type
CREATE TABLE organization_type_associations
(
  id                   uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  organization_id      uuid NOT NULL REFERENCES organizations (id),
  organization_type_id uuid NOT NULL REFERENCES organization_types (id),
  created_at             TIMESTAMP             DEFAULT NOW(),
  modified_at            TIMESTAMP             DEFAULT NOW(),

  CONSTRAINT organizations_organization_type_pk PRIMARY KEY (organization_id, organization_type_id)
);

-- association between organization and contact type
CREATE TABLE organization_contacts
(
  id              uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES organizations (id),
  contact_type_id uuid NOT NULL REFERENCES contact_types (id),
  created_at             TIMESTAMP             DEFAULT NOW(),
  modified_at            TIMESTAMP             DEFAULT NOW(),

  CONSTRAINT organizations_contact_pk PRIMARY KEY (organization_id, contact_type_id)
);

-- update organization_types table with references.
-- ref: https://hl7.org/fhir/valueset-organization-type.html

INSERT INTO organization_types (code, display, definition)
VALUES ('prov', 'Healthcare Provider', 'An organization that provides healthcare services.'),
       ('dept', 'Hospital Department',
        'A department or ward within a hospital (Generally is not applicable to top level organizations)'),
       ('team', 'Organizational team',
        'An organizational team is usually a grouping of practitioners that perform a specific function within an organization (which could be a top level organization, or a department).'),
       ('govt', 'Government',
        'A political body, often used when including organization records for government bodies such as a Federal Government, State or Local Government.'),
       ('ins', 'Insurance Company',
        'A company that provides insurance to its subscribers that may include healthcare related policies.'),
       ('pay', 'Payer',
        'A company, charity, or governmental organization, which processes claims and/or issues payments to providers on behalf of patients or groups of patients.'),
       ('edu', 'Educational Institute', 'An educational institution that provides education or research facilities.'),
       ('reli', 'Religious Institution', 'An organization that is identified as a part of a religious institution.'),
       ('crs', 'Clinical Research Sponsor',
        'An organization that is identified as a Pharmaceutical/Clinical Research Sponsor.'),
       ('cg', 'Community Group', 'An un-incorporated community group.'),
       ('bus', 'Non-Healthcare Business or Corporation',
        'An organization that is a registered business or corporation but not identified by other types.'),
       ('other', 'Other', 'Other type of organization not already specified.');

-- update contact_types table with references
-- https://terminology.hl7.org/5.1.0/ValueSet-contactentity-type.html
INSERT INTO contact_types (code, display, definition)
VALUES ('BILL', 'Billing', 'Contact details for information regarding to billing/general finance enquiries.'),
       ('ADMIN', 'Administrative', 'Contact details for administrative enquiries.'),
       ('HR', 'Human Resource',
        'Contact details for issues related to Human Resources, such as staff matters, OH&S etc.'),
       ('PAYOR', 'Payor', 'Contact details for dealing with issues related to insurance claims/adjudication/payment.'),
       ('PATINF', 'Patient', 'Generic information contact for patients.'),
       ('PRESS', 'Press', 'Dedicated contact point for matters relating to press enquiries.');
