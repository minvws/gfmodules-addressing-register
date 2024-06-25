CREATE TABLE addresses (
    provider_id VARCHAR(50) NOT NULL,
    data_domain VARCHAR(50) NOT NULL ,
    endpoint VARCHAR(255) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    parameters JSON,

    PRIMARY KEY (provider_id, data_domain)
);

ALTER TABLE addresses OWNER TO addressing;
