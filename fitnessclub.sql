CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255),
  `street_address` varchar(255),
  `state` varchar(255),
  `postal_code` varchar(255),
  `city` varchar(45) NOT NULL,
  `date_of_birth` date NOT NULL,
  `phone` varchar(255) NOT NULL UNIQUE,
  `email` varchar(255) NOT NULL UNIQUE,
  `user_name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE (`user_name`)
);

CREATE TABLE `role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `membership_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `membership_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `membership` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `membership_status_id` int NOT NULL,
  `membership_type_id` int NOT NULL,
  `period` varchar(255) DEFAULT "One Month",
  `amount` float DEFAULT 20,
  `date` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  `is_active` bit DEFAULT 0,
  PRIMARY KEY (`id`)
);

CREATE TABLE `payment_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `payment_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `payment_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `payment` (
  `member_id` int NOT NULL,
  `payment_type_id` int NOT NULL,
  `payment_category_id` int NOT NULL,
  `payment_status_id` int NOT NULL,
  `session_id` int NOT NULL,
  `description` varchar(255),
  `amount` float DEFAULT 0,
  `date` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`member_id`, `payment_type_id`, `date`)
);

CREATE TABLE `class` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  `date` date NOT NULL,
  `time_start` timestamp DEFAULT NULL,
  `time_end` timestamp DEFAULT NULL,
  `total_capacity` int DEFAULT 30,
  `available_capacity` int DEFAULT 30,
  PRIMARY KEY (`id`)
);

CREATE TABLE `booking_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `booking` (
  `class_id` int NOT NULL,
  `member_id` int NOT NULL,
  `booking_status_id` int NOT NULL,
  PRIMARY KEY (`class_id`, `member_id`)
);

CREATE TABLE `attendance_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `attendance` (
  `attendance_type_id` int NOT NULL,
  `member_id` int NOT NULL,
  `date` date NOT NULL,
  `time_start` timestamp,
  `time_end` timestamp,
  PRIMARY KEY (`attendance_type_id`, `member_id`, `date`)
);

CREATE TABLE `training` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  `trainer_id` int NOT NULL,
  `date` date NOT NULL,
  `amount` float DEFAULT 0,
  `time_start` timestamp,
  `time_end` timestamp,
  PRIMARY KEY (`id`)
);

CREATE TABLE `training_session` (
  `training_id` int NOT NULL,
  `member_id` int NOT NULL,
  PRIMARY KEY (`training_id`, `member_id`)
);

-- Notification Tables
CREATE TABLE `notification_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `recipient_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `schedule_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `notification_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notification_type_id` int NOT NULL,
  `recipient_type_id` int NOT NULL,
  `schedule_type_id` int NOT NULL,
  `notification_channel_id` int NOT NULL,
  `days` int DEFAULT 0,
  `subject` varchar(255) NOT NULL,
  `body` varchar(255) NOT NULL,
  `is_active` bit DEFAULT 0,
  PRIMARY KEY (`id`)
);

CREATE TABLE `notification_channel` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `site_notification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notification_id` int NOT NULL,
  `recipient_id` int NOT NULL,
  `is_read` bit DEFAULT 0,
  `date` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `notification_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `notification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notification_type_id` int NOT NULL,
  `recipient_id` int NOT NULL,
  `notification_status_id` int NOT NULL,
  `notification_channel_id` int NOT NULL,
  `schedule_date` date NOT NULL,
  `subject` varchar(255) NOT NULL,
  `body` varchar(255) NOT NULL,
  `created_date` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `notification_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notification_type` varchar(255) NOT NULL,
  `recipient_email` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  `notification_channel` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `date` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

ALTER TABLE `membership` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

ALTER TABLE `membership` ADD FOREIGN KEY (`membership_status_id`) REFERENCES `membership_status` (`id`);

ALTER TABLE `membership` ADD FOREIGN KEY (`membership_type_id`) REFERENCES `membership_type` (`id`);

ALTER TABLE `user_role` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

ALTER TABLE `user_role` ADD FOREIGN KEY (`role_id`) REFERENCES `role` (`id`);

ALTER TABLE `payment` ADD FOREIGN KEY (`member_id`) REFERENCES `user` (`id`);

ALTER TABLE `payment` ADD FOREIGN KEY (`payment_type_id`) REFERENCES `payment_type` (`id`);

ALTER TABLE `payment` ADD FOREIGN KEY (`payment_category_id`) REFERENCES `payment_category` (`id`);

ALTER TABLE `booking` ADD FOREIGN KEY (`class_id`) REFERENCES `class` (`Id`);

ALTER TABLE `booking` ADD FOREIGN KEY (`member_id`) REFERENCES `user_role` (`id`);

ALTER TABLE `booking` ADD FOREIGN KEY (`booking_status_id`) REFERENCES `booking_status` (`id`);

ALTER TABLE `training` ADD FOREIGN KEY (`trainer_id`) REFERENCES `user` (`id`);

ALTER TABLE `payment` ADD FOREIGN KEY (`payment_status_id`) REFERENCES `payment_status` (`id`);

ALTER TABLE `attendance` ADD FOREIGN KEY (`member_id`) REFERENCES `user_role` (`id`);

ALTER TABLE `attendance` ADD FOREIGN KEY (`attendance_type_id`) REFERENCES `attendance_type` (`id`);

ALTER TABLE `training_session` ADD FOREIGN KEY (`member_id`) REFERENCES `user_role` (`id`);

ALTER TABLE `training_session` ADD FOREIGN KEY (`training_id`) REFERENCES `training` (`id`);

ALTER TABLE `notification` ADD FOREIGN KEY (`notification_type_id`) REFERENCES `notification_type` (`id`);

ALTER TABLE `notification` ADD FOREIGN KEY (`recipient_id`) REFERENCES `user` (`id`);

ALTER TABLE `notification` ADD FOREIGN KEY (`notification_status_id`) REFERENCES `notification_status` (`id`);

ALTER TABLE `notification` ADD FOREIGN KEY (`notification_channel_id`) REFERENCES `notification_channel` (`id`);

ALTER TABLE `site_notification` ADD FOREIGN KEY (`notification_id`) REFERENCES `notification` (`id`);

ALTER TABLE `site_notification` ADD FOREIGN KEY (`recipient_id`) REFERENCES `user` (`id`);

ALTER TABLE `notification_config` ADD FOREIGN KEY (`notification_type_id`) REFERENCES `notification_type` (`id`);

ALTER TABLE `notification_config` ADD FOREIGN KEY (`recipient_type_id`) REFERENCES `recipient_type` (`id`);

ALTER TABLE `notification_config` ADD FOREIGN KEY (`schedule_type_id`) REFERENCES `schedule_type` (`id`);

ALTER TABLE `notification_config` ADD FOREIGN KEY (`notification_channel_id`) REFERENCES `notification_channel` (`id`);

INSERT INTO notification_status VALUES('1','Pending');
INSERT INTO notification_status VALUES('2','Sent');
INSERT INTO notification_status VALUES('3','Failed');

INSERT INTO notification_channel VALUES('1','Email');
INSERT INTO notification_channel VALUES('2','SMS');
INSERT INTO notification_channel VALUES('3','Site Notification');
INSERT INTO notification_channel VALUES('4','Microsoft Teams');

INSERT INTO schedule_type VALUES('1','On Event');
INSERT INTO schedule_type VALUES('2','Day Before');
INSERT INTO schedule_type VALUES('3','Day After');

INSERT INTO recipient_type VALUES('1','Admin/Manager');
INSERT INTO recipient_type VALUES('2','Trainer');
INSERT INTO recipient_type VALUES('3','Member');

INSERT INTO notification_type VALUES('1','Membership Reminder');
INSERT INTO notification_type VALUES('2','Membership Expiry');
INSERT INTO notification_type VALUES('3','Promotion');
INSERT INTO notification_type VALUES('4','News');
INSERT INTO notification_type VALUES('5','Class Enrolment');
INSERT INTO notification_type VALUES('6','Class Cancelation');

INSERT INTO notification_config VALUES('1','1','3','1','1','0','Membership Reminder','Your membership is about to expire',1);
INSERT INTO notification_config VALUES('2','2','3','1','1','0','Membership Expiry','Your membership has expired',1);
INSERT INTO notification_config VALUES('3','3','3','1','1','0','Promotion','New promotion is available',1);
INSERT INTO notification_config VALUES('4','4','3','1','1','0','News','New news is available',1);
INSERT INTO notification_config VALUES('5','5','3','1','1','0','Class Enrolment','You have enrolled to the new class',1);
INSERT INTO notification_config VALUES('6','6','3','1','1','0','Class Cancelation','Your booking has been cancelled.',1);

INSERT INTO role VALUES('1','Admin');
INSERT INTO role VALUES('2','Manager');
INSERT INTO role VALUES('3','Trainer');
INSERT INTO role VALUES('4','Member');

INSERT INTO membership_status VALUES('1', 'Active');
INSERT INTO membership_status VALUES('2', 'Inactive');

INSERT INTO membership_type VALUES('1', 'Regular');
INSERT INTO membership_type VALUES('2', 'Pro');
INSERT INTO membership_type VALUES('3', 'VIP');

INSERT INTO user VALUES ('1', 'Simon', 'Charles','23 Albert','Manuka','3340' ,'Auckland','1980-07-24', '0221234562','sc@gmail.com','scharles','1234', '2020-03-08');
INSERT INTO user VALUES ('2', 'Charlie', 'Venu','33 Prince','Manawatu','4410','Palmerston North','1988-07-24', '0211234562','svnu@yahoo.com','svenu','1234', '2020-03-08');
INSERT INTO user VALUES ('3', 'Sam', 'Ford', '453 Main','Central','3040','Wellington','1981-07-24', '0241234563','for@gmail.com','sford','1234', '2020-03-08');
INSERT INTO user VALUES ('4', 'Nathon', 'Pim', '23 Rangi','Main','4567', 'Christchurch','1990-07-24', '0261234564','ni@gmail.com','npim','1234', '2020-03-08');
INSERT INTO user VALUES ('5', 'John', 'Smith', '23 Rangi','Main','4567', 'Christchurch','1990-07-24', '0261234565','jo@gamil.com','jsmith','1234', '2020-03-08');
INSERT INTO user VALUES ('6', 'Jane', 'Doe', '23 Rangi','Main','4567', 'Christchurch','1990-07-24', '0261234566','jam@gmail.com','jdoe','1234', '2020-03-08');
INSERT INTO user VALUES ('7', 'Admin', 'Admin', '23 Rangi','Main','4567', 'Christchurch','1990-07-24', '0261234567','admin@gmail.com','admin','1234', '2020-03-08');
INSERT INTO user VALUES ('8', 'Luna', 'Xiang', '23 Rangi', 'Main', '4567', 'Christchurch', '1990-07-24', '0261234568', 'luni@gmail.com', 'luna', '1234', '2023-03-15');
INSERT INTO user VALUES ('9', 'Member', 'Member','23 Albert','Manuka','3340' ,'Auckland','1980-07-24', '022154562','member@gmail.com','member','1234', '2020-03-08');
INSERT INTO user VALUES ('10', 'Trainer', 'Trainer','23 Albert','Manuka','3340' ,'Auckland','1980-07-24', '022158562','trainer@gmail.com','trainer','1234', '2020-03-08');

INSERT INTO user_role  VALUES('1',1, 4, 1);
INSERT INTO user_role  VALUES('2', 2, 4, 1);
INSERT INTO user_role  VALUES('3', 3, 4, 1);
INSERT INTO user_role  VALUES('4', 4, 4, 1);
INSERT INTO user_role  VALUES('5', 5, 3, 1);
INSERT INTO user_role  VALUES('6', 6, 3, 1);
INSERT INTO user_role  VALUES('7', 7, 1, 1);
INSERT INTO user_role  VALUES ('8', 8, 1, 1);
INSERT INTO user_role  VALUES('9', 9, 4, 1);
INSERT INTO user_role  VALUES('10', 10, 3, 1);

INSERT INTO class VALUES(1,'Yoga', 'Yoga is a group of physical, mental, and spiritual practices or disciplines which originated in ancient India.','2023-05-01',TIMESTAMP("2023-05-01",  "10:00:00"), TIMESTAMP("2023-05-01",  "11:00:00"), 30, 30);
INSERT INTO class VALUES(2,'Zumba', 'Zumba is a fitness program that combines Latin and international music with dance moves.','2023-05-02',TIMESTAMP("2023-05-02",  "10:00:00"), TIMESTAMP("2023-05-02",  "11:00:00"), 30, 30);
INSERT INTO class VALUES(3,'Pilates', 'Pilates is a physical fitness system developed in the early 20th century by Joseph Pilates, after whom it was named.','2023-05-03',TIMESTAMP("2023-05-03",  "10:00:00"), TIMESTAMP("2023-05-03",  "11:00:00"), 30, 30);
INSERT INTO class VALUES(4,'Aerobics', 'Aerobics is a form of physical exercise that combines rhythmic aerobic exercise.','2023-05-04',TIMESTAMP("2023-05-04",  "10:00:00"), TIMESTAMP("2023-05-04",  "11:00:00"), 30, 30);

INSERT INTO membership (id,user_id, membership_status_id, membership_type_id ) VALUES(1, 1, 1, 1);
INSERT INTO membership (id,user_id, membership_status_id, membership_type_id ) VALUES(2, 2, 1, 1);
INSERT INTO membership (id,user_id, membership_status_id, membership_type_id ) VALUES(3, 3, 1, 1);
INSERT INTO membership (id,user_id, membership_status_id, membership_type_id ) VALUES(4, 4, 1, 2);
INSERT INTO membership (id,user_id, membership_status_id, membership_type_id ) VALUES(5, 9, 1, 3);

INSERT INTO training  VALUES(1,'Yoga','', 5, '2023-04-01', 60, TIMESTAMP("2023-04-01",  "10:00:00"), TIMESTAMP("2023-04-01",  "11:00:00"));
INSERT INTO training  VALUES(2,'Zumba','', 5, '2023-04-01', 60, TIMESTAMP("2023-04-01",  "11:00:00"), TIMESTAMP("2023-04-01",  "12:00:00"));
INSERT INTO training  VALUES(3,'Pilates','', 5, '2023-04-01', 60, TIMESTAMP("2023-04-01",  "12:00:00"), TIMESTAMP("2023-04-01",  "13:00:00"));
INSERT INTO training  VALUES(4,'BODY TRANSFORMATION','', 6, '2023-04-03', 60, TIMESTAMP("2023-04-03",  "13:00:00"), TIMESTAMP("2023-04-03",  "14:00:00"));
INSERT INTO training  VALUES(5,'BODYBUILDER','', 6, '2023-04-03', 60, TIMESTAMP("2023-04-03",  "11:00:00"), TIMESTAMP("2023-04-03",  "12:00:00"));

INSERT INTO payment_type VALUES(1, 'Cash', '');
INSERT INTO payment_type VALUES(2, 'Credit Card', '');
INSERT INTO payment_type VALUES(3, 'Debit Card', '');

INSERT INTO payment_category VALUES(1, 'Membership', '');
INSERT INTO payment_category VALUES(2, 'Training', '');

INSERT INTO booking_status VALUES(1, 'Pending', '');
INSERT INTO booking_status VALUES(2, 'Confirmed', '');
INSERT INTO booking_status VALUES(3, 'Cancelled', '');

INSERT INTO payment_status VALUES(1, 'Pending', '');
INSERT INTO payment_status VALUES(2, 'Paid', '');
INSERT INTO payment_status VALUES(3, 'Cancelled', '');
INSERT INTO payment_status VALUES(4, 'Refunded', '');


INSERT INTO attendance_type VALUES (1, 'Attend', NULL);

INSERT INTO attendance VALUES (1, 1, '2023-03-15', '2023-03-15 10:00:00', '2023-03-21 11:00:00');
INSERT INTO attendance VALUES (1, 2, '2023-03-15', '2023-03-15 10:00:00', '2023-03-21 11:00:00');

/*
-- Drop all tables
DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS booking_status;
DROP TABLE IF EXISTS class;
DROP TABLE IF EXISTS membership;
DROP TABLE IF EXISTS membership_status;
DROP TABLE IF EXISTS membership_type;
DROP TABLE IF EXISTS notification_config;
DROP TABLE IF EXISTS site_notification;
DROP TABLE IF EXISTS notification;
DROP TABLE IF EXISTS notification_type;
DROP TABLE IF EXISTS recipient_type;
DROP TABLE IF EXISTS schedule_type;
DROP TABLE IF EXISTS notification_channel;
DROP TABLE IF EXISTS notification_status;
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS payment_type;
DROP TABLE IF EXISTS payment_category;
DROP TABLE IF EXISTS payment_status;
DROP TABLE IF EXISTS training_session;
DROP TABLE IF EXISTS training;
DROP TABLE IF ExISTS attendance;
DROP TABLE IF EXISTS attendance_type;
DROP TABLE IF EXISTS user_role;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS role;
DROP TABLE IF EXISTS notification_log;
*/