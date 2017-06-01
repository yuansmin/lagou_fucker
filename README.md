### 数据库
1. 使用SQLite3

create table company(
id integer primary key, name text, logo text,
url text,
brief text, comment_count integer,
jobs_count integer, resume_rate integer,
city_id integer, last_login_text text,
last_login text,
process_ text, process integer,
employee_count integer,
products text,
description text,
interview_rate integer,
interview_count integer,
raw_data text
);

create table company_type(
id integer primary key,
company_id integer,
type_id integer
);

create table type(
id integer primary key,
name text
);

create table jobs(
id integer primary key,
salay text,
city_id integer,
experince text,
degree text,
pub_date text,
advantage text,
description text,
publisher_id integer
);

create table company_tag(
id integer primary key,
company_id integer,
tag_id integer
);

create table tags(
id integer primary key,
name text
);

create table humanresource(
id integer primary key,
name text
);

create table city(
id integer primary key,
name text
);

