truncate table yt_analysis_vid
;
insert into yt_analysis_vid
select 
A.video_id,
B.video_name,
B.channel_id,
A.view_count,
A.like_count,
A.dislike_count,
A.favorite_count,
A.comment_count,
A.most_used_words,
B.published_at
from yt_pfm_vid A
left join yt_mst_vid B on A.video_id = B.video_id
;