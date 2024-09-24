-- https://hl7.org/fhir/organization.html
CREATE TABLE organizations
(
  id                     uuid         NOT NULL DEFAULT gen_random_uuid(),
  ura_number             VARCHAR      NOT NULL UNIQUE,
  active                 BOOLEAN      NOT NULL,
  name                   VARCHAR(150) NOT NULL,
  description            TEXT,
  parent_organization_id uuid,
  created_at             TIMESTAMP             DEFAULT NOW(),
  modified_at            TIMESTAMP             DEFAULT NOW(),

  PRIMARY KEY (id)
);

-- https://hl7.org/fhir/valueset-organization-type.html
CREATE TABLE organization_types
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
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

-- https://terminology.hl7.org/5.1.0/ValueSet-contactentity-type.html
CREATE TABLE contact_types
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);
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

-- association between organization and organization type
CREATE TABLE organization_type_associations
(
  id                uuid        NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  organization_id   uuid        NOT NULL,
  organization_type VARCHAR(50) NOT NULL,
  created_at        TIMESTAMP                   DEFAULT NOW(),
  modified_at       TIMESTAMP                   DEFAULT NOW(),

  PRIMARY KEY (organization_id, organization_type),
  CONSTRAINT organization_type_associations_organizations_fk FOREIGN KEY (organization_id) REFERENCES organizations (id),
  CONSTRAINT organization_organization_type_fk FOREIGN KEY (organization_type) REFERENCES organization_types (code)
);

-- association between organization and contact type
CREATE TABLE organization_contacts -- added
(
  id              uuid        NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  organization_id uuid        NOT NULL,
  contact_type    VARCHAR(50) NOT NULL,
  created_at      TIMESTAMP                   DEFAULT NOW(),
  modified_at     TIMESTAMP                   DEFAULT NOW(),

  PRIMARY KEY (organization_id, contact_type),
  CONSTRAINT organization_contacts_organizations_fk FOREIGN KEY (organization_id) REFERENCES organizations (id),
  CONSTRAINT organization_contacts_contact_type_fk FOREIGN KEY (contact_type) REFERENCES contact_types (code)
);


-- https://hl7.org/fhir/valueset-endpoint-status.html
CREATE TABLE statuses
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);
INSERT INTO statuses(code, display, definition)
VALUES ('active', 'Active', 'This endpoint is expected to be active and can be used.'),
       ('suspended', 'Suspended', 'This endpoint is temporarily unavailable.'),
       ('error', 'Error',
        'This endpoint has exceeded connectivity thresholds and is considered in an error state and should no longer be attempted to connect to until corrective action is taken.'),
       ('off', 'Off', 'This endpoint is no longer to be used.'),
       ('entered-in-error', 'Entered in error',
        'This instance should not have been part of this patient''s medical record.');


-- https://build.fhir.org/valueset-endpoint-environment.html
CREATE TABLE environments -- added
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);
INSERT INTO environments(code, display, definition)
VALUES ('prod', 'Production',
        'Production environment and is expected to contain real data and should be protected appropriately'),
       ('staging', 'Staging', 'Staging environment typically used while preparing for a release to production'),
       ('dev', 'Development', 'evelopment environment used while building systems'),
       ('test', 'Test', 'Test environment, it is not intended for production usage.'),
       ('train', 'Training',
        'Training environment, it is not intended for production usage and typically contains data specifically prepared for training usage.');

-- https://hl7.org/fhir/valueset-endpoint-connection-type.html
CREATE TABLE connection_types -- added
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);
INSERT INTO connection_types(code, display, definition)
VALUES ('dicom-wado-rs', 'DICOM WADO-RS',
        'DICOMweb RESTful Image Retrieve - http://dicom.nema.org/medical/dicom/current/output/chtml/part18/sect_6.5.html'),
       ('dicom-qido-rs', 'DICOM QIDO-RS',
        'DICOMweb RESTful Image query - http://dicom.nema.org/medical/dicom/current/output/chtml/part18/sect_6.7.html'),
       ('dicom-stow-rs', 'DICOM STOW-RS',
        'DICOMweb RESTful image sending and storage - http://dicom.nema.org/medical/dicom/current/output/chtml/part18/sect_6.6.html'),
       ('dicom-wado-uri', 'DICOM WADO-URI',
        'DICOMweb Image Retrieve - http://dicom.nema.org/dicom/2013/output/chtml/part18/sect_6.3.html'),
       ('hl7-fhir-rest', 'HL7 FHIR',
        'Interact with the server interface using FHIR''s RESTful interface. For details on its version/capabilities you should connect the value in Endpoint.address and retrieve the FHIR CapabilityStatement.'),
       ('hl7-fhir-msg', 'HL7 FHIR Messaging',
        'Use the servers FHIR Messaging interface. Details can be found on the messaging.html page in the FHIR Specification. The FHIR server''s base address is specified in the Endpoint.address property.'),
       ('hl7v2-mllp', 'HL7 v2 MLLP', 'HL7v2 messages over an LLP TCP connection'),
       ('secure-email', 'Secure email',
        'Email delivery using a digital certificate to encrypt the content using the public key, receiver must have the private key to decrypt the content'),
       ('direct-project', 'Direct Project', 'Direct Project information - http://wiki.directproject.org/'),
       ('cds-hooks-service', 'CDS Hooks Service',
        'A CDS Hooks Service connection. The address will be the base URL of the service as described in the CDS specification https://cds-hooks.hl7.org');

-- https://hl7.org/fhir/endpoint.html#Endpoint
CREATE TABLE endpoints
(
  id              UUID        NOT NULL DEFAULT gen_random_uuid(),
  organization_id UUID,
  status_type     VARCHAR(50) NOT NULL,
  name            VARCHAR(150),
  description     VARCHAR,
  address         TEXT        NOT NULL,
  created_at      TIMESTAMP            DEFAULT NOW(),
  modified_at     TIMESTAMP            DEFAULT NOW(),

  PRIMARY KEY (id),
  CONSTRAINT endpoints_organizations_fk FOREIGN KEY (organization_id) REFERENCES organizations (id),
  CONSTRAINT endpoint_statuses_fk FOREIGN KEY (status_type) REFERENCES statuses (code)

);

-- zero to one
CREATE TABLE endpoint_periods -- added
(
  id          uuid      NOT NULL DEFAULT gen_random_uuid(),
  endpoint_id uuid      NOT NULL UNIQUE,
  start_date  TIMESTAMP NOT NULL,
  end_date    TIMESTAMP NOT NULL,
  created_at  TIMESTAMP          DEFAULT NOW(),
  modified_at TIMESTAMP          DEFAULT NOW(),

  PRIMARY KEY (id),
  CONSTRAINT endpoints_period_endpoint_fk FOREIGN KEY (endpoint_id) REFERENCES endpoints (id)
);

CREATE TABLE endpoint_headers -- added
(
  id          uuid NOT NULL DEFAULT gen_random_uuid(),
  endpoint_id uuid NOT NULL,
  data        TEXT,
  created_at  TIMESTAMP     DEFAULT NOW(),
  modified_at TIMESTAMP     DEFAULT NOW(),

  PRIMARY KEY (id),
  CONSTRAINT endpoint_headers_endpoint_fk FOREIGN KEY (endpoint_id) REFERENCES endpoints (id)
);

CREATE TABLE endpoints_connection_types -- added
(
  id              uuid        NOT NULL DEFAULT gen_random_uuid(),
  endpoint_id     uuid        NOT NULL,
  connection_type VARCHAR(50) NOT NULL,
  created_at      TIMESTAMP            DEFAULT NOW(),
  modified_at     TIMESTAMP            DEFAULT NOW(),

  PRIMARY KEY (endpoint_id, connection_type),
  CONSTRAINT endpoint_connection_types_endpoint_fk FOREIGN KEY (endpoint_id) REFERENCES endpoints (id),
  CONSTRAINT endpoints_connection_types_connection_types_fk FOREIGN KEY (connection_type) REFERENCES connection_types (code)
);

CREATE TABLE endpoints_environments -- added
(
  id               uuid        NOT NULL DEFAULT gen_random_uuid(),
  endpoint_id      uuid        NOT NULL,
  environment_type VARCHAR(50) NOT NULL,
  created_at       TIMESTAMP            DEFAULT NOW(),
  modified_at      TIMESTAMP            DEFAULT NOW(),

  PRIMARY KEY (endpoint_id, environment_type),
  CONSTRAINT endpoint_environments_endpoints_fk FOREIGN KEY (endpoint_id) REFERENCES endpoints (id),
  CONSTRAINT endpoints_environments_environments_fk FOREIGN KEY (environment_type) REFERENCES environments (code)
);

-- https://hl7.org/fhir/valueset-contact-point-system.html
CREATE TABLE contact_point_systems -- added
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);
INSERT INTO contact_point_systems (code, display, definition)
VALUES ('phone', 'Phone',
        'The value is a telephone number used for voice calls. Use of full international numbers starting with + is recommended to enable automatic dialing support but not required.'),
       ('fax', 'Fax',
        'The value is a fax machine. Use of full international numbers starting with + is recommended to enable automatic dialing support but not required.'),
       ('email', 'Email', 'The value is an email address.'),
       ('pager', 'Pager',
        'The value is a pager number. These may be local pager numbers that are only usable on a particular pager system.'),
       ('url', 'URL',
        'A contact that is not a phone, fax, pager or email address and is expressed as a URL. This is intended for various institutional or personal contacts including web sites, blogs, Skype, Twitter, Facebook, etc. Do not use for email addresses.'),
       ('sms', 'SMS', 'A contact that can be used for sending a sms message (e.g. mobile phones, some landlines).'),
       ('other', 'Other',
        'A contact that is not a phone, fax, page or email address and is not expressible as a URL. E.g. Internal mail address. This SHOULD NOT be used for contacts that are expressible as a URL (e.g. Skype, Twitter, Facebook, etc.) Extensions may be used to distinguish "other" contact types.');

-- https://hl7.org/fhir/valueset-contact-point-use.html
CREATE TABLE contact_point_use
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);
INSERT INTO contact_point_use (code, display, definition)
VALUES ('home', 'Home',
        'A communication contact point at a home; attempted contacts for business purposes might intrude privacy and chances are one will contact family or other household members instead of the person one wishes to call. Typically used with urgent cases, or if no other contacts are available.'),
       ('work', 'Work', 'An office contact point. First choice for business related contacts during business hours.'),
       ('temp', 'Temp', 'A temporary contact point. The period can provide more detailed information.'),
       ('old', 'Old', 'This contact point is no longer in use (or was never correct, but retained for records).'),
       ('mobile', 'Mobile',
        'A telecommunication device that moves and stays with its owner. May have characteristics of all other use codes, suitable for urgent matters, not the first choice for routine business.');


CREATE TABLE contact_points
(
  id          uuid    NOT NULL DEFAULT gen_random_uuid(),
  system_type VARCHAR(50),
  use_type    VARCHAR(50),
  value       VARCHAR NOT NULL,
  rank        numeric CHECK (rank > 0),
  created_at  TIMESTAMP        DEFAULT NOW(),
  modified_at TIMESTAMP        DEFAULT NOW(),

  PRIMARY KEY (id),
  UNIQUE (id, system_type),
  CONSTRAINT contact_points_contact_point_systems_fk FOREIGN KEY (system_type) REFERENCES contact_point_systems (code),
  CONSTRAINT contact_points_contact_point_use_fk FOREIGN KEY (use_type) REFERENCES contact_point_use (code)
);

-- zero to one
CREATE TABLE contact_point_periods -- added
(
  id               uuid NOT NULL DEFAULT gen_random_uuid(),
  contact_point_id uuid NOT NULL UNIQUE,
  start_date       TIMESTAMP,
  end_date         TIMESTAMP,
  created_at       TIMESTAMP     DEFAULT NOW(),
  modified_at      TIMESTAMP     DEFAULT NOW(),
  PRIMARY KEY (id),
  CONSTRAINT contact_points_period_contact_points_fk FOREIGN KEY (contact_point_id) REFERENCES contact_points (id)
);

CREATE TABLE endpoints_contact_points
(
  id               uuid NOT NULL DEFAULT gen_random_uuid(),
  endpoint_id      uuid NOT NULL,
  contact_point_id uuid NOT NULL,
  created_at       TIMESTAMP     DEFAULT NOW(),
  modified_at      TIMESTAMP     DEFAULT NOW(),

  PRIMARY KEY (id),
  UNIQUE (endpoint_id, contact_point_id),
  CONSTRAINT endpoint_contact_points_endpoints_fk FOREIGN KEY (endpoint_id) REFERENCES endpoints (id),
  CONSTRAINT endpoint_contact_points_contact_points_fk FOREIGN KEY (contact_point_id) REFERENCES contact_points (id)
);

CREATE TABLE endpoint_payload_types
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);

INSERT INTO endpoint_payload_types (code, display, definition)
VALUES ('any', 'ANY',
        'Any payload type can be used with this endpoint, it is either a payload agnostic infrastructure (such as a storage repository), or some other type of endpoint where payload considerations are internally handled, and not available'),
       ('none', 'NONE',
        'This endpoint does not require any content to be sent; simply connecting to the endpoint is enough notification. This can be used as a ''ping'' to wakeup a service to retrieve content, which could be to ensure security considerations are correctly handled'),
       ('urn:ihe:pcc:xds-ms:2007', 'PCC XDS-MS', 'XDS Medical Summaries');

CREATE TABLE endpoint_payloads
(
  id           uuid        NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  endpoint_id  UUID        NOT NULL,
  payload_type VARCHAR(50) NOT NULL,
  mime_type    TEXT,
  created_at   TIMESTAMP                   DEFAULT NOW(),
  modified_at  TIMESTAMP                   DEFAULT NOW(),

  PRIMARY KEY (id),
  CONSTRAINT endpoint_payloads_endpoint_payload_types_fk FOREIGN KEY (payload_type) REFERENCES endpoint_payload_types (code),
  CONSTRAINT endpont_payloads_endpoints_fk FOREIGN KEY (endpoint_id) REFERENCES endpoints (id)
);

-- https://hl7.org/fhir/R4/organizationaffiliation.html
CREATE TABLE organization_affiliation_roles
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);


INSERT INTO organization_affiliation_roles (code, display, definition)
VALUES ('provider', 'Provider', 'An organization that delivers care services (e.g. hospitals, clinics, community and social services, etc.).'),
       ('agency', 'Agency', 'An organization such as a public health agency, community/social services provider, etc.'),
       ('research', 'Research',
        'An organization providing research-related services such as conducting research, recruiting research participants, analyzing data, etc.'),
       ('payer', 'Payer', 'An organization providing reimbursement, payment, or related services'),
       ('diagnostics', 'Diagnostics', 'An organization providing diagnostic testing/laboratory services'),
       ('supplier', 'Supplier',
        'An organization that provides medical supplies (e.g. medical devices, equipment, pharmaceutical products, etc.'),
       ('HIE/HIO', 'HIE/HIO', 'An organization that facilitates electronic clinical data exchange between entities'),
       ('member', 'Member',
        'A type of non-ownership relationship between entities (encompasses partnerships, collaboration, joint ventures, etc.)');


-- https://hl7.org/fhir/R4/valueset-c80-practice-codes.html
-- note: not all codes are added, just examples
CREATE TABLE practice_codes
(
  code        VARCHAR(50)  NOT NULL UNIQUE,
  definition  VARCHAR      NOT NULL,
  display     VARCHAR(150) NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW(),
  modified_at TIMESTAMP DEFAULT NOW(),

  PRIMARY KEY (code)
);
INSERT INTO practice_codes (code, display, definition)
VALUES ('408467006', 'Adult mental illness - specialty (qualifier value)','Adult mental illness'),
       ('394577000', 'Anesthetics','Anesthetics'),
       ('394579002', 'Cardiology (qualifier value)','Cardiology'),
       ('408480009', 'Clinical immunology (qualifier value)','Clinical immunology'),
       ('408475000', 'Diabetic medicine (qualifier value)','Diabetic medicine'),
       ('419772000', 'Family practice (qualifier value)', 'Family practice'),
       ('394814009', 'General practice (specialty) (qualifier value)', 'General practice'),
       ('394593009', 'Medical oncology (qualifier value)', 'Medical oncology');






















