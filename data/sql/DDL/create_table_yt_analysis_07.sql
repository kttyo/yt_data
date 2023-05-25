CREATE TABLE `yt_analysis_07` (
  `channel_id` varchar(40) DEFAULT NULL,
  `channel_name` tinytext,
  `view_count` bigint DEFAULT NULL,
  `like_count` int DEFAULT NULL,
  `dislike_count` int DEFAULT NULL,
  `favorite_count` int DEFAULT NULL,
  `comment_count` int DEFAULT NULL,
  `video_count` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;