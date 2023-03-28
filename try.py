# import pymysql,base64
# from pymysql.converters import escape_string
#
# conn_obj = pymysql.connect(
#     host='127.0.0.1',  # MySQL服务端的IP地址
#     port=3306,  # MySQL默认PORT地址(端口号)
#     user='root',  # 用户名
#     password='nzh278799',  # 密码,也可以简写为passwd
#     database='project',  # 库名称,也可以简写为db
#     charset='utf8'  # 字符编码
# )
#
# with open("static/index7/images/Image-28678EF9-664A-4CB7-A50D-975283680C83.png", 'rb') as f:
#     img = f.read()
# img = base64.b64encode(img)
#
# # print(img)
# # print(img)
# cursor = conn_obj.cursor()
# # sql = """INSERT INTO users ('ID', 'name', 'Gender', 'date_of_birth', 'nationality', 'Registration_Number',
# # 'major', 'degree', 'GPA', 'DateOfAttendanceAndGraduation', 'DateOfGraduation', 'image')
# # VALUES ('DQ12345678', 'Heng', 'Male', '2021-01-01', 'UAS', '121321212122', 'market', '1111',
# # '1111', '2020-01-01', '2022-01-01', '{}');""".format(escape_string(img))
#
# # sql = """INSERT INTO `project`.`users`
# # (`ID`, `name`, `Gender`, `date_of_birth`, `nationality`,
# # `Registration_Number`, `major`, `degree`, `GPA`,
# #  `DateOfAttendanceAndGraduation`, `DateOfGraduation`, `image`)
# #  VALUES ('DQ12345678', 'Heng', 'Male', '2021-01-01', 'UAS',
# #  '121321212122', 'market', '1111', '1111', '2020-01-01', '2022-01-01', %s);"""
#
# sql = """INSERT INTO `project`.`users` (`ID`, `name`, `Gender`, `date_of_birth`, `nationality`, `Registration_Number`, `major`, `degree`, `GPA`, `DateOfAttendanceAndGraduation`, `DateOfGraduation`, `image`) VALUES ('EH19730319', 'Ming Chen', 'Male', '1973-03-19', 'China', '10121534002', 'Public Administration', 'Master of Public health', '3.8', '2019-09-01', '2021-01-01', %s);"""
#
# # args = escape_string(img)
# cursor.execute(sql, img)
# conn_obj.commit()

# sql = """select * from users WHERE users.ID = """ + """'EH19730319';"""
# cursor.execute(sql)

# import pandas as pd
# data = pd.read_excel('static/tmp/AQ12345678.xlsx')
# print(data.loc[0:0].values[0][0])  # 姓名
# print(str((data.loc[0:0].values[0][1]))[0:10])  # 生日
# print(data.loc[0:0].values[0][2])   # ID
# print(data.loc[0:0].values[0][3])   # 性别
# print(data.loc[0:0].values[0][4])   # 国籍
# print(data.loc[0:0].values[0][5])   # Registration_Number
# print(data.loc[0:0].values[0][6])   # degree
# print(data.loc[0:0].values[0][7])   # DateOfAttendance
# print(data.loc[0:0].values[0][8])   # DateOfGraduation
# print(data.loc[0:0].values[0][9])   # Major
# print(data.loc[0:0].values[0][10])   # GPA
# print(data.loc[0:0].values[0][11])   # img
# import os
#
# # 解压目录
# unzip_path = "static/tmp/unzip"
# if not os.path.exists(unzip_path):
#     os.mkdir(unzip_path)
# with ZipFile("static/tmp/AQ12345678.xlsx") as f:
#     for file in f.namelist():
#         # 解压图片部分的文件
#         if file.startswith("xl/media"):
#             f.extract(file, path=unzip_path)
import config, threading
import json
import pymysql
from flask import Flask, render_template, request, Response, make_response
from flask_cors import CORS, cross_origin
from dbutils.pooled_db import PooledDB
from dbutils.persistent_db import PersistentDB

app = Flask(__name__, static_folder='', static_url_path='', template_folder='')
app.config.from_object(config)


class MysqlHelper(object):
    conn = None

    def __init__(self, host, username, password, db=None, charset='utf8', port=3306):
        self.__pool = PooledDB(creator=pymysql,
                               mincached=10,
                               maxcached=0,
                               maxshared=20,
                               maxconnections=200,
                               maxusage=20,
                               blocking=True,
                               user=username,
                               passwd=password,
                               db=db,
                               host=host,
                               port=port)

    def connect(self):
        conn = self.__pool.connection()
        cursor = conn.cursor()
        # print("连接成功")
        return conn, cursor

    def close(self):
        conn, cursor = self.connect()
        cursor.close()
        conn.close()

    def get_one(self, sql, params=()):
        result = None
        title = []
        try:
            conn, cursor = self.connect()
            cursor.execute(sql, params)
            result = cursor.fetchone()
            des = cursor.description
            title = [item[0] for item in des]
            self.close()
        except Exception as e:
            print(e)
        return list(title), result

    def get_all(self, sql, params=()):
        list_data = ()
        title = []
        try:
            conn, cursor = self.connect()
            cursor.execute(sql, params)
            list_data = cursor.fetchall()
            des = cursor.description
            title = [item[0] for item in des]
            self.close()
        except Exception as e:
            print(e)
        return title, list_data

    def insert(self, sql, params=()):
        return self.__edit(sql, params)

    def update(self, sql, params=()):
        return self.__edit(sql, params)

    def delete(self, sql, params=()):
        return self.__edit(sql, params)

    def __edit(self, sql, params):
        count = 0
        try:
            conn, cursor = self.connect()
            count = cursor.execute(sql, params)
            conn.commit()
            self.close()
        except Exception as e:
            print(e)
        return count


mysql = MysqlHelper(
    host='127.0.0.1',  # MySQL服务端的IP地址
    port=3306,  # MySQL默认PORT地址(端口号)
    username='root',  # 用户名
    password='nzh278799',  # 密码,也可以简写为passwd
    db='project',  # 库名称,也可以简写为db
    charset='utf8'  # 字符编码
)
mysql.connect()

# data = ((1, 'DQ12345678', 'DUC 2021-2022', 'ME 511', 'Master of Public health', 4.0, 'A', '12'),
#         (2, 'DQ12345678', 'DUC 2021-2022', 'ME 512', 'Master of Public health', 4.0, 'A', '13'),
#         (3, 'DQ12345678', 'DUC 2021-2022', 'ME 513', 'Master of Public health', 4.0, 'A', '12'),
#         (4, 'DQ12345678', 'DUC 2022-2023', 'ME 514', 'Master of Public health', 4.0, 'B', '14'))

# dict = {
#
# }
# academicyear = []
# for i in data:
#     if i[2] not in academicyear:
#         academicyear.append(i[2])
#
# for n in academicyear:
#     dict.setdefault(n, [])
#
# for m in data:
#     dict1 = {
#         'courseNum':m[3],
#         'courseName': m[4],
#         'score': m[5],
#         'GPA': m[6],
#         'courseLength': m[7]
#     }
#     if m[2] in dict:
#         dict.get(m[2]).append(dict1)
# print(dict)
# ID = "ER12345678"
# req = [{"prop": "",
#         "value": "",
#         "key": "",
#         "Academic_Year": "DUC 2020-2021",
#         "labelPosition": "right",
#         "addInputArr": [
#             {"prop": "", "value1": "AS 1", "value2": "操作系统", "value3": "80", "value4": "3", "value5": "40",
#              "key": "", "labelPosition": "right"},
#             {"prop": "", "value1": "AS 2", "value2": "", "value3": "", "value4": "", "value5": "", "key": "",
#              "labelPosition": "right"}]},
#        {"prop": "",
#         "value": "",
#         "key": "",
#         "Academic_Year": "DUC 2021-2022",
#         "labelPosition": "right",
#         "addInputArr": [
#             {"prop": "", "value1": "AS 3", "value2": "C++", "value3": "70", "value4": "2.8", "value5": "45", "key": "",
#              "labelPosition": "right"}]}]
#
# data = []
# course = []
# for i in req:
#     course.append(ID)
#     course.append(i.get('Academic_Year'))
#     course.append(i.get('statement'))
#     for n in i.get('addInputArr'):
#         course.append(n.get('value1'))
#         course.append(n.get('value2'))
#         course.append(n.get('value3'))
#         course.append(n.get('value4'))
#         course.append(n.get('value5'))
#         data.append(tuple(course))
#         course.pop()
#         course.pop()
#         course.pop()
#         course.pop()
#         course.pop()
#     course = []
# print(data)
#
# sql = """INSERT INTO `project`.`course` (`ID`, `academicYear`, `courseNum`, `courseName`, `score`, `gpa`, `courselength`)
#          VALUES (%s, %s, %s, %s, %s, %s, %s);"""
#
# for i in range(len(data)):
#     mysql.insert(sql, params=data[i])

# req = {"name":"sads","passport":"dasd","gender":"asd","nationality":"sa","DateOfBirth":"2023-02-08","Registration_Number":"",
#        "Degree_awarded":"","Major":"","GpA":"","DateOfAttendence":'',"DateOfGraduation":"","img":"","course":[]}
#
# print((req.get('passport'), req.get('name'), req.get('gender'), req.get('DateOfBirth'),
#                     req.get('nationality'), req.get('Registration_Number'), req.get('Major'), req.get('Degree_awarded'),
#                     req.get('GpA'), req.get('DateOfAttendence'), req.get('DateOfGraduation'), req.get('img')),'------------------')
#
# sql1 = """INSERT INTO `project`.`users` (`ID`, `name`, `Gender`, `date_of_birth`, `nationality`, `Registration_Number`,
#     `major`, `degree`, `GPA`, `DateOfAttendance`, `DateOfGraduation`, `image`)
#              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
#
# mysql.insert(sql1, params=(req.get('passport'), req.get('name'), req.get('gender'), req.get('DateOfBirth'),
#                     req.get('nationality'), req.get('Registration_Number'), req.get('Major'), req.get('Degree_awarded'),
#                     req.get('GpA'), req.get('DateOfAttendence'), req.get('DateOfGraduation'), req.get('img')))

# str1="[a,b,c]"
# print(type(str1))
#
# res=str1.strip('[')
# res=res.strip(']')
# res=res.split(',')
# print(res)
# print(type(res))

# arr = [{'Academic_Year': 'DUC 2121', 'addInputArr': [
#     {'key': '', 'labelPosition': 'right', 'prop': '', 'value1': '', 'value2': 'das', 'value3': '', 'value4': '',
#      'value5': ''},
#     {'key': '', 'labelPosition': 'right', 'prop': '', 'value1': 'fdsf', 'value2': '', 'value3': 'fds', 'value4': '12',
#      'value5': ''}], 'key': '', 'labelPosition': 'right', 'prop': '',
#         'statement': '8763617867637621786876361786763762178687636178676376217868763617867637621786', 'value': ''},
#
#
#
#        {'Academic_Year': 'fdsfsd', 'addInputArr': [
#            {'key': '', 'labelPosition': 'right', 'prop': '', 'value1': 'vfg', 'value2': '', 'value3': '', 'value4': '',
#             'value5': ''}], 'key': '', 'labelPosition': 'right', 'prop': '',
#         'statement': '876361786763762178687636178676376217868763617867637621786', 'value': ''},
#        {'Academic_Year': 'dasasd', 'addInputArr': [
#            {'key': '', 'labelPosition': 'right', 'prop': '', 'value1': 'dsadasd', 'value2': '12', 'value3': '',
#             'value4': '', 'value5': ''}], 'key': '', 'labelPosition': 'right', 'prop': '',
#         'statement': '876361786763762178687636178676376217868763617867637621786', 'value': ''}]
#
# data = []
# course = []
# for i in arr:
#     course.append('565576576556756567')
#     course.append(i.get('Academic_Year'))
#     for n in i.get('addInputArr'):
#         course.append(n.get('value1'))
#         course.append(n.get('value2'))
#         course.append(n.get('value3'))
#         course.append(n.get('value4'))
#         course.append(n.get('value5'))
#         course.append(i.get('statement'))
#         data.append(tuple(course))
#         course.pop()
#         course.pop()
#         course.pop()
#         course.pop()
#         course.pop()
#         course.pop()
#     course = []
# print(data)

dic = [{'prop': '', 'value': '', 'key': '', 'Academic_Year': '2018    Fall Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'ER 111', 'value2': 'General Psychology I', 'value3': '3.0', 'value4': 'A',
             'value5': '12.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 113', 'value2': 'Research Methods and Data Analysis I', 'value3': '4.0',
             'value4': 'B-', 'value5': '10.8', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 115', 'value2': 'Academic Writing', 'value3': '3.0', 'value4': 'B+',
             'value5': '9.9', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
       {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2019    Spring Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'ER 121', 'value2': 'General Psychology II', 'value3': '3.0', 'value4': 'B-',
             'value5': '8.1', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 122', 'value2': 'Research Methods and Data Analysis II', 'value3': '4.0',
             'value4': 'B', 'value5': '12.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 129', 'value2': 'Psychology of Social and Cultural Diversity', 'value3': '3.0',
             'value4': 'A', 'value5': '12.0', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
       {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2019    Fall Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'ER 124', 'value2': 'Developmental Psychology', 'value3': '3.0', 'value4': 'B+',
             'value5': '9.9', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 125', 'value2': 'Foundations of Neuroscience', 'value3': '4.0', 'value4': 'C',
             'value5': '8.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 127', 'value2': 'Fundamentals of Psychotherapy', 'value3': '3.0', 'value4': 'A',
             'value5': '12.0', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
       {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2020    Spring Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'ER 140', 'value2': 'Cognitive Psychology', 'value3': '3.0', 'value4': 'A-',
             'value5': '11.1', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 138', 'value2': 'Statistics', 'value3': '4.0', 'value4': 'B', 'value5': '12.0',
             'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 142', 'value2': 'Learning and Memory', 'value3': '3.0', 'value4': 'A',
             'value5': '12.0', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
       {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2020    Fall  Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'EC 121', 'value2': 'Clinical Psychology I', 'value3': '3.0', 'value4': 'B+',
             'value5': '9.9', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EC 122', 'value2': 'Personality Psychology', 'value3': '3.0', 'value4': 'C',
             'value5': '6.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EC 129', 'value2': 'Child and Adolescent Psychology', 'value3': '3.0',
             'value4': 'A', 'value5': '12.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EC 133', 'value2': 'Experimental Psychology', 'value3': '3.0', 'value4': 'A-',
             'value5': '11.1', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
       {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2021    Spring Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'EC 111', 'value2': 'Clinical Psychology II', 'value3': '3.0', 'value4': 'B',
             'value5': '9.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EC 113', 'value2': 'Health Psychology', 'value3': '3.0', 'value4': 'B',
             'value5': '9.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EC 115', 'value2': 'Animal Behavior', 'value3': '3.0', 'value4': 'A',
             'value5': '12.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EC 117', 'value2': 'Emotion and Affect', 'value3': '3.0', 'value4': 'B+',
             'value5': '9.9', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
       {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2021    Fall Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'EK 121', 'value2': 'Psychology Research Internship', 'value3': '3.0', 'value4': 'C',
             'value5': '6.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EQ 122', 'value2': 'Social Psychology', 'value3': '3.0', 'value4': 'A',
             'value5': '12.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EK 129', 'value2': 'Fear and Anxiety', 'value3': '3.0', 'value4': 'A-',
             'value5': '11.1', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'EK 133', 'value2': 'History of Psychology', 'value3': '3.0', 'value4': 'B',
             'value5': '9.0', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
       {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2022    Spring Semester', 'labelPosition': 'right',
        'addInputArr': [
            {'prop': '', 'value1': 'EQ 121', 'value2': 'Senior Thesis', 'value3': '3.0', 'value4': 'B', 'value5': '9.0',
             'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 152', 'value2': 'Cross-Cultural Psychology', 'value3': '3.0', 'value4': 'B',
             'value5': '9.0', 'key': '', 'labelPosition': 'right'},
            {'prop': '', 'value1': 'ER 159', 'value2': 'Consciousness and Sleep', 'value3': '3.0', 'value4': 'B',
             'value5': '9.0', 'key': '', 'labelPosition': 'right'}],
        'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'}]

dict = [{'prop': '', 'value': '', 'key': '', 'Academic_Year': '2018    Fall Semester', 'labelPosition': 'right',
         'addInputArr': [
             {'prop': '', 'value1': 'ER 111', 'value2': 'General Psychology I', 'value3': '3.0', 'value4': 'A',
              'value5': '12.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 113', 'value2': 'Research Methods and Data Analysis I', 'value3': '4.0',
              'value4': 'B-', 'value5': '10.8', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 115', 'value2': 'Academic Writing', 'value3': '3.0', 'value4': 'B+',
              'value5': '9.9', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
        {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2019    Spring Semester', 'labelPosition': 'right',
         'addInputArr': [
             {'prop': '', 'value1': 'ER 121', 'value2': 'General Psychology II', 'value3': '3.0', 'value4': 'B-',
              'value5': '8.1', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 122', 'value2': 'Research Methods and Data Analysis II', 'value3': '4.0',
              'value4': 'B', 'value5': '12.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 129', 'value2': 'Psychology of Social and Cultural Diversity', 'value3': '3.0',
              'value4': 'A', 'value5': '12.0', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
        {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2019    Fall Semester', 'labelPosition': 'right',
         'addInputArr': [
             {'prop': '', 'value1': 'ER 124', 'value2': 'Developmental Psychology', 'value3': '3.0', 'value4': 'B+',
              'value5': '9.9', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 125', 'value2': 'Foundations of Neuroscience', 'value3': '4.0', 'value4': 'C',
              'value5': '8.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 127', 'value2': 'Fundamentals of Psychotherapy', 'value3': '3.0', 'value4': 'A',
              'value5': '12.0', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
        {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2020    Spring Semester', 'labelPosition': 'right',
         'addInputArr': [
             {'prop': '', 'value1': 'ER 140', 'value2': 'Cognitive Psychology', 'value3': '3.0', 'value4': 'A-',
              'value5': '11.1', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 138', 'value2': 'Statistics', 'value3': '4.0', 'value4': 'B', 'value5': '12.0',
              'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'ER 142', 'value2': 'Learning and Memory', 'value3': '3.0', 'value4': 'A',
              'value5': '12.0', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
        {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2020    Fall  Semester', 'labelPosition': 'right',
         'addInputArr': [
             {'prop': '', 'value1': 'EC 121', 'value2': 'Clinical Psychology I', 'value3': '3.0', 'value4': 'B+',
              'value5': '9.9', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'EC 122', 'value2': 'Personality Psychology', 'value3': '3.0', 'value4': 'C',
              'value5': '6.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'EC 129', 'value2': 'Child and Adolescent Psychology', 'value3': '3.0',
              'value4': 'A', 'value5': '12.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'EC 133', 'value2': 'Experimental Psychology', 'value3': '3.0', 'value4': 'A-',
              'value5': '11.1', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
        {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2021    Spring Semester', 'labelPosition': 'right',
         'addInputArr': [
             {'prop': '', 'value1': 'EC 111', 'value2': 'Clinical Psychology II', 'value3': '3.0', 'value4': 'B',
              'value5': '9.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'EC 113', 'value2': 'Health Psychology', 'value3': '3.0', 'value4': 'B',
              'value5': '9.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'EC 115', 'value2': 'Animal Behavior', 'value3': '3.0', 'value4': 'A',
              'value5': '12.0', 'key': '', 'labelPosition': 'right'},
             {'prop': '', 'value1': 'EC 117', 'value2': 'Emotion and Affect', 'value3': '3.0', 'value4': 'B+',
              'value5': '9.9', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
        {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2021    Fall Semester', 'labelPosition': 'right',
         'addInputArr': [{'prop': '', 'value1': 'EK 121', 'value2': 'Psychology Research Internship', 'value3': '3.0',
                          'value4': 'C', 'value5': '6.0', 'key': '', 'labelPosition': 'right'},
                         {'prop': '', 'value1': 'EQ 122', 'value2': 'Social Psychology', 'value3': '3.0', 'value4': 'A',
                          'value5': '12.0', 'key': '', 'labelPosition': 'right'},
                         {'prop': '', 'value1': 'EK 129', 'value2': 'Fear and Anxiety', 'value3': '3.0', 'value4': 'A-',
                          'value5': '11.1', 'key': '', 'labelPosition': 'right'},
                         {'prop': '', 'value1': 'EK 133', 'value2': 'History of Psychology', 'value3': '3.0',
                          'value4': 'B', 'value5': '9.0', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'},
        {'prop': '', 'value': '', 'key': '', 'Academic_Year': '2022    Spring Semester', 'labelPosition': 'right',
         'addInputArr': [{'prop': '', 'value1': 'EQ 121', 'value2': 'Senior Thesis', 'value3': '3.0', 'value4': 'B',
                          'value5': '9.0', 'key': '', 'labelPosition': 'right'},
                         {'prop': '', 'value1': 'ER 152', 'value2': 'Cross-Cultural Psychology', 'value3': '3.0',
                          'value4': 'B', 'value5': '9.0', 'key': '', 'labelPosition': 'right'},
                         {'prop': '', 'value1': 'ER 159', 'value2': 'Consciousness and Sleep', 'value3': '3.0',
                          'value4': 'B', 'value5': '9.0', 'key': '', 'labelPosition': 'right'}],
         'statement': 'This is a statement listing courses completed online or by distance study and courses completed by regular classroom attendance'}]

new = 1
new = 2