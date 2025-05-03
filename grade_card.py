import requests
import re
import mysql.connector

rootuser = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306"
)

enrolment_number = 0000000000
programme_code = "BAM"

r = requests.get("https://gradecard.ignou.ac.in/gradecard/view_gradecard.aspx?eno=" + str(enrolment_number) + "&prog=" + programme_code + "&type=1")

content = r.content.decode("utf-8")
content = content.replace("\r", "")
content = content.replace("\t", "")
content = content.replace("\n", "")

try:
    name = re.findall('Name:.*?<b>(.*?)</b>.*?Programme Code:', content)[0]
    table = re.findall('<table cellspacing="0" cellpadding="8" align="Center" border="0" id="ctl00_ContentPlaceHolder1_gvDetail" width="100%">(.*?)</table>', content)[0]
except:
    print("Error:- No Record Found")
    rootuser.close()
    exit(0)

database_name = "grade_cards"
query = rootuser.cursor()
query.execute("show databases like '" + database_name + "'")
t = query.fetchall()
if (len(t) != 1):
    query.execute("create database " + database_name)
query.execute("use " + database_name)

tr = re.findall('<tr align="center" valign=".*?" bgcolor=".*?">(.*?)</tr>', table)

th = re.findall('<th scope="col"><font face="Arial" color="White" size="4"><b>(.*?)</b></font></th>', tr[0])

table_name = name.replace(" ", "_") + "_" + str(enrolment_number)

query.execute("show tables like '" + table_name + "'")
t = query.fetchall()

if (len(t) != 1):
    q = "create table " + table_name + "("
    for i in range(len(th)):
        if (th[i] == th[-1]):
            q += th[i].replace(" ", "_") + " varchar(50))"
        elif (th[i].lower() == "course"):
            q += th[i].replace(" ", "_") + " varchar(50) primary key, "
        else:
            q += th[i].replace(" ", "_") + " varchar(50), "
    query.execute(q)
else:
    query.execute("truncate table " + table_name + "")

tr.pop(0)

insert = "insert into " + table_name + " value ("
for i in tr:
    td = re.findall('<td><font face="Arial" color=".*?" size="4">(.*?)</font></td>', i)
    for j in range(len(td)-1):
        insert += "'" + td[j] + "', "
    insert += "'" + td[len(td)-1] + "')"
    query.execute(insert)
    insert = "insert into " + table_name + " value ("


rootuser.commit()

rootuser.close()