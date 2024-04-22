CREATE TABLE addresses (
    provider_id VARCHAR(50) NOT NULL,
    data_domain VARCHAR(50) NOT NULL ,
    endpoint VARCHAR(255) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    parameters JSON,

    PRIMARY KEY (provider_id, data_domain)
);


INSERT INTO public.addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.amsterdam@medmij', 'beeldbank', 'https://medmeij.services.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "beeldbank", "required": "true", "description": "department"},{"name": "blood-type", "type" : "string", "required": "true", "description": "blood type category"}]');

INSERT INTO public.addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.amsterdam@medmij', 'test resultaten', 'https://medmeij.services.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "department"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');