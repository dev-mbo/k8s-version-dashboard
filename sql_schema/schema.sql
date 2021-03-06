CREATE DATABASE IF NOT EXISTS k8s_version_dashboard;
USE k8s_version_dashboard;
DROP TABLE IF EXISTS version_history;
DROP TABLE IF EXISTS application; 
DROP TABLE IF EXISTS context; 
CREATE TABLE application (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL);
CREATE TABLE context (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL);
CREATE TABLE version_history (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, application_id INT NOT NULL, context_id INT NOT NULL, version_no varchar(100) NOT NULL, created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (application_id) REFERENCES application (id), FOREIGN KEY (context_id) REFERENCES context(id));