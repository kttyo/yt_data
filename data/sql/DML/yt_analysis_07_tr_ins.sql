truncate table yt_analysis_07
;
insert into yt_analysis_07
select 
channel_id,
channel_name,
view_count,
like_count,
dislike_count,
favorite_count,
comment_count,
video_count
from (
select 
B.channel_id as channel_id, 
max(C.channel_name) as channel_name, 
sum(A.view_count) as view_count, 
sum(A.like_count) as like_count, 
sum(A.dislike_count) as dislike_count, 
sum(A.favorite_count) as favorite_count, 
sum(A.comment_count) as comment_count, 
count(*) as video_count
from yt_pfm_vid A
left join yt_mst_vid B on A.video_id = B.video_id
left join (select channel_id, max(channel_name) as channel_name from yt_mst_cnl group by channel_id) C on B.channel_id = C.channel_id
where B.published_at >= '20210601'
group by channel_id
) T1
order by view_count desc
;