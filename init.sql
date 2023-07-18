-- init.sql

-- drop table - we create always new table
DROP TABLE IF EXISTS sreality;

-- Create a table
CREATE TABLE IF NOT EXISTS sreality (id SERIAL PRIMARY KEY,
                                     title VARCHAR(256),
                                     local_data VARCHAR(256),
                                     img_href VARCHAR(256),
                                     price INT);
