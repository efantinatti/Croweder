# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 15:02:38 2021

@author: Mohammed Ibraheem
"""


import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from joblib import dump, load
import datetime
import mysql.connector

Dataset = np.loadtxt("store_Data.csv", delimiter=",")

X = Dataset[:,0:32]
y1 = Dataset[:,32]
y2 = Dataset[:,33]

X_train, X_test, y_train, y_test = train_test_split( X, y1, test_size=0.25, random_state=1)
knnAdult = KNeighborsRegressor(n_neighbors=5)
knnAdult.fit(X, y1)
predictionAdult = knnAdult.predict(X_test)
dump(knnAdult, 'knnAdult.joblib')
X_train, X_test, y_train, y_test = train_test_split( X, y2, test_size=0.25, random_state=1)
knnChild = KNeighborsRegressor(n_neighbors=5)
knnChild.fit(X, y2)
predictionChild = knnChild.predict(X_test)
dump(knnChild, 'knnChild.joblib')
# to load use:
clf = load('knnAdult.joblib')
clf2 = load('knnChild.joblib')
#ex = clf.predict(X_test)
dt = datetime.date.today()
wd = dt.weekday()
month =  dt.month
forecast_data = np.zeros((13, 32))
forecast_data[:,month - 1] = 1
forecast_data[:,25+wd] = 1
for i in range(0,13):
    forecast_data[i,12 + i]=1
#h_lable = ['9 am','10 am','11 am','12 pm','1 pm','2 pm','3 pm','4 pm','5 pm','6 pm','7 pm','8 pm','9 pm']
forecastAdult = clf.predict(forecast_data)
forecastCild = clf2.predict(forecast_data)
mydb = mysql.connector.connect(host = "sep769.fantinatti.net",user = "mibraheem",passwd = "ibraheem12345",database = "SEP769",)
c = mydb.cursor()
for i in range(13):
    sql = "INSERT INTO SEP769Forecast (Hour, Adults , Children, Total) VALUES (%s, %s, %s, %s)"
    val = ((i +9),int(forecastAdult[i]), int(forecastCild[i]), (int(forecastCild[i])+int(forecastAdult[i])))
    c.execute(sql, val)
    mydb.commit()


mydb.close()