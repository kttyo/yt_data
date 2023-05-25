CREATE TABLE `yt_mst_cnl` (
  `channel_id` varchar(40) NOT NULL,
  `channel_name` tinytext,
  `description` text,
  `thumbnail` text,
  `uploads_list` varchar(40) DEFAULT NULL,
  `published_at` date DEFAULT NULL,
  `data_update_date` date DEFAULT NULL,
  PRIMARY KEY (`channel_id`),
  KEY `idx_published_at` (`published_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;