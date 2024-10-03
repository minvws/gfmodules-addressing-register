CREATE TABLE supplier_endpoints
(
  ura_number                CHAR(8)         NOT NULL UNIQUE,
  care_provider_name        VARCHAR(150)    NOT NULL,
  update_supplier_endpoint  VARCHAR         NOT NULL,
  created_at                TIMESTAMP           DEFAULT NOW(),
  modified_at               TIMESTAMP           DEFAULT NOW(),

  PRIMARY KEY (ura_number)
);
