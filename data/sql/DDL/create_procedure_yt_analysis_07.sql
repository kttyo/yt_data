CREATE DEFINER=`dbadmin`@`localhost` PROCEDURE `buzzing`.`yt_analysis_07`(published_after VARCHAR(8))
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
        WHERE B.published_at >= published_after
        GROUP BY channel_id
    ) T1
    ORDER BY view_count DESC;
    COMMIT;
END