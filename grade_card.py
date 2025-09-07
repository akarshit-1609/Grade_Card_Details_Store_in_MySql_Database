import tkinter as tk
import requests
import re
import mysql.connector
import subprocess
import os

from tkinter import ttk
from termcolor import colored
from xlsxwriter import Workbook

rootuser = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306"
)

mysql_exe = "mysql"
mysql_login_file = "--defaults-file=mylogin.cnf"
mysql_args = ["--table", "-D", "grade_cards", "-e"]
mysql_default_command = [mysql_exe, mysql_login_file, *mysql_args]

window = tk.Tk()
wt = 320
ht = 320
window.geometry(f"{wt+50}x{ht}+800+50")
window.title("Grade Card Details")
window.configure(bg="white")

heading_color = "green"
table_color = "light_cyan"

frame1 = tk.Frame(window, background="white", width=wt/2)
frame1.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
frame1.grid_columnconfigure(0, weight=1)

frame2 = tk.Frame(window, background="white", width=wt/2)
frame2.pack(side=tk.RIGHT, fill="both", expand=True, padx=10)
frame2.grid_columnconfigure(0, weight=1)

enrolnment = tk.StringVar()
programme = tk.StringVar()
all_enrolnments = [2351604407]
all_names = ["Akarshit Kumar"]
current_name = tk.StringVar(value="--Select--")
current_enrolnment = all_enrolnments[0]

def all_names_fetch():
    global all_names, dropdown_menu
    database_name = "grade_cards"
    query = rootuser.cursor()
    query.execute("show databases like '" + database_name + "'")
    t = query.fetchall()
    if (len(t) != 1):
        query.execute("create database " + database_name)
    query.execute("use " + database_name)

    query.execute("select * from all_recorded_data")
    t = query.fetchall()
    all_names.clear()
    all_enrolnments.clear()
    for i in t:
        enrolnment_number = i[0]
        name = i[1]
        all_enrolnments.append(enrolnment_number)
        all_names.append(name)
    dropdown_menu["values"] = all_names
    

def fetch(e_no, p_cd):
    fetch_remark.config(text="")
    enrolment_number = e_no
    programme_code = p_cd
    r = requests.get("https://gradecard.ignou.ac.in/gradecard/view_gradecard.aspx?eno=" + str(enrolment_number) + "&prog=" + programme_code + "&type=1")

    content = r.content.decode("utf-8")
    content = content.replace("\r", "")
    content = content.replace("\t", "")
    content = content.replace("\n", "")

    name = re.findall('Name:.*?<b>(.*?)</b>.*?Programme Code:', content)[0]

    try:
        table = re.findall('<table cellspacing="0" cellpadding="8" align="Center" border="0" id="ctl00_ContentPlaceHolder1_gvDetail" width="100%">(.*?)</table>', content)[0]
    except:
        fetch_remark.config(text="Error:- No Record Found", fg="red")
        return None

    database_name = "grade_cards"
    query = rootuser.cursor()
    query.execute("show databases like '" + database_name + "'")
    t = query.fetchall()
    if (len(t) != 1):
        query.execute("create database " + database_name)
    query.execute("use " + database_name)

    tr = re.findall('<tr align="center" valign=".*?" bgcolor=".*?">(.*?)</tr>', table)

    th = re.findall('<th scope="col"><font face="Arial" color="White" size="4"><b>(.*?)</b></font></th>', tr[0])

    table_name = (name.replace(" ", "_") + "_" + str(enrolment_number)).lower()

    query.execute("show tables like 'all_recorded_data'")
    t = query.fetchall()
    if (len(t) != 1):
        q = "create table all_recorded_data(enrolnment_number varchar(20) primary key, name char(50), course varchar(20), table_name varchar(80))"
        query.execute(q)

    query.execute("select * from all_recorded_data where enrolnment_number = '"+ enrolment_number +"'")
    t = query.fetchall()
    if (len(t) != 1):
        query.execute("insert into all_recorded_data value('"+ enrolment_number +"', '"+ name.title() +"', '"+ programme_code +"', '"+ table_name +"')")

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
    fetch_remark.config(text="Done", fg="green")
    all_names_fetch()

def update_current_enrolnment():
    global current_enrolnment
    name = current_name.get()
    name_index = dropdown_menu.current()
    if (name != "--Select--"):
        current_enrolnment = all_enrolnments[name_index]

def update_marks():
    update_current_enrolnment()
    name = current_name.get()
    if (name != "--Select--"):
        query = rootuser.cursor()
        query.execute("select * from all_recorded_data where enrolnment_number = '"+ current_enrolnment +"'")
        t = query.fetchall()
        course = t[0][2]
        fetch(current_enrolnment, course)

def show_marks():
    update_current_enrolnment()
    name = current_name.get()
    if (name != "--Select--"):
        query = rootuser.cursor()
        query.execute("select * from all_recorded_data where enrolnment_number = '"+ current_enrolnment +"'")
        t = query.fetchall()
        course = t[0][2]
        table_name = t[0][3]

        q = "select count(*) from " + table_name
        query.execute(q)
        t = query.fetchall()
        count = t[0][0]

        q = "select * from " + table_name
        output = subprocess.check_output([*mysql_default_command, q], universal_newlines=True)
        print(colored(f"Enrolnment No: {current_enrolnment}\tName: {name}\tCourse: {course}\tTotal Rows: {count}",heading_color,attrs=["bold"]))
        print(colored(output, table_color))

def show_marks_c():
    update_current_enrolnment()
    name = current_name.get()
    if (name != "--Select--"):
        query = rootuser.cursor()
        query.execute("select * from all_recorded_data where enrolnment_number = '"+ current_enrolnment +"'")
        t = query.fetchall()
        course = t[0][2]
        table_name = t[0][3]
        
        q = "select count(*) from " + table_name + " where STATUS='COMPLETED'"
        query.execute(q)
        t = query.fetchall()
        count = t[0][0]

        q = "select * from " + table_name + " where STATUS='COMPLETED'"
        output = subprocess.check_output([*mysql_default_command, q], universal_newlines=True)
        print(colored(f"Enrolnment No: {current_enrolnment}\tName: {name}\tCourse: {course}\tTotal Rows: {count}",heading_color,attrs=["bold"]))
        print(colored(output, table_color))

def show_marks_nc():
    update_current_enrolnment()
    name = current_name.get()
    if (name != "--Select--"):
        query = rootuser.cursor()
        query.execute("select * from all_recorded_data where enrolnment_number = '"+ current_enrolnment +"'")
        t = query.fetchall()
        course = t[0][2]
        table_name = t[0][3]
        
        q = "select count(*) from " + table_name + " where STATUS='NOT COMPLETED'"
        query.execute(q)
        t = query.fetchall()
        count = t[0][0]

        q = "select * from " + table_name + " where STATUS='NOT COMPLETED'"
        output = subprocess.check_output([*mysql_default_command, q], universal_newlines=True)
        print(colored(f"Enrolnment No: {current_enrolnment}\tName: {name}\tCourse: {course}\tTotal Rows: {count}",heading_color,attrs=["bold"]))
        print(colored(output, table_color))

def export_into_excel():
    update_current_enrolnment()
    name = current_name.get()
    if (name != "--Select--"):
        query = rootuser.cursor()
        query.execute("select * from all_recorded_data where enrolnment_number = '"+ current_enrolnment +"'")
        t = query.fetchall()
        course = t[0][2]
        table_name = t[0][3]
        excel_file_name = os.environ["USERPROFILE"] + "\\Desktop\\" + table_name + ".xlsx"
        excel_file = Workbook(excel_file_name)
        excel_write = excel_file.add_worksheet()

        heading_format = excel_file.add_format({
            "bold": True,
            "border": 1,
            "align": "center",
            "valign": "center",
            "bg_color": "#0000dd",
            "font_color": "#ffffff"
        })
        merge_format = excel_file.add_format({
            "bold": True,
            "border": 1,
            "align": "center",
            "valign": "center",
            "font_size": 15,
            "bg_color": "#ffff00",
            "font_color": "#000000"
        })

        user_format = excel_file.add_format({
            "border": 1,
            "align": "center",
            "valign": "center",
            "bg_color": "#b8f3fd",
            "font_color": "#000000"
        })

        marks_format_dict = {
            "border": 1,
            "font_color": "#000000"
        }

        excel_write.write(1, 1, "Name", heading_format)
        excel_write.write(1, 2, "Enrolnment", heading_format)
        excel_write.write(1, 3, "Course", heading_format)
        excel_write.write(2, 1, name, user_format)
        excel_write.write(2, 2, current_enrolnment, user_format)
        excel_write.write(2, 3, course, user_format)

        excel_write.set_column(1, 3, 15)
        excel_write.set_column(7, 7, 21)
        excel_write.set_column(8, 8, 25)
        excel_write.set_column(9, 9, 16)

        excel_write.set_row(4, 15)

        q = "describe " + table_name
        query.execute(q)
        table_description = query.fetchall()
        for i, heading in enumerate(table_description):
            excel_write.write(5, i+1, heading[0].replace("_", " "), heading_format)

        q = "select * from " + table_name
        query.execute(q)
        table_data = query.fetchall()

        excel_write.merge_range(4, 1, 4, len(table_data[0])+0, "Grade Card", merge_format)

        row_design = True
        for i, row in enumerate(table_data):
            new_design = marks_format_dict
            if row_design:
                if (row[-1] == "COMPLETED"):
                    new_design["bg_color"] = "#99ff99"
                elif (row[-1] == "NOT COMPLETED"):
                    new_design["bg_color"] = "#ff9999"
                row_design = False
            else:
                if (row[-1] == "COMPLETED"):
                    new_design["bg_color"] = "#ddffdd"
                elif (row[-1] == "NOT COMPLETED"):
                    new_design["bg_color"] = "#ffdddd"
                row_design = True
            marks_format = excel_file.add_format(new_design)
            for j, data in enumerate(row):
                if (data == "-"):
                    data = ""
                elif (data.isnumeric()):
                    data = int(data)
                excel_write.write(i+6, j+1, data, marks_format)
        excel_file.close()
        print(colored(f"Export File :- {excel_file_name} ", "light_green"))


enrolnment_input = tk.Entry(frame1, textvariable=enrolnment)
enrolnment_input.grid(row=0, column=0, pady=5)

programme_input = tk.Entry(frame1, textvariable=programme)
programme_input.insert(0, "BAM")
programme_input.grid(row=1, column=0, pady=5)

tk.Button(frame1, text="Fetch", background="green", fg="white", command=lambda: fetch(enrolnment.get(), programme.get())).grid(row=2, column=0, pady=5)

fetch_remark = tk.Label(frame1, text="", bg="white", fg="green")
fetch_remark.grid(row=3, column=0, pady=5)

dropdown_menu = ttk.Combobox(frame2, textvariable=current_name, values=all_names, state="readonly")
dropdown_menu.grid(row=0, column=0, pady=5)

tk.Button(frame2, text="Update", width=int(wt/2), background="green", fg="white", command=update_marks).grid(row=1, column=0, pady=5)
tk.Button(frame2, text="Show all marks", width=int(wt/2), background="yellow", command=show_marks).grid(row=2, column=0, pady=5)
tk.Button(frame2, text="Show only completed", width=int(wt/2), background="yellow", command=show_marks_c).grid(row=3, column=0, pady=5)
tk.Button(frame2, text="show only not completed", width=int(wt/2), background="yellow", command=show_marks_nc).grid(row=4, column=0, pady=5)
tk.Button(frame2, text="Export into excel", width=int(wt/2), background="#ff7700", fg="white", command=export_into_excel).grid(row=5, column=0, pady=5)

all_names_fetch()

window.mainloop()

rootuser.close()