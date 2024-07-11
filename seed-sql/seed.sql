-- Mock Provider: irealisatie.mock.metadata
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('irealisatie.mock.metadata', 'beeldbank', 'http://metadata:8503/resource', 'GET', '[]');
-- Mock Provider: irealisatie.mock.metadata.unavailable
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('irealisatie.mock.metadata.unavailable', 'beeldbank', 'http://metadata:9999/resource', 'GET', '[]');

-- Mock Provider: ziekenhuis.amsterdam@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.amsterdam@medmij', 'beeldbank', 'https://medmeij.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.amsterdam@medmij', 'test resultaten', 'https://medmeij.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: ziekenhuis.apeldoorn@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.apeldoorn@medmij', 'beeldbank', 'https://medmeij.apeldoorn.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');

-- Mock Provider: ziekenhuis.tilburg@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.tilburg@medmij', 'test resultaten', 'https://medmeij.tilburg.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: ziekenhuis.eindhoven@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('ziekenhuis.eindhoven@medmij', 'beeldbank', 'https://fysio.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');

-- Mock Provider: fysio.amsterdam@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('fysio.amsterdam@medmij', 'test resultaten', 'https://fysio.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: fysio.deventetr@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('fysio.deventetr@medmij', 'test resultaten', 'https://fysio.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: huisarts.apeldoorn@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.apeldoorn@medmij', 'beeldbank', 'https://huisarts.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.apeldoorn@medmij', 'test resultaten', 'https://huisarts.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: huisarts.groningen@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.groningen@medmij', 'beeldbank', 'https://huisarts.groningen.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.groningen@medmij', 'test resultaten', 'https://huisarts.groningen.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.groningen@medmij', 'medicatie', 'https://huisarts.groningen.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "medicatie", "required": "true", "description": "medication route"},{"name": "name", "type" : "string", "required": "true", "description": "name of the medication"}]');

-- Mock Provider: huisarts.eindhoven@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.eindhoven@medmij', 'beeldbank', 'https://huisarts.eindhovwn.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');

-- Mock Provider: huisarts.tilburg@medmij
INSERT INTO addresses (provider_id, data_domain, endpoint, request_type, parameters) VALUES ('huisarts.tilburg@medmij', 'beeldbank', 'https://huisarts.tilburg.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');