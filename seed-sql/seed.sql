-- Mock Provider: 23665292
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('23665292', 'beeldbank', 'http://metadata:8503/resource', 'GET', '[]');
-- Mock Provider: 13873620
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('13873620', 'beeldbank', 'http://metadata:9999/resource', 'GET', '[]');

-- Mock Provider: 10258861
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('10258861', 'beeldbank', 'https://medmeij.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('10258861', 'test resultaten', 'https://medmeij.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: 13339380
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('13339380', 'beeldbank', 'https://medmeij.apeldoorn.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');

-- Mock Provider: 74604482
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('74604482', 'test resultaten', 'https://medmeij.tilburg.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: 69092583
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('69092583', 'beeldbank', 'https://fysio.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');

-- Mock Provider: 90962238
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('90962238', 'test resultaten', 'https://fysio.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: 54448949
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('54448949', 'test resultaten', 'https://fysio.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: 69113161
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('69113161', 'beeldbank', 'https://huisarts.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('69113161', 'test resultaten', 'https://huisarts.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');

-- Mock Provider: 78356561
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('78356561', 'beeldbank', 'https://huisarts.groningen.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('78356561', 'test resultaten', 'https://huisarts.groningen.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-work", "required": "true", "description": "blood work route"},{"name": "test-name", "type" : "string", "required": "true", "description": "name of the test"}]');
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('78356561', 'medicatie', 'https://huisarts.groningen.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "medicatie", "required": "true", "description": "medication route"},{"name": "name", "type" : "string", "required": "true", "description": "name of the medication"}]');

-- Mock Provider: 28631171
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('28631171', 'beeldbank', 'https://huisarts.eindhoven.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');

-- Mock Provider: 90899169
INSERT INTO addresses (ura_number, data_domain, endpoint, request_type, parameters) VALUES ('90899169', 'beeldbank', 'https://huisarts.tilburg.example.nl', 'GET', '[{"name": "category", "type" : "string", "value" : "blood-bank", "required": "true", "description": "blood bank route"}, {"name": "blood-type", "type" : "string", "values": ["A", "B", "AB", "O"], "required": "true", "description": "the type of blood"}]');
