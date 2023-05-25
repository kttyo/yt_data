CREATE TABLE `yt_pfm_cnl` (
  `channel_id` varchar(40) DEFAULT NULL,
  `subscriber_count` bigint DEFAULT NULL,
  `hidden_subscriber_count` varchar(1) DEFAULT NULL,
  `view_count` bigint DEFAULT NULL,
  `video_count` int DEFAULT NULL,
  `data_date` varchar(8) DEFAULT NULL,
  KEY `fk_channel_pfm` (`channel_id`),
  CONSTRAINT `fk_channel_pfm` FOREIGN KEY (`channel_id`) REFERENCES `yt_mst_cnl` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;