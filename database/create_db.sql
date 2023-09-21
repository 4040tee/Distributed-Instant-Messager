CREATE USER 'chat-app'@'localhost' IDENTIFIED BY 'pass';
GRANT ALL PRIVILEGES ON *.* TO 'chat-app'@'localhost' WITH GRANT OPTION;
CREATE USER 'chat-app'@'%' IDENTIFIED BY 'pass';
GRANT ALL PRIVILEGES ON *.* TO 'chat-app'@'%' WITH GRANT OPTION;

DROP DATABASE IF EXISTS ChatApp;
CREATE DATABASE ChatApp;
USE ChatApp;

CREATE TABLE User (
    id INT AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Channel (
    id INT AUTO_INCREMENT,
    channel_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);

CREATE TABLE Watching (
    user_id INT,
    channel_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (channel_id) REFERENCES Channel(id),
	PRIMARY KEY (user_id, channel_id)
);

CREATE TABLE Block (
    user_id INT,
    block_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (block_id) REFERENCES User(id),
	PRIMARY KEY (user_id, block_id)
);

CREATE TABLE Online (
    user_id INT,
    access_token VARCHAR(20) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE Missed (
    user_id INT,
    message VARCHAR(500) NOT NULL,
    from_user INT NOT NULL,
    sender_name VARCHAR(50) NOT NULL,
    datetime DATETIME NOT NULL,
	channel_name VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES User(id)
);