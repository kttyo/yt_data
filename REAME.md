# YouTube Data Pipeline
This repository contains code for extracting data from the YouTube Data API, processing it, and storing it in a database. The code is designed to help users work with YouTube data in a more efficient and organized way. With this code, you can easily capture and store data from YouTube, and then use it for further analysis or other purposes.

## Assumptions
- Developed with: Python version 3.8, Django version 3.2

---
## Data pipeline from YouTube API to MySQL tables
![data process](https://github.com/kttyo/youtube_data/blob/5d56108b7c10d1badb9e0c8d3c49a05ebb406c74/images/buzzing_data_flow.jpg)
### Tools Used
- Python, MySQL, YouTube Data API, CaboCha

### Directory Structure

The project is organized into the following directories:

The `data/` directory contains the scripts for the project. It is organized into the following sub-directories:

- `sql/`: Contains the SQL scripts for both Data Definition Language (DDL) and Data Manipulation Language (DML). These scripts are used to create and manipulate the project's database tables.
- `scripts/`: Contains the Python scripts that capture data from the YouTube Data API and store it in the appropriate database tables. These scripts are used to populate the project's database with data from YouTube.



## Web Interface to display data captured and aggregated for analysis
- Visual representation of the data is also available on the web, at [https://buzzing.jppj.jp/](https://buzzing.jppj.jp/)
- However, this part is separately in another private repository for security reasons at the moment. 
![web ui](https://github.com/kttyo/youtube_data/blob/a6b850c1d85db7841c8aa23554f17841a4ae2159/images/buzzing_chart.jpg)
### Tools Used
- Django, Django REST Framework, Nginx, Gunicorn, Javascript
