/*
create table users query
*/

CREATE TABLE USERS (
	      ID int(4) unsigned NOT NULL AUTO_INCREMENT,
	      PHONE_NUMBER varchar(13) DEFAULT NULL,
	      EMAIL_ADDRESS varchar(50) DEFAULT NULL,
	      PRIMARY KEY (ID),
	      UNIQUE KEY ID (ID)
)
