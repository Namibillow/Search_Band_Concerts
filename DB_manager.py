#!/usr/bin/env python

import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from DB_config import read_db_config


class DataBase:
    def __init__(self):
        self.db_config = read_db_config()

        try:
            self.cnx = mysql.connector.connect(**self.db_config)

            if(self.cnx.is_connected()):
                self.mycursor = self.cnx.cursor()
                self.db = self.db_config["database"]
                self.tables = self.GetTableName()
                print('connection established.')

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                self.CreateDatabase()
            else:
                print(err)

    def CheckDatabase(self):
        '''
        Chcecks what databases are avaiable
        '''
        self.mycursor.execute("SHOW DATABASES")

        print('showing databases: ')
        for d in self.mycursor:
            print(d)

    def CreateDataBase(self):
        '''
        Creat a database
        '''
        try:
            self.mycursor.execute("CREATE DATABASE %s DEFAULT CHARACTER SET 'utf8';" % self.db)
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))

    def CreateTable(self, table_name):
        '''
        Create a table
        '''
        try:
            self.mycursor.execute("CREATE TABLE '%s'.'%s' ('YEAR' INT NOT NULL, 'MONTH' INT NOT NULL, 'DATE' INT NOT NULL, 'BAND' VARCHAR(80) NOT NULL, 'AREA' VARCHAR(5) NOT NULL, 'LOCATION' VARCHAR(80) NOT NULL" % self.db, table_name)
        except mysql.connector.Error as err:
            print("Failed creating a table: {}".format(err))

    def InsertTable(self, year, month, day, band, area, location):
        '''
        Insert new data
        '''
        for t in self.tables:
            sql = "INSERT INTO " + str(t) + " VALUES (%s, %s, %s, %s, %s, %s);"
            val = (year, month, day, band, area, location)
            self.mycursor.execute(sql, val)
            self.cnx.commit()

    def DeleteTableData(self):
        '''
        Delete all data of that table
        '''
        print("deleting everything right now")
        for t in self.tables:
            self.mycursor.execute("DELETE FROM " + t)
            self.cnx.commit()

    def DeleteSpecificRows(self):
        '''
        Delete old data
        '''
        now = datetime.now()
        for t in self.tables:
            sql = "DELETE FROM " + t + " WHERE YEAR = " + str(now.year) + " AND MONTH = " + str(now.month) + " AND DAY < " + str(now.day)
            self.mycursor.execute(sql)
            self.cnx.commit()

        print("deleting old stuff done!")

    def GetTableName(self):
        '''
        Return a list of tables in that database
        '''
        self.mycursor.execute("USE " + self.db)
        self.mycursor.execute("SHOW TABLES")
        # print("Showing tables:")
        self.tables = self.mycursor.fetchall()
        self.tables = [''.join(t) for t in self.tables]

        # for (table_name,) in self.mycursor:
        #     print(table_name)

        return self.tables

    def GetTableData(self, year=None, month=None, area=None, band=None):

        for t in self.tables:
            searchQuery = self.GenerateSearchQuery(t, year, month, area, band)
            try:
                self.mycursor.execute(searchQuery)
                myresult = self.mycursor.fetchall()

                return myresult
                # row = self.mycursor.fetchone()

                # while row is not None:
                #     print(row)
                #     row = self.mycursor.fetchone()

            except mysql.connector.Error as e:
                print(e)

    def GenerateSearchQuery(self, table_name, year, month, area, band):
        query = "SELECT * FROM " + str(table_name)
        condition = []

        if year != None:
            condition.append(" YEAR = " + str(year))

        if month != None:
            condition.append(" MONTH = " + str(month))

        if area != None and area != "全て":
            condition.append(" AREA = '" + area + "'")

        if band != None:
            bandsQ = " ( "
            for b in band:
                bandsQ += " BAND LIKE '%" + b + "%' OR "

            bandsQ = bandsQ[:-4] + " ) "
            condition.append(bandsQ)

        if condition:
            query = query + " WHERE"
            for c in condition[:len(condition) - 1]:
                query = query + c + " AND "

            query = query + condition[-1]

        # print(query)
        return query

    def __del__(self):
        print("connection closed")
        self.cnx.commit()
        # self.mycursor.close()
        self.cnx.close()


# if __name__ == '__main__':
#     db = DataBase()
    # db.DeleteTableData()
    # # db.CheckDatabase()
    # db.GetTableName()
    # db.InsertTable(2020, 3, 12, "Hareruya", "東京", "Zipp Japan")
