CREATE TABLE addresses (
    provider_id VARCHAR(50) NOT NULL,
    data_domain VARCHAR(50) NOT NULL ,
    endpoint VARCHAR(255) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    parameters JSON,

    PRIMARY KEY (provider_id, data_domain)
);


-- Mock Provider: ziekenhuis.amsterdam@medmij
INSERT INTO public.addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.amsterdam@medmij', 'beeldbank', 'https://medmeij.services.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "beeldbank", "required": "true", "description": "department"},{"name": "blood-type", "type" : "string", "required": "true", "description": "blood type category"}]');
INSERT INTO public.addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.amsterdam@medmij', 'test resultaten', 'https://medmeij.services.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "department"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: fysio.amsterdam@medmij
INSERT INTO public.addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('fysio.amsterdam@medmij', 'test resultaten', 'https://fysio.services.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "test-results", "required": "true", "description": "test results"},{"name": "location", "type" : "string", "values": ["Rotterdam", "Den Haag"], "required": "true", "description": "the location of the test"}]');

-- Mock Provider: huisarts.apeldoorn@medmij
INSERT INTO public.addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.apeldoorn@medmij', 'beeldbank', 'https://huisarts.services.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of the blood work done"}]');
INSERT INTO public.addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.apeldoorn@medmij', 'test resultaten', 'https://huisarts.services.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-tests", "required": "true", "description": "blood test results"}, {"name": "test-type", "type" : "string", "values": ["liver function", "thyroid function"], "required": "true", "description": "the type of the blood work done"}]');