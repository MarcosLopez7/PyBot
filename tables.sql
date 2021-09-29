CREATE TABLE EspecialChannel(
    id INTEGER PRIMARY KEY,
    guild_id VARCHAR(30) NOT NULL,
    channel_id VARCHAR(30) NOT NULL,
    type VARCHAR(30) NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE SEQUENCE test_id_seq OWNED BY EspecialChannel.id;
ALTER TABLE EspecialChannel ALTER COLUMN id SET DEFAULT nextval('test_id_seq');


CREATE TABLE Roles(
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    role_id VARCHAR(50) NOT NULL,
);

CREATE SEQUENCE role_id_seq OWNED BY Roles.id;
ALTER TABLE Roles ALTER COLUMN id SET DEFAULT nextval('role_id_seq');
