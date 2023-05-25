from credentials import VENV_PATH, VENV_PYTHON, SCRIPT_PATH, DB_HOST, DATABASE, DB_USER, DB_PASSWORD
import datetime
import MySQLdb
import subprocess
import logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


conn = MySQLdb.connect(host=DB_HOST, db=DATABASE,user=DB_USER,passwd=DB_PASSWORD,charset='utf8mb4')
c = conn.cursor()


# Activate the virtual environment
result = subprocess.run(
    ['/bin/bash', '-c', f"source {VENV_PATH}"], 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE, 
    # shell=True, 
    check=True
    )

# If the virtual environment was activated successfully, run script1.py
try:
    if result.returncode == 0:
        logging.info('venv successfully activated')
        result1 = subprocess.run([VENV_PYTHON, SCRIPT_PATH+"mst_cnl_trending.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logging.error('Error occurred in venv activation')
        exit()

    if result1.returncode == 0:
        logging.info('mst_cnl_trending.py successfully completed')
        result2 = subprocess.run([VENV_PYTHON, SCRIPT_PATH+"mst_vid.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logging.error('Error occurred in mst_cnl_trending.py processing')
        exit()

    if result2.returncode == 0:
        logging.info('mst_vid.py successfully completed')
        result3 = subprocess.run([VENV_PYTHON, SCRIPT_PATH+"pfm_cnl.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logging.error('Error occurred in mst_vid.py processing')
        exit()

    if result3.returncode == 0:
        logging.info('pfm_cnl.py successfully completed')
        result4 = subprocess.run([VENV_PYTHON, SCRIPT_PATH+"pfm_vid.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        logging.error('Error occurred in pfm_cnl.py data processing')
        exit()
    
    if result4.returncode == 0:
        logging.info('pfm_vid.py successfully completed')
    else:
        logging.error('Error occurred in pfm_vid.py data processing')
        exit()
        
    try:
        # Define the argument value
        today = datetime.datetime.now()
        filter_date = today - datetime.timedelta(7) # goes back 7 days
        filter_date_str = filter_date.strftime('%Y%m%d')
        # Execute the stored procedure
        c.callproc('yt_analysis_07',[filter_date_str])

        # Retrieve the result set, if any
        result = c.fetchall()
        for row in result:
            print(row)  # Handle the result as needed

    except MySQLdb.Error as error:
        print(f"Error while executing stored procedure: {error}")
    
    c.close()
    conn.close()

except Exception as e:
    logging.error(e)
subprocess.run(["deactivate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)