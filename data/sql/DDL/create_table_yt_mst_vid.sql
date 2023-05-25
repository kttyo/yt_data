CREATE TABLE `yt_mst_vid` (
  `video_id` varchar(20) NOT NULL,
  `video_name` text,
  `description` text,
  `thumbnail` text,
  `channel_id` varchar(40) DEFAULT NULL,
  `published_at` varchar(8) DEFAULT NULL,
  `data_update_date` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`video_id`),
  KEY `fk_channel` (`channel_id`),
  KEY `idx_published_at` (`published_at`),
  CONSTRAINT `fk_channel` FOREIGN KEY (`channel_id`) REFERENCES `yt_mst_cnl` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;