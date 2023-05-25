CREATE DATABASE IF NOT EXISTS buzzing;
USE buzzing;

CREATE TABLE IF NOT EXISTS `yt_mst_cnl` (
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

CREATE TABLE IF NOT EXISTS `yt_mst_vid` (
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

CREATE TABLE IF NOT EXISTS `yt_pfm_cnl` (
  `channel_id` varchar(40) DEFAULT NULL,
  `subscriber_count` bigint DEFAULT NULL,
  `hidden_subscriber_count` varchar(1) DEFAULT NULL,
  `view_count` bigint DEFAULT NULL,
  `video_count` int DEFAULT NULL,
  `data_date` varchar(8) DEFAULT NULL,
  KEY `fk_channel_pfm` (`channel_id`),
  CONSTRAINT `fk_channel_pfm` FOREIGN KEY (`channel_id`) REFERENCES `yt_mst_cnl` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `yt_pfm_vid` (
  `video_id` varchar(20) DEFAULT NULL,
  `view_count` bigint DEFAULT NULL,
  `like_count` int DEFAULT NULL,
  `dislike_count` int DEFAULT NULL,
  `favorite_count` int DEFAULT NULL,
  `comment_count` int DEFAULT NULL,
  `most_used_words` text,
  `data_date` varchar(8) DEFAULT NULL,
  KEY `fk_video_pfm` (`video_id`),
  CONSTRAINT `fk_video_pfm` FOREIGN KEY (`video_id`) REFERENCES `yt_mst_vid` (`video_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `yt_analysis_07` (
  `channel_id` varchar(40) DEFAULT NULL,
  `channel_name` tinytext,
  `view_count` bigint DEFAULT NULL,
  `like_count` int DEFAULT NULL,
  `dislike_count` int DEFAULT NULL,
  `favorite_count` int DEFAULT NULL,
  `comment_count` int DEFAULT NULL,
  `video_count` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP PROCEDURE IF EXISTS `buzzing`.`yt_analysis_07`;
DELIMITER //
CREATE PROCEDURE `buzzing`.`yt_analysis_07`(IN published_after VARCHAR(8))
BEGIN
    -- truncate the yt_analysis_07 table
    TRUNCATE TABLE yt_analysis_07;

    -- insert data into the yt_analysis_07 table
    INSERT INTO yt_analysis_07
    SELECT 
        channel_id,
        channel_name,
        view_count,
        like_count,
        dislike_count,
        favorite_count,
        comment_count,
        video_count
    FROM (
        SELECT 
            B.channel_id AS channel_id, 
            MAX(C.channel_name) AS channel_name, 
            SUM(A.view_count) AS view_count, 
            SUM(A.like_count) AS like_count, 
            SUM(A.dislike_count) AS dislike_count, 
            SUM(A.favorite_count) AS favorite_count, 
            SUM(A.comment_count) AS comment_count, 
            COUNT(*) AS video_count
        FROM yt_pfm_vid A
        LEFT JOIN yt_mst_vid B ON A.video_id = B.video_id
        LEFT JOIN (
            SELECT channel_id, MAX(channel_name) AS channel_name FROM yt_mst_cnl GROUP BY channel_id
        ) C ON B.channel_id = C.channel_id
        WHERE B.published_at >= @published_after
        GROUP BY channel_id
    ) T1
    ORDER BY view_count DESC;
    COMMIT;
END //
DELIMITER ;
