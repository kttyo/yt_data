import MySQLdb
import credentials
from datetime import datetime, timedelta

conn = MySQLdb.connect(host=credentials.DB_HOST, db=credentials.DATABASE,user=credentials.DB_USER,passwd=credentials.DB_PASSWORD,charset='utf8mb4')
c = conn.cursor()


def date_minus_days(days):
    current_date = datetime.today()
    new_date = current_date - timedelta(days=days)
    return new_date.strftime('%Y%m%d')

days = 7
filter_date = date_minus_days(days)

args = (filter_date,)
c.callproc('yt_analysis_07', args)
conn.commit()

c.close()
conn.close()