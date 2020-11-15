CREATE DATABASE IF NOT EXISTS `plex_files`
USE `plex_files`;

CREATE TABLE IF NOT EXISTS `assoc_process_response` (
  `Id` int NOT NULL DEFAULT '0',
  `Response` char(10) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `compressed_files` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Size` bigint NOT NULL DEFAULT '0',
  `Response` int NOT NULL DEFAULT '0',
  `Processing` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Name` (`Name`),
  KEY `FK_compressed_files_assoc_process_response` (`Response`),
  KEY `FK_compressed_files_assoc_process_response_2` (`Processing`),
  CONSTRAINT `FK_compressed_files_assoc_process_response` FOREIGN KEY (`Response`) REFERENCES `assoc_process_response` (`Id`),
  CONSTRAINT `FK_compressed_files_assoc_process_response_2` FOREIGN KEY (`Processing`) REFERENCES `assoc_process_response` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
