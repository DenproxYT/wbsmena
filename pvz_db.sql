-- MySQL dump 10.13  Distrib 8.4.9, for Linux (x86_64)
--
-- Host: localhost    Database: pvz_db
-- ------------------------------------------------------
-- Server version	8.4.9

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `pvz_address` varchar(255) NOT NULL,
  `is_intern` tinyint(1) NOT NULL,
  `role` varchar(20) NOT NULL,
  `must_change_credentials` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone_number` (`phone_number`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES (1,'pbkdf2_sha256$600000$ke7B9aFHBAdysFHSpMRc3M$sp/GjM3kimGNoq0/bxBdwIYwWftcHWGybqzbS/E2IcQ=','2026-05-11 09:06:34.764044',1,'admin','Елена','','admin@example.com',1,1,'2026-01-30 09:34:01.000000','+73022355600','ул. Анохина, 88',0,'administrator',0),(2,'pbkdf2_sha256$600000$04ieltaoRPCv8sJ76mIQrm$KmFCXgOxllzqVtgFJB3LmyTsX1q/wBuYyz/pU8owh2U=','2026-04-13 05:42:32.808000',1,'danil','Данил','Гнатчук','denproxyt@mail.ru',1,1,'2026-01-30 10:23:50.000000','+79962432796','ул. Лазо, 42',0,'chief_manager',0),(3,'pbkdf2_sha256$600000$LEy70Gm3GQzPEEDbyv0em0$nH26LV33t4PKxS/ec3PmgSjmhbXMB466Hro1gRU2bmc=','2026-05-07 04:12:07.804000',0,'bogdan','Богдан','Комков','bogdankomkov@mail.ru',0,1,'2026-02-03 01:06:02.429000','89141356578','ул. Анохина, 88',0,'staff_manager',0);
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_groups`
--

DROP TABLE IF EXISTS `accounts_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_groups`
--

LOCK TABLES `accounts_user_groups` WRITE;
/*!40000 ALTER TABLE `accounts_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_user_user_permissions`
--

DROP TABLE IF EXISTS `accounts_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user_user_permissions`
--

LOCK TABLES `accounts_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_user'),(22,'Can change user',6,'change_user'),(23,'Can delete user',6,'delete_user'),(24,'Can view user',6,'view_user'),(25,'Can add schedule',7,'add_schedule'),(26,'Can change schedule',7,'change_schedule'),(27,'Can delete schedule',7,'delete_schedule'),(28,'Can view schedule',7,'view_schedule'),(29,'Can add training material',8,'add_trainingmaterial'),(30,'Can change training material',8,'change_trainingmaterial'),(31,'Can delete training material',8,'delete_trainingmaterial'),(32,'Can view training material',8,'view_trainingmaterial'),(33,'Can add training slide',9,'add_trainingslide'),(34,'Can change training slide',9,'change_trainingslide'),(35,'Can delete training slide',9,'delete_trainingslide'),(36,'Can view training slide',9,'view_trainingslide'),(37,'Can add training progress',10,'add_trainingprogress'),(38,'Can change training progress',10,'change_trainingprogress'),(39,'Can delete training progress',10,'delete_trainingprogress'),(40,'Can view training progress',10,'view_trainingprogress'),(41,'Can add training test',11,'add_trainingtest'),(42,'Can change training test',11,'change_trainingtest'),(43,'Can delete training test',11,'delete_trainingtest'),(44,'Can view training test',11,'view_trainingtest'),(45,'Can add training question',12,'add_trainingquestion'),(46,'Can change training question',12,'change_trainingquestion'),(47,'Can delete training question',12,'delete_trainingquestion'),(48,'Can view training question',12,'view_trainingquestion'),(49,'Can add training answer',13,'add_traininganswer'),(50,'Can change training answer',13,'change_traininganswer'),(51,'Can delete training answer',13,'delete_traininganswer'),(52,'Can view training answer',13,'view_traininganswer'),(53,'Can add training attempt',14,'add_trainingattempt'),(54,'Can change training attempt',14,'change_trainingattempt'),(55,'Can delete training attempt',14,'delete_trainingattempt'),(56,'Can view training attempt',14,'view_trainingattempt');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-01-30 11:10:19.171000','1','Елена',2,'[{\"changed\": {\"fields\": [\"First name\", \"Phone number\", \"Pvz address\", \"Role\"]}}]',6,1),(2,'2026-01-30 11:10:59.693000','4','Данил Гнатчук',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\", \"Staff status\", \"Superuser status\", \"Role\"]}}]',6,1),(3,'2026-01-30 11:11:11.166000','2','smoketest',3,'',6,1),(4,'2026-01-30 11:11:11.166000','3','smokeuser',3,'',6,1),(5,'2026-02-23 02:32:30.712000','1','Елена',2,'[]',6,1),(6,'2026-04-13 05:08:38.728000','1','Елена',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',6,2),(7,'2026-04-13 05:09:47.229000','1','Итоговый тест стажёра ПВЗ',2,'[{\"changed\": {\"fields\": [\"Require all other materials completed\"]}}]',11,2),(8,'2026-04-13 05:10:34.703000','3','TrainingAttempt object (3)',3,'',14,2),(9,'2026-04-13 05:10:34.726000','2','TrainingAttempt object (2)',3,'',14,2),(10,'2026-04-13 05:10:34.746000','1','TrainingAttempt object (1)',3,'',14,2),(11,'2026-04-13 05:25:48.756000','1','Итоговый тест стажёра ПВЗ',2,'[{\"changed\": {\"fields\": [\"Require all other materials completed\"]}}]',11,2),(12,'2026-04-13 05:32:34.935000','1','Итоговый тест стажёра ПВЗ',2,'[{\"changed\": {\"fields\": [\"Require all other materials completed\"]}}]',11,2),(13,'2026-04-13 05:32:55.939000','1','Итоговый тест стажёра ПВЗ',2,'[{\"changed\": {\"fields\": [\"Require all other materials completed\"]}}]',11,2);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'accounts','user'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(7,'schedule','schedule'),(5,'sessions','session'),(13,'training','traininganswer'),(14,'training','trainingattempt'),(8,'training','trainingmaterial'),(10,'training','trainingprogress'),(12,'training','trainingquestion'),(9,'training','trainingslide'),(11,'training','trainingtest');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-05-11 09:03:17.940233'),(2,'contenttypes','0002_remove_content_type_name','2026-05-11 09:03:18.105668'),(3,'auth','0001_initial','2026-05-11 09:03:18.567533'),(4,'auth','0002_alter_permission_name_max_length','2026-05-11 09:03:18.672654'),(5,'auth','0003_alter_user_email_max_length','2026-05-11 09:03:18.684814'),(6,'auth','0004_alter_user_username_opts','2026-05-11 09:03:18.698164'),(7,'auth','0005_alter_user_last_login_null','2026-05-11 09:03:18.711817'),(8,'auth','0006_require_contenttypes_0002','2026-05-11 09:03:18.719865'),(9,'auth','0007_alter_validators_add_error_messages','2026-05-11 09:03:18.733013'),(10,'auth','0008_alter_user_username_max_length','2026-05-11 09:03:18.746415'),(11,'auth','0009_alter_user_last_name_max_length','2026-05-11 09:03:18.758896'),(12,'auth','0010_alter_group_name_max_length','2026-05-11 09:03:18.785489'),(13,'auth','0011_update_proxy_permissions','2026-05-11 09:03:18.802099'),(14,'auth','0012_alter_user_first_name_max_length','2026-05-11 09:03:18.814594'),(15,'accounts','0001_initial','2026-05-11 09:03:19.393626'),(16,'accounts','0002_user_must_change_credentials','2026-05-11 09:03:19.586013'),(17,'admin','0001_initial','2026-05-11 09:03:20.088407'),(18,'admin','0002_logentry_remove_auto_add','2026-05-11 09:03:20.118207'),(19,'admin','0003_logentry_add_action_flag_choices','2026-05-11 09:03:20.133487'),(20,'schedule','0001_initial','2026-05-11 09:03:20.445510'),(21,'sessions','0001_initial','2026-05-11 09:03:20.583789'),(22,'training','0001_initial','2026-05-11 09:03:20.669470'),(23,'training','0002_trainingquestion_alter_trainingmaterial_options_and_more','2026-05-11 09:03:23.636982'),(24,'training','0003_extended_test_questions','2026-05-11 09:03:25.491143'),(25,'training','0004_trainingmaterial_pdf_file_and_more','2026-05-11 09:03:25.598509');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('42g1lh57ufg4wcl28e024c5hlystnykw','.eJxVjEEOwiAQRe_C2hCgpcy4dO8ZGmYYbNVAUtqV8e7apAvd_vfef6kxbus0bk2WcU7qrKw6_W4U-SFlB-key61qrmVdZtK7og_a9LUmeV4O9-9gim361oyOIA4GqXOuc4PtfQIkMo6zuND36CEHsOAxiGEWQhPs0EFOPjOKen8Awrc3YA:1vn58V:PSCV8crhA9VV4hKkaEAHc2o36HCA67LODTw3Ynnsz08','2026-02-17 01:23:23.799000'),('68ptvfwn6y54tyzle8mchly8mz2ycyzv','.eJxVjEEOwiAQRe_C2hBo6QAu3XsGMsOAVA0kpV0Z765NutDtf-_9lwi4rSVsPS1hZnEWRpx-N8L4SHUHfMd6azK2ui4zyV2RB-3y2jg9L4f7d1Cwl2-tvZsAlWEgA4lNGjVwVBk1jjlZi4qHwVk7qUweAV3OmRAojkDeoBPvD-ycOJY:1wCA48:MRqj2irsCu3nHRrSG6Xm_Cx_JYQ_jtfn-uCVSVFbnFI','2026-04-27 05:42:32.825000'),('6fruaozx61wlg8gc6wxv1kh348uwear8','.eJxVjEEOwiAQRe_C2hCgpcy4dO8ZGmYYbNVAUtqV8e7apAvd_vfef6kxbus0bk2WcU7qrKw6_W4U-SFlB-key61qrmVdZtK7og_a9LUmeV4O9-9gim361oyOIA4GqXOuc4PtfQIkMo6zuND36CEHsOAxiGEWQhPs0EFOPjOKen8Awrc3YA:1vn4vo:TMSF1s69V3tGKM26VqFy2ypZAaM4O0Piktk0wMA5u-k','2026-02-17 01:10:16.022000'),('9nkr474zh1k2ts1450nk7x8z0lmbpwop','.eJxVjDsOwjAQBe_iGlkOWfyhpOcM1u56jQPIluKkQtwdIqWA9s3Me6mI61Li2mWOU1JnNajD70bID6kbSHest6a51WWeSG-K3mnX15bkedndv4OCvXxrgBFtOmLKAhAMwRg4syEbIKMNPiMEbxwRnVCsB2_YDdaJEHumIOr9AfQnOKc:1wMMaw:bV8oSw_PEzDnVjBJv9h029yXkmRurOv9XbsTXu-s4NE','2026-05-25 09:06:34.773317'),('h6voewzkmnmmqrhtbyd3z32z7gjzcqn9','.eJxVjDsOwjAQBe_iGln-LAmmpOcM1nrXiwPIluKkQtwdIqWA9s3Me6mI61Li2vMcJ1ZnZdXhd0tIj1w3wHest6ap1WWekt4UvdOur43z87K7fwcFe_nWKAaEwCOzGEHKgdORLIB1AyTKMrAXL4bGcAqYAoGzCQGCxdE6EPX-ACDPOOM:1wKr4x:AdpONp3pLKemSZ0lnBHheCkxHQ5bV63PaYXcs-CP9Ck','2026-05-21 05:15:19.699000'),('junp26ggchzb1cm2r3aysawsks7jdzgk','.eJxVjMsOwiAQRf-FtSHlXVy69xvIwAxSNZCUdmX8dyXpQpO7uufkvFiAfSth77SGBdmZGXb6_SKkB9UB8A711nhqdVuXyIfCD9r5tSE9L4f7FyjQy8gKDTbb2VvvQctsNUkDkDFHI6dIXmqjRIqAzmHSQOo7lGKayWWtFHt_AOkcODQ:1w4WkM:yosqlRmTP26YDCMAt0BFWlZSK_hb6Rs1Lesj1RXqbAA','2026-04-06 04:18:34.613000'),('kuf9j6wd4988nyw1leeedp9elqy0hu84','.eJxVjEEOwiAQRe_C2hCgpcy4dO8ZGmYYbNVAUtqV8e7apAvd_vfef6kxbus0bk2WcU7qrKw6_W4U-SFlB-key61qrmVdZtK7og_a9LUmeV4O9-9gim361oyOIA4GqXOuc4PtfQIkMo6zuND36CEHsOAxiGEWQhPs0EFOPjOKen8Awrc3YA:1vn4RS:_0UtVHNl23Y_QTzpNuyKDXXxAE0WUFA8C0ft3liFl-c','2026-02-17 00:38:54.217000'),('lqcy4mj5ymbxf6tvqwsg8r8u25wa8x4n','.eJxVjEEOwiAQRe_C2hCmHQq4dO8ZyDCAVA0kpV0Z765NutDtf-_9l_C0rcVvPS1-juIsUJx-t0D8SHUH8U711iS3ui5zkLsiD9rltcX0vBzu30GhXr61HiZnySFoAMhKhdEh5hwBOXJWWhsLZmKKxgCMKnFgZTAYy-BQD0m8P7xHNw4:1vlm4T:D98JZ--bE5bPfS6XKMY2OxlFPxLKlWgca7N76h20vGQ','2026-02-13 10:49:49.516000'),('n6txocfq14t6usdo1gmkzkrw134ben4b','.eJxVjEEOwiAQRe_C2hCgpcy4dO8ZGmYYbNVAUtqV8e7apAvd_vfef6kxbus0bk2WcU7qrKw6_W4U-SFlB-key61qrmVdZtK7og_a9LUmeV4O9-9gim361oyOIA4GqXOuc4PtfQIkMo6zuND36CEHsOAxiGEWQhPs0EFOPjOKen8Awrc3YA:1vln10:a-yK5RRgLX1D4r_1PphJWIKZ44PB7WN0vwH_ULO7N9I','2026-02-13 11:50:18.181000'),('pquwbaw0mv31y38zqcaor9yh20x02eim','.eJxVjEEOwiAQRe_C2hCoQMGl-56BzAyDVA0kpV0Z765NutDtf-_9l4iwrSVunZc4J3ERWpx-NwR6cN1BukO9NUmtrsuMclfkQbucWuLn9XD_Dgr08q2tAho9Q2DL6MAbFcCA05QREUbnBnCJMGeVWJucrA-DyV7RmaxGcuL9ARH7ORs:1vuSvx:CVq6GQ2Qtjr71A82hT1b0VIqcJuvWBdYCTVXcXvyQFw','2026-03-09 10:12:57.687000'),('upgaqgxehjl6uki9ul6e2unxhj4y6gdw','.eJxVjEEOwiAQRe_C2hCgpcy4dO8ZGmYYbNVAUtqV8e7apAvd_vfef6kxbus0bk2WcU7qrKw6_W4U-SFlB-key61qrmVdZtK7og_a9LUmeV4O9-9gim361oyOIA4GqXOuc4PtfQIkMo6zuND36CEHsOAxiGEWQhPs0EFOPjOKen8Awrc3YA:1vlmhl:xZXFdtMFGmqX2VeOa8sE1tvlYXeDP8Njs6TtQ1Kxths','2026-02-13 11:30:25.375000');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule_schedule`
--

DROP TABLE IF EXISTS `schedule_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_schedule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `shifts` decimal(4,2) NOT NULL,
  `comment` longtext NOT NULL,
  `pvz_address` varchar(255) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `schedule_schedule_user_id_date_2d789b4e_uniq` (`user_id`,`date`),
  CONSTRAINT `schedule_schedule_user_id_e9a0b84b_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule_schedule`
--

LOCK TABLES `schedule_schedule` WRITE;
/*!40000 ALTER TABLE `schedule_schedule` DISABLE KEYS */;
INSERT INTO `schedule_schedule` VALUES (9,'2026-01-31',1.00,'','ул. Шилова, 81',1),(11,'2026-01-01',1.00,'','ул. Ленина, 54',2),(16,'2026-02-02',1.00,'','ул. Лазо, 42',2),(17,'2026-02-03',1.00,'','ул. Лазо, 42',2),(18,'2026-02-04',1.00,'','ул. Лазо, 42',2),(20,'2026-02-02',1.00,'','ул. Лазо, 42',3),(21,'2026-02-03',1.00,'','ул. Лазо, 42',3),(22,'2026-02-04',1.00,'','ул. Лазо, 42',3),(23,'2026-02-05',1.00,'','ул. Лазо, 42',3),(24,'2026-02-06',1.00,'','ул. Лазо, 42',3),(25,'2026-02-07',1.00,'','ул. Лазо, 42',3),(26,'2026-02-08',1.00,'','ул. Лазо, 42',3),(27,'2026-02-09',1.00,'','ул. Лазо, 42',3),(28,'2026-02-10',1.00,'','ул. Лазо, 42',3),(29,'2026-02-11',1.00,'','ул. Лазо, 42',3),(30,'2026-02-12',1.00,'','ул. Лазо, 42',3),(31,'2026-02-13',1.00,'','ул. Лазо, 42',3),(32,'2026-02-14',1.00,'','ул. Лазо, 42',3),(33,'2026-02-15',1.00,'','ул. Лазо, 42',3),(34,'2026-02-16',1.00,'','ул. Лазо, 42',3),(35,'2026-02-28',1.00,'','ул. Лазо, 42',3),(36,'2026-02-23',1.00,'','ул. Лазо, 42',3),(37,'2026-02-23',1.00,'','ул. Лазо, 42',2),(39,'2026-02-17',1.00,'','ул. Лазо, 42',3),(40,'2026-02-17',1.00,'','ул. Лазо, 42',2),(41,'2026-04-01',1.00,'','ул. Лазо, 42',2),(56,'2026-05-01',1.00,'','ул. Анохина, 88',3),(57,'2026-05-02',1.00,'','ул. Анохина, 88',3),(58,'2026-05-03',1.00,'','ул. Анохина, 88',3),(59,'2026-05-04',1.00,'','ул. Анохина, 88',3),(60,'2026-05-05',1.00,'','ул. Анохина, 88',3),(61,'2026-05-06',1.00,'','ул. Анохина, 88',3),(62,'2026-05-07',1.00,'','ул. Анохина, 88',3),(63,'2026-05-01',1.00,'','ул. Лазо, 42',2),(64,'2026-05-02',1.00,'','ул. Лазо, 42',2),(65,'2026-05-03',1.00,'','ул. Лазо, 42',2),(66,'2026-05-04',1.00,'','ул. Лазо, 42',2),(67,'2026-05-05',1.00,'','ул. Лазо, 42',2),(68,'2026-05-06',1.00,'','ул. Лазо, 42',2),(69,'2026-05-07',1.00,'','ул. Лазо, 42',2),(70,'2026-05-31',1.00,'','ул. Лазо, 42',2),(71,'2026-05-30',1.00,'','ул. Лазо, 42',2),(72,'2026-05-29',1.00,'','ул. Лазо, 42',2),(73,'2026-05-28',1.00,'','ул. Лазо, 42',2),(74,'2026-05-27',1.00,'','ул. Лазо, 42',2),(75,'2026-05-26',1.00,'','ул. Лазо, 42',2),(76,'2026-05-25',1.00,'','ул. Лазо, 42',2),(77,'2026-05-18',1.00,'','ул. Лазо, 42',2),(78,'2026-05-19',1.00,'','ул. Лазо, 42',2),(79,'2026-05-20',1.00,'','ул. Лазо, 42',2),(80,'2026-05-21',0.50,'','ул. Лазо, 42',2),(81,'2026-05-22',0.50,'','ул. Лазо, 42',2),(82,'2026-05-23',0.50,'','ул. Лазо, 42',2),(83,'2026-05-11',1.50,'','ул. Лазо, 42',2),(84,'2026-05-08',1.00,'','ул. Анохина, 88',2),(85,'2026-05-15',1.00,'','ул. Лазо, 42',3),(86,'2026-05-11',0.17,'','ул. Богомягкова, 60',1);
/*!40000 ALTER TABLE `schedule_schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_traininganswer`
--

DROP TABLE IF EXISTS `training_traininganswer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_traininganswer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `text` varchar(500) NOT NULL,
  `is_correct` tinyint(1) NOT NULL,
  `question_id` bigint NOT NULL,
  `correct_sequence` smallint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `training_trainingans_question_id_ff14f978_fk_training_` (`question_id`),
  CONSTRAINT `training_trainingans_question_id_ff14f978_fk_training_` FOREIGN KEY (`question_id`) REFERENCES `training_trainingquestion` (`id`),
  CONSTRAINT `training_traininganswer_chk_1` CHECK ((`correct_sequence` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=231 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_traininganswer`
--

LOCK TABLES `training_traininganswer` WRITE;
/*!40000 ALTER TABLE `training_traininganswer` DISABLE KEYS */;
INSERT INTO `training_traininganswer` VALUES (116,'7 дней',0,31,0),(117,'14 дней',1,31,0),(118,'21 день',0,31,0),(119,'30 дней',0,31,0),(120,'Выдать товар и попросить клиента оформить заявку',0,32,0),(121,'Поставить отметку о браке в программе и сохранить видеозапись',1,32,0),(122,'Просто снять товар с выдачи без отметки',0,32,0),(123,'Отправить товар на склад без оформления',0,32,0),(124,'2 для брака + 2 для остальных товаров',0,33,0),(125,'3 для брака + 3 для остальных товаров',1,33,0),(126,'5 для брака + 5 для остальных товаров',0,33,0),(127,'Неограниченно',0,33,0),(128,'24 часа',0,34,0),(129,'3 дня',0,34,0),(130,'7 дней',1,34,0),(131,'30 дней',0,34,0),(132,'Принять возврат сразу в ПВЗ',0,35,0),(133,'Направить клиента на оформление заявки на брак в ЛК',1,35,0),(134,'Отметить брак и выдать деньги на месте',0,35,0),(135,'Отказать в возврате',0,35,0),(136,'3 кг',0,36,0),(137,'5 кг',1,36,0),(138,'10 кг',0,36,0),(139,'15 кг',0,36,0),(140,'Отклейка подошвы',0,37,0),(141,'Следы клея по периметру подошвы менее 3 мм',1,37,0),(142,'Разрыв шва',0,37,0),(143,'Деформация изделия',0,37,0),(144,'Видео должно быть снято на телефон',0,38,0),(145,'Видео должно быть непрерывным, без склеек, с камер ПВЗ',1,38,0),(146,'Достаточно скриншотов',0,38,0),(147,'Видео должно быть длиной не более 1 минуты',0,38,0),(148,'Отправить на склад',0,39,0),(149,'Вернуть клиенту',0,39,0),(150,'Утилизировать, предварительно убрав символику WB',1,39,0),(151,'Оставить на хранение',0,39,0),(152,'1',0,40,0),(153,'2',0,40,0),(154,'3',0,40,0),(155,'4',1,40,0),(156,'Парфюмерно-косметические товары',1,41,0),(157,'Нижнее бельё и чулочно-носочные изделия',1,41,0),(158,'Ювелирные изделия',1,41,0),(159,'Одежда верхняя',0,41,0),(160,'Предметы личной гигиены',1,41,0),(161,'Проверить работу камер и сканера',1,42,0),(162,'Проверить целостность упаковки',1,42,0),(163,'Отсканировать стикер товара',1,42,0),(164,'Вскрыть заводскую упаковку для проверки содержимого',0,42,0),(165,'Показать повреждённую упаковку на камеру',1,42,0),(166,'Клиент отказался до примерки, товар надлежащего качества',1,43,0),(167,'Клиент обнаружил брак до примерки',1,43,0),(168,'Клиент отказался после примерки, товар возвратный и надлежащего качества',1,43,0),(169,'Клиент отказался после примерки от неотказного товара',0,43,0),(170,'Товар утерян и не найден',1,43,0),(171,'Загрязнение',1,44,0),(172,'Дефект ткани',1,44,0),(173,'Потёртости/царапины',1,44,0),(174,'Отличия товара от фото (не влияющие на характеристики)',0,44,0),(175,'Разбит/разлит',1,44,0),(176,'Добавлять обычные возвраты в МП-коробку',1,45,0),(177,'Перемещать товар между коробками более 2 раз',1,45,0),(178,'Оставлять коробку открытой более 48 часов',1,45,0),(179,'Наклеивать стикер поверх старой маркировки',0,45,0),(180,'Принимать в коробку более 60 товаров',1,45,0),(181,'Паспорт',1,46,0),(182,'Специальный QR-код из мессенджера MAX',1,46,0),(183,'Скриншот паспорта из телефона',0,46,0),(184,'Иной документ, удостоверяющий личность',1,46,0),(185,'Устное подтверждение клиента',0,46,0),(186,'Отсканировать QR-код из раздела «Возврат товара» ИЛИ ШК товара',1,47,0),(187,'Проверить соответствие товара карточке',1,47,0),(188,'Добавить товар в возвратную коробку в течение 24/48 часов',1,47,0),(189,'Принимать товар без проверки заявки на брак (если срок >14 дней)',0,47,0),(190,'Переупаковать товар при необходимости',1,47,0),(191,'Непрерывность, без склеек',1,48,0),(192,'Съёмка с камер ПВЗ',1,48,0),(193,'Хранение на сервере минимум 90 дней',1,48,0),(194,'Съёмка на телефон менеджера',0,48,0),(195,'Видно весь процесс: от вскрытия коробки до передачи курьеру',1,48,0),(196,'Отсканировать стикер коробки',0,49,1),(197,'Открыть коробку, проверить целостность упаковки',0,49,2),(198,'Отсканировать стикер товара',0,49,3),(199,'Отнести товар в указанную ячейку',0,49,4),(200,'Продолжать сканирование, пока все товары не будут приняты',0,49,5),(201,'Открыть заказ по QR-коду или номеру телефона',0,50,1),(202,'Проверить документы для товаров 18+ (если есть)',0,50,2),(203,'Принести товары со склада и сверить с заказом',0,50,3),(204,'Провести оплату (если требуется)',0,50,4),(205,'Выдать товар и пакеты',0,50,5),(206,'Нажать «Заполнить форму брака»',0,51,1),(207,'Выбрать категорию и тип брака',0,51,2),(208,'Приложить 4 фото (спереди, сзади, дефект, ШК)',0,51,3),(209,'Указать комментарий',0,51,4),(210,'Нажать «Отправить»',0,51,5),(211,'Перейти в раздел «Вернуть» / «Коробки»',0,52,1),(212,'Нажать «Создать коробку»',0,52,2),(213,'Выбрать тип коробки «Брак»',0,52,3),(214,'Отсканировать стикер коробки или создать без наклейки',0,52,4),(215,'Начать сканировать бракованные товары',0,52,5),(216,'Отсканировать QR-код курьера в разделе «Приёмка»',0,53,1),(217,'Проверить товары на брак перед сканированием',0,53,2),(218,'Отсканировать товары',0,53,3),(219,'Нажать «Завершить»',0,53,4),(220,'Разложить товары: в ячейку или в возвратную коробку',0,53,5),(221,'Перейти в раздел «Зависшие ШК»',0,54,1),(222,'Найти товар в разделе «Зависшие ШК»',0,54,2),(223,'Нажать «Оспорить удержание» → «Отправить»',0,54,3),(224,'Описать в комментарии, что происходит на видео',0,54,4),(225,'Прикрепить видео или ссылку на него',0,54,5),(226,'Перейти в раздел «Возврат» → вкладка «WB MP»',0,55,1),(227,'Отсканировать стикер формата WB-MP',0,55,2),(228,'Проверить, что создалась открытая коробка с тем же номером',0,55,3),(229,'В присутствии поставщика открыть коробку и отсканировать товары',0,55,4),(230,'Закрыть коробку в программе',0,55,5);
/*!40000 ALTER TABLE `training_traininganswer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_trainingattempt`
--

DROP TABLE IF EXISTS `training_trainingattempt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_trainingattempt` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `score` int unsigned NOT NULL,
  `max_score` int unsigned NOT NULL,
  `passed` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `material_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `breakdown` json NOT NULL DEFAULT (_utf8mb4'[]'),
  `responses` json NOT NULL DEFAULT (_utf8mb4'{}'),
  PRIMARY KEY (`id`),
  KEY `training_trainingatt_material_id_48a60003_fk_training_` (`material_id`),
  KEY `training_trainingattempt_user_id_815ae762_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `training_trainingatt_material_id_48a60003_fk_training_` FOREIGN KEY (`material_id`) REFERENCES `training_trainingmaterial` (`id`),
  CONSTRAINT `training_trainingattempt_user_id_815ae762_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `training_trainingattempt_chk_1` CHECK ((`score` >= 0)),
  CONSTRAINT `training_trainingattempt_chk_2` CHECK ((`max_score` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_trainingattempt`
--

LOCK TABLES `training_trainingattempt` WRITE;
/*!40000 ALTER TABLE `training_trainingattempt` DISABLE KEYS */;
INSERT INTO `training_trainingattempt` VALUES (4,0,30,0,'2026-04-13 05:29:25.601000',304,2,'[{\"ok\": false, \"text\": \"Какой максимальный срок хранения товара в ПВЗ до автоматической отмены?\", \"detail\": {\"answer_id\": null}, \"question_id\": 31, \"question_type\": \"single\", \"question_order\": 1, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Что нужно сделать при обнаружении брака на товаре ДО выдачи клиенту?\", \"detail\": {\"answer_id\": null}, \"question_id\": 32, \"question_type\": \"single\", \"question_order\": 2, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Сколько открытых возвратных коробок может быть одновременно в ПВЗ?\", \"detail\": {\"answer_id\": null}, \"question_id\": 33, \"question_type\": \"single\", \"question_order\": 3, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какой минимальный срок для оспаривания удержания за подмену/брак/зависший ШК?\", \"detail\": {\"answer_id\": null}, \"question_id\": 34, \"question_type\": \"single\", \"question_order\": 4, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Что делать, если клиент обнаружил брак ПОСЛЕ примерки?\", \"detail\": {\"answer_id\": null}, \"question_id\": 35, \"question_type\": \"single\", \"question_order\": 5, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какой вес маркетплейс-коробки является максимальным для приёмки?\", \"detail\": {\"answer_id\": null}, \"question_id\": 36, \"question_type\": \"single\", \"question_order\": 6, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Что НЕ является браком для обуви?\", \"detail\": {\"answer_id\": null}, \"question_id\": 37, \"question_type\": \"single\", \"question_order\": 7, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какое требование обязательно для видео при оспаривании удержаний?\", \"detail\": {\"answer_id\": null}, \"question_id\": 38, \"question_type\": \"single\", \"question_order\": 8, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Что делать с товаром, который попал в раздел «Утиль»?\", \"detail\": {\"answer_id\": null}, \"question_id\": 39, \"question_type\": \"single\", \"question_order\": 9, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Сколько фото необходимо приложить при заполнении формы отметки о браке?\", \"detail\": {\"answer_id\": null}, \"question_id\": 40, \"question_type\": \"single\", \"question_order\": 10, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какие товары относятся к НЕвозвратным? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 41, \"question_type\": \"multiple\", \"question_order\": 11, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какие действия необходимо выполнить при приёмке товара? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 42, \"question_type\": \"multiple\", \"question_order\": 12, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"В каких случаях можно снять товар с выдачи? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 43, \"question_type\": \"multiple\", \"question_order\": 13, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какие типы брака можно оспорить? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 44, \"question_type\": \"multiple\", \"question_order\": 14, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Что запрещено делать при работе с возвратными коробками? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 45, \"question_type\": \"multiple\", \"question_order\": 15, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какие документы можно принять для подтверждения возраста 18+? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 46, \"question_type\": \"multiple\", \"question_order\": 16, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Какие действия выполняются при возврате товара из дома? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 47, \"question_type\": \"multiple\", \"question_order\": 17, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Что входит в требования к видео для оспаривания? (выберите все верные)\", \"detail\": {\"answer_ids\": []}, \"question_id\": 48, \"question_type\": \"multiple\", \"question_order\": 18, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Порядок действий при приёмке товара в десктоп-приложении (расставьте шаги):\", \"detail\": {\"ordered_ids\": [200, 198, 196, 197, 199]}, \"question_id\": 49, \"question_type\": \"ordering\", \"question_order\": 19, \"user_answer_summary\": \"Продолжать сканирование, пока все товары не будут приняты; Отсканировать стикер товара; Отсканировать стикер коробки; Открыть коробку, проверить целостность упаковки; Отнести товар в указанную ячейку\"}, {\"ok\": false, \"text\": \"Порядок действий при выдаче товара клиенту (расставьте шаги):\", \"detail\": {\"ordered_ids\": [203, 204, 205, 201, 202]}, \"question_id\": 50, \"question_type\": \"ordering\", \"question_order\": 20, \"user_answer_summary\": \"Принести товары со склада и сверить с заказом; Провести оплату (если требуется); Выдать товар и пакеты; Открыть заказ по QR-коду или номеру телефона; Проверить документы для товаров 18+ (если есть)\"}, {\"ok\": false, \"text\": \"Порядок заполнения формы отметки о браке (расставьте шаги):\", \"detail\": {\"ordered_ids\": [207, 208, 206, 210, 209]}, \"question_id\": 51, \"question_type\": \"ordering\", \"question_order\": 21, \"user_answer_summary\": \"Выбрать категорию и тип брака; Приложить 4 фото (спереди, сзади, дефект, ШК); Нажать «Заполнить форму брака»; Нажать «Отправить»; Указать комментарий\"}, {\"ok\": false, \"text\": \"Порядок создания возвратной коробки для брака (расставьте шаги):\", \"detail\": {\"ordered_ids\": [214, 215, 212, 211, 213]}, \"question_id\": 52, \"question_type\": \"ordering\", \"question_order\": 22, \"user_answer_summary\": \"Отсканировать стикер коробки или создать без наклейки; Начать сканировать бракованные товары; Нажать «Создать коробку»; Перейти в раздел «Вернуть» / «Коробки»; Выбрать тип коробки «Брак»\"}, {\"ok\": false, \"text\": \"Порядок действий при возврате товара курьером (расставьте шаги):\", \"detail\": {\"ordered_ids\": [219, 218, 220, 217, 216]}, \"question_id\": 53, \"question_type\": \"ordering\", \"question_order\": 23, \"user_answer_summary\": \"Нажать «Завершить»; Отсканировать товары; Разложить товары: в ячейку или в возвратную коробку; Проверить товары на брак перед сканированием; Отсканировать QR-код курьера в разделе «Приёмка»\"}, {\"ok\": false, \"text\": \"Порядок оспаривания удержания за зависший ШК (расставьте шаги):\", \"detail\": {\"ordered_ids\": [224, 222, 225, 223, 221]}, \"question_id\": 54, \"question_type\": \"ordering\", \"question_order\": 24, \"user_answer_summary\": \"Описать в комментарии, что происходит на видео; Найти товар в разделе «Зависшие ШК»; Прикрепить видео или ссылку на него; Нажать «Оспорить удержание» → «Отправить»; Перейти в раздел «Зависшие ШК»\"}, {\"ok\": false, \"text\": \"Порядок приёмки маркетплейс-коробки (расставьте шаги):\", \"detail\": {\"ordered_ids\": [229, 228, 226, 227, 230]}, \"question_id\": 55, \"question_type\": \"ordering\", \"question_order\": 25, \"user_answer_summary\": \"В присутствии поставщика открыть коробку и отсканировать товары; Проверить, что создалась открытая коробка с тем же номером; Перейти в раздел «Возврат» → вкладка «WB MP»; Отсканировать стикер формата WB-MP; Закрыть коробку в программе\"}, {\"ok\": false, \"text\": \"Порядок: Приёмка товара с повреждённым ШК. Указанная последовательность шагов верна?\", \"detail\": {\"judgment\": \"\", \"order_input\": \"\"}, \"question_id\": 56, \"question_type\": \"order_judgment\", \"question_order\": 26, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Порядок: Возврат товара из дома с одобренной заявкой на брак. Последовательность верна?\", \"detail\": {\"judgment\": \"\", \"order_input\": \"\"}, \"question_id\": 57, \"question_type\": \"order_judgment\", \"question_order\": 27, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Порядок: Смена ячейки с помощью сканера (десктоп). Последовательность верна?\", \"detail\": {\"judgment\": \"\", \"order_input\": \"\"}, \"question_id\": 58, \"question_type\": \"order_judgment\", \"question_order\": 28, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Порядок: Обнаружение подмены до примерки. Последовательность верна? (Учтите: пункт «сообщить клиенту, что только по заявке» в данном сценарии неверен.)\", \"detail\": {\"judgment\": \"\", \"order_input\": \"\"}, \"question_id\": 59, \"question_type\": \"order_judgment\", \"question_order\": 29, \"user_answer_summary\": \"—\"}, {\"ok\": false, \"text\": \"Порядок: Утилизация товара. Последовательность верна?\", \"detail\": {\"judgment\": \"\", \"order_input\": \"\"}, \"question_id\": 60, \"question_type\": \"order_judgment\", \"question_order\": 30, \"user_answer_summary\": \"—\"}]','{\"41\": [], \"42\": [], \"43\": [], \"44\": [], \"45\": [], \"46\": [], \"47\": [], \"48\": [], \"49\": [200, 198, 196, 197, 199], \"50\": [203, 204, 205, 201, 202], \"51\": [207, 208, 206, 210, 209], \"52\": [214, 215, 212, 211, 213], \"53\": [219, 218, 220, 217, 216], \"54\": [224, 222, 225, 223, 221], \"55\": [229, 228, 226, 227, 230], \"56\": {\"order\": \"\", \"judgment\": \"\"}, \"57\": {\"order\": \"\", \"judgment\": \"\"}, \"58\": {\"order\": \"\", \"judgment\": \"\"}, \"59\": {\"order\": \"\", \"judgment\": \"\"}, \"60\": {\"order\": \"\", \"judgment\": \"\"}}');
/*!40000 ALTER TABLE `training_trainingattempt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_trainingmaterial`
--

DROP TABLE IF EXISTS `training_trainingmaterial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_trainingmaterial` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `content` longtext NOT NULL,
  `description` longtext NOT NULL DEFAULT (_utf8mb4''),
  `module_title` varchar(255) NOT NULL,
  `order` int unsigned NOT NULL,
  `pdf_file` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `training_trainingmaterial_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=305 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_trainingmaterial`
--

LOCK TABLES `training_trainingmaterial` WRITE;
/*!40000 ALTER TABLE `training_trainingmaterial` DISABLE KEYS */;
INSERT INTO `training_trainingmaterial` VALUES (267,'Сервис доставок WB Track. Десктоп-приложение','PDF_URL:/static/training/material/WB Track/Сервис доставок WB Track. Десктоп-приложение.pdf','PDF-материал','WB Track',1,''),(268,'Сервис доставок WB Track. Мобильное приложение','PDF_URL:/static/training/material/WB Track/Сервис доставок WB Track. Мобильное приложение.pdf','PDF-материал','WB Track',2,''),(269,'Работа с курьерскими заказами. Десктоп-приложение','PDF_URL:/static/training/material/WB Курьер/Работа с курьерскими заказами. Десктоп-приложение.pdf','PDF-материал','WB Курьер',1,''),(270,'Работа с курьерскими заказами. Мобильное приложение','PDF_URL:/static/training/material/WB Курьер/Работа с курьерскими заказами. Мобильное приложение.pdf','PDF-материал','WB Курьер',2,''),(271,'Зависшие ШК','PDF_URL:/static/training/material/Брак, Подмены, Зависшие ШК/Зависшие ШК.pdf','PDF-материал','Брак, Подмены, Зависшие ШК',1,''),(272,'Инструкция по браку','PDF_URL:/static/training/material/Брак, Подмены, Зависшие ШК/Инструкция по браку.pdf','PDF-материал','Брак, Подмены, Зависшие ШК',2,''),(273,'Как проверить товар на брак','PDF_URL:/static/training/material/Брак, Подмены, Зависшие ШК/Как проверить товар на брак.pdf','PDF-материал','Брак, Подмены, Зависшие ШК',3,''),(274,'Как работать с товарами подменами','PDF_URL:/static/training/material/Брак, Подмены, Зависшие ШК/Как работать с товарами подменами.pdf','PDF-материал','Брак, Подмены, Зависшие ШК',4,''),(275,'Отметка о браке. Десктоп-приложение','PDF_URL:/static/training/material/Брак, Подмены, Зависшие ШК/Отметка о браке. Десктоп-приложение.pdf','PDF-материал','Брак, Подмены, Зависшие ШК',5,''),(276,'Отметка о браке. Мобильное приложение','PDF_URL:/static/training/material/Брак, Подмены, Зависшие ШК/Отметка о браке. Мобильное приложение.pdf','PDF-материал','Брак, Подмены, Зависшие ШК',6,''),(277,'Инструкция «Оплата через WB Кошелёк»','PDF_URL:/static/training/material/ВБ кошелек/Инструкция «Оплата через WB Кошелёк».pdf','PDF-материал','ВБ кошелек',1,''),(278,'Возврат банковских карт. Десктоп-приложение','PDF_URL:/static/training/material/Возврат/Возврат банковских карт. Десктоп-приложение.pdf','PDF-материал','Возврат',1,''),(279,'Возврат банковских карт. Мобильное приложение','PDF_URL:/static/training/material/Возврат/Возврат банковских карт. Мобильное приложение.pdf','PDF-материал','Возврат',2,''),(280,'Возврат картона. Десктоп-приложение','PDF_URL:/static/training/material/Возврат/Возврат картона. Десктоп-приложение.pdf','PDF-материал','Возврат',3,''),(281,'Возврат картона. Мобильное приложение','PDF_URL:/static/training/material/Возврат/Возврат картона. Мобильное приложение.pdf','PDF-материал','Возврат',4,''),(282,'Возврат товаров из дома. Десктоп-приложение','PDF_URL:/static/training/material/Возврат/Возврат товаров из дома. Десктоп-приложение.pdf','PDF-материал','Возврат',5,''),(283,'Возврат товаров из дома. Мобильное приложение','PDF_URL:/static/training/material/Возврат/Возврат товаров из дома. Мобильное приложение.pdf','PDF-материал','Возврат',6,''),(284,'Возврат товаров. Десктоп-приложение','PDF_URL:/static/training/material/Возврат/Возврат товаров. Десктоп-приложение.pdf','PDF-материал','Возврат',7,''),(285,'Возврат товаров. Мобильное приложение','PDF_URL:/static/training/material/Возврат/Возврат товаров. Мобильное приложение.pdf','PDF-материал','Возврат',8,''),(286,'Возвратная коробка для брака','PDF_URL:/static/training/material/Возврат/Возвратная коробка для брака.pdf','PDF-материал','Возврат',9,''),(287,'Как работать с невозвратными и неотказными','PDF_URL:/static/training/material/Возврат/Как работать с невозвратными и неотказными.pdf','PDF-материал','Возврат',10,''),(288,'Отмена товаров в клиентском приложении','PDF_URL:/static/training/material/Возврат/Отмена товаров в клиентском приложении.pdf','PDF-материал','Возврат',11,''),(289,'Утилизация товаров. Десктоп-приложение','PDF_URL:/static/training/material/Возврат/Утилизация товаров. Десктоп-приложение.pdf','PDF-материал','Возврат',12,''),(290,'Выдача товаров. Десктоп-приложение','PDF_URL:/static/training/material/Выдача/Выдача товаров. Десктоп-приложение.pdf','PDF-материал','Выдача',1,''),(291,'Выдача товаров. Мобильное приложение','PDF_URL:/static/training/material/Выдача/Выдача товаров. Мобильное приложение.pdf','PDF-материал','Выдача',2,''),(292,'Приёмка и выдача подарочных сертификатов','PDF_URL:/static/training/material/Выдача/Приёмка и выдача подарочных сертификатов.pdf','PDF-материал','Выдача',3,''),(293,'Работа с товарами поставщика','PDF_URL:/static/training/material/Выдача/Работа с товарами поставщика.pdf','PDF-материал','Выдача',4,''),(294,'Снятие товара с выдачи. Десктоп-приложение','PDF_URL:/static/training/material/Выдача/Снятие товара с выдачи. Десктоп-приложение.pdf','PDF-материал','Выдача',5,''),(295,'Нестандартные ситуации при приёмке товаров. Десктоп-приложение','PDF_URL:/static/training/material/Приемка/Нестандартные ситуации при приёмке товаров. Десктоп-приложение.pdf','PDF-материал','Приемка',1,''),(296,'Поиск по ШК. Десктоп-приложение','PDF_URL:/static/training/material/Приемка/Поиск по ШК. Десктоп-приложение.pdf','PDF-материал','Приемка',2,''),(297,'Приёмка маркетплейс-коробки. Десктоп-приложение','PDF_URL:/static/training/material/Приемка/Приёмка маркетплейс-коробки. Десктоп-приложение.pdf','PDF-материал','Приемка',3,''),(298,'Приёмка маркетплейс-коробки. Мобильное приложение','PDF_URL:/static/training/material/Приемка/Приёмка маркетплейс-коробки. Мобильное приложение.pdf','PDF-материал','Приемка',4,''),(299,'Приёмка товаров. Десктоп-приложение','PDF_URL:/static/training/material/Приемка/Приёмка товаров. Десктоп-приложение.pdf','PDF-материал','Приемка',5,''),(300,'Приёмка товаров. Мобильное приложение','PDF_URL:/static/training/material/Приемка/Приёмка товаров. Мобильное приложение.pdf','PDF-материал','Приемка',6,''),(301,'Смена ячейки с помощью сканера. Десктоп-приложение','PDF_URL:/static/training/material/Смена ячейки с помощью сканера/Смена ячейки с помощью сканера. Десктоп-приложение.pdf','PDF-материал','Смена ячейки с помощью сканера',1,''),(302,'Смена ячейки с помощью сканера. Мобильное приложение','PDF_URL:/static/training/material/Смена ячейки с помощью сканера/Смена ячейки с помощью сканера. Мобильное приложение.pdf','PDF-материал','Смена ячейки с помощью сканера',2,''),(303,'Создание тикетов','PDF_URL:/static/training/material/Создание тикетов/Создание тикетов.pdf','PDF-материал','Создание тикетов',1,''),(304,'Тест для стажёров ПВЗ Wildberries','FINAL_PVZ_EXAM','Проверка знаний по инструкциям.\n\nВсего вопросов: 30.\nТипы: один ответ, несколько ответов, установление порядка, проверка порядка.\nДля успешной сдачи необходимо набрать не менее 90% правильных ответов.\nВремя прохождения не ограничено.\nДоступно 3 попытки. После провала прогресс обучения сбрасывается — пройдите материалы заново.','Как работать с программой WB PVZ',9999,'');
/*!40000 ALTER TABLE `training_trainingmaterial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_trainingprogress`
--

DROP TABLE IF EXISTS `training_trainingprogress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_trainingprogress` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `completed_slides` int unsigned NOT NULL,
  `total_slides` int unsigned NOT NULL,
  `is_completed` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `material_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `training_trainingprogress_user_id_material_id_04173577_uniq` (`user_id`,`material_id`),
  KEY `training_trainingpro_material_id_435de941_fk_training_` (`material_id`),
  CONSTRAINT `training_trainingpro_material_id_435de941_fk_training_` FOREIGN KEY (`material_id`) REFERENCES `training_trainingmaterial` (`id`),
  CONSTRAINT `training_trainingprogress_user_id_e521f9de_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `training_trainingprogress_chk_1` CHECK ((`completed_slides` >= 0)),
  CONSTRAINT `training_trainingprogress_chk_2` CHECK ((`total_slides` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_trainingprogress`
--

LOCK TABLES `training_trainingprogress` WRITE;
/*!40000 ALTER TABLE `training_trainingprogress` DISABLE KEYS */;
INSERT INTO `training_trainingprogress` VALUES (98,2,17,0,'2026-04-13 05:58:32.281000',267,2),(99,1,17,0,'2026-05-07 01:15:20.816000',267,3),(100,1,17,0,'2026-05-07 05:15:36.798000',267,1);
/*!40000 ALTER TABLE `training_trainingprogress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_trainingquestion`
--

DROP TABLE IF EXISTS `training_trainingquestion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_trainingquestion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `text` longtext NOT NULL,
  `order` int unsigned NOT NULL,
  `test_id` bigint NOT NULL,
  `meta` json NOT NULL DEFAULT (_utf8mb4'{}'),
  `question_type` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `training_trainingque_test_id_92b011d4_fk_training_` (`test_id`),
  CONSTRAINT `training_trainingque_test_id_92b011d4_fk_training_` FOREIGN KEY (`test_id`) REFERENCES `training_trainingtest` (`id`),
  CONSTRAINT `training_trainingquestion_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_trainingquestion`
--

LOCK TABLES `training_trainingquestion` WRITE;
/*!40000 ALTER TABLE `training_trainingquestion` DISABLE KEYS */;
INSERT INTO `training_trainingquestion` VALUES (31,'Какой максимальный срок хранения товара в ПВЗ до автоматической отмены?',1,1,'{}','single'),(32,'Что нужно сделать при обнаружении брака на товаре ДО выдачи клиенту?',2,1,'{}','single'),(33,'Сколько открытых возвратных коробок может быть одновременно в ПВЗ?',3,1,'{}','single'),(34,'Какой минимальный срок для оспаривания удержания за подмену/брак/зависший ШК?',4,1,'{}','single'),(35,'Что делать, если клиент обнаружил брак ПОСЛЕ примерки?',5,1,'{}','single'),(36,'Какой вес маркетплейс-коробки является максимальным для приёмки?',6,1,'{}','single'),(37,'Что НЕ является браком для обуви?',7,1,'{}','single'),(38,'Какое требование обязательно для видео при оспаривании удержаний?',8,1,'{}','single'),(39,'Что делать с товаром, который попал в раздел «Утиль»?',9,1,'{}','single'),(40,'Сколько фото необходимо приложить при заполнении формы отметки о браке?',10,1,'{}','single'),(41,'Какие товары относятся к НЕвозвратным? (выберите все верные)',11,1,'{}','multiple'),(42,'Какие действия необходимо выполнить при приёмке товара? (выберите все верные)',12,1,'{}','multiple'),(43,'В каких случаях можно снять товар с выдачи? (выберите все верные)',13,1,'{}','multiple'),(44,'Какие типы брака можно оспорить? (выберите все верные)',14,1,'{}','multiple'),(45,'Что запрещено делать при работе с возвратными коробками? (выберите все верные)',15,1,'{}','multiple'),(46,'Какие документы можно принять для подтверждения возраста 18+? (выберите все верные)',16,1,'{}','multiple'),(47,'Какие действия выполняются при возврате товара из дома? (выберите все верные)',17,1,'{}','multiple'),(48,'Что входит в требования к видео для оспаривания? (выберите все верные)',18,1,'{}','multiple'),(49,'Порядок действий при приёмке товара в десктоп-приложении (расставьте шаги):',19,1,'{}','ordering'),(50,'Порядок действий при выдаче товара клиенту (расставьте шаги):',20,1,'{}','ordering'),(51,'Порядок заполнения формы отметки о браке (расставьте шаги):',21,1,'{}','ordering'),(52,'Порядок создания возвратной коробки для брака (расставьте шаги):',22,1,'{}','ordering'),(53,'Порядок действий при возврате товара курьером (расставьте шаги):',23,1,'{}','ordering'),(54,'Порядок оспаривания удержания за зависший ШК (расставьте шаги):',24,1,'{}','ordering'),(55,'Порядок приёмки маркетплейс-коробки (расставьте шаги):',25,1,'{}','ordering'),(56,'Порядок: Приёмка товара с повреждённым ШК. Указанная последовательность шагов верна?',26,1,'{\"statements\": [\"В разделе «Приёмка» выбрать «Принять товар без ШК»\", \"Ввести любые 4 последовательные цифры со стикера\", \"Отсканировать стикер коробки\", \"Отсканировать сгенерированный QR-код\", \"Положить товар в ячейку\"], \"correct_order\": [1, 3, 2, 4, 5], \"sequence_valid\": false}','order_judgment'),(57,'Порядок: Возврат товара из дома с одобренной заявкой на брак. Последовательность верна?',27,1,'{\"statements\": [\"Отсканировать QR-код из заявки в разделе «Возврат товара»\", \"Проверить соответствие товара фото в заявке\", \"Нажать «Принять возврат»\", \"Добавить товар в коробку «Для брака»\", \"Заполнить форму брака (если не заполнена)\"], \"correct_order\": [], \"sequence_valid\": true}','order_judgment'),(58,'Порядок: Смена ячейки с помощью сканера (десктоп). Последовательность верна?',28,1,'{\"statements\": [\"Отсканировать товар в разделе «Приёмка»\", \"Перейти на вкладку «Смена ячейки»\", \"Ввести номер новой ячейки вручную\", \"Отсканировать QR-код товара\", \"Подтвердить и физически переместить товары\"], \"correct_order\": [1, 2, 4, 3, 5], \"sequence_valid\": false}','order_judgment'),(59,'Порядок: Обнаружение подмены до примерки. Последовательность верна? (Учтите: пункт «сообщить клиенту, что только по заявке» в данном сценарии неверен.)',29,1,'{\"statements\": [\"Поставить отметку о браке в программе\", \"Сообщить клиенту, что товар можно вернуть только по заявке\", \"Оформить возврат в программе\", \"Положить товар в возвратную коробку\", \"Сохранить видеозапись работы с товаром\"], \"correct_order\": [1, 3, 4, 5], \"sequence_valid\": false}','order_judgment'),(60,'Порядок: Утилизация товара. Последовательность верна?',30,1,'{\"statements\": [\"Перейти в раздел «Возврат» → вкладка «Утиль»\", \"Поставить галочку напротив товара или ячейки\", \"Нажать «Утилизировать»\", \"Подтвердить действие\", \"Убрать символику WB с товара и утилизировать\"], \"correct_order\": [], \"sequence_valid\": true}','order_judgment');
/*!40000 ALTER TABLE `training_trainingquestion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_trainingslide`
--

DROP TABLE IF EXISTS `training_trainingslide`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_trainingslide` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `image_url` varchar(500) NOT NULL,
  `text` longtext NOT NULL,
  `order` int unsigned NOT NULL,
  `material_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `training_trainingsli_material_id_0a91493a_fk_training_` (`material_id`),
  CONSTRAINT `training_trainingsli_material_id_0a91493a_fk_training_` FOREIGN KEY (`material_id`) REFERENCES `training_trainingmaterial` (`id`),
  CONSTRAINT `training_trainingslide_chk_1` CHECK ((`order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_trainingslide`
--

LOCK TABLES `training_trainingslide` WRITE;
/*!40000 ALTER TABLE `training_trainingslide` DISABLE KEYS */;
/*!40000 ALTER TABLE `training_trainingslide` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_trainingtest`
--

DROP TABLE IF EXISTS `training_trainingtest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_trainingtest` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `material_id` bigint NOT NULL,
  `pass_threshold_percent` int unsigned NOT NULL,
  `require_all_other_materials_completed` tinyint(1) NOT NULL,
  `reset_all_training_progress_on_fail` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `material_id` (`material_id`),
  CONSTRAINT `training_trainingtes_material_id_6dfd3ae6_fk_training_` FOREIGN KEY (`material_id`) REFERENCES `training_trainingmaterial` (`id`),
  CONSTRAINT `training_trainingtest_chk_1` CHECK ((`pass_threshold_percent` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_trainingtest`
--

LOCK TABLES `training_trainingtest` WRITE;
/*!40000 ALTER TABLE `training_trainingtest` DISABLE KEYS */;
INSERT INTO `training_trainingtest` VALUES (1,'Итоговый тест стажёра ПВЗ',304,90,1,1);
/*!40000 ALTER TABLE `training_trainingtest` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-11  9:09:30
