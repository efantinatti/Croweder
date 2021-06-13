# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 19:48:08 2021

@author: Mohammed Ibraheem
"""

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import mysql.connector
from tkinter import *
from tkinter import ttk
import pandas as pd
from joblib import dump, load
import datetime
import numpy as np


root = Tk()
root.title('DASHBOARD')
root.iconbitmap('Image.ico')
root.geometry("850x850")


# Add some style
style = ttk.Style()
#Pick a theme
style.theme_use("default")
# Configure our treeview colors

style.configure("Treeview", 
	background="#D3D3D3",
	foreground="black",
	rowheight=25,
	fieldbackground="#D3D3D3"
	)
# Change selected color
style.map('Treeview', 
	background=[('selected', 'blue')])

# Create Frames
tree_frame = Frame(root)
tree_frame.grid(row =0 , column =0,padx=20 ,pady=20)
graph_frame = Frame(root)
graph_frame.grid(row =1 , column =0,padx=20 ,pady=20)
forecast_frame = LabelFrame(root, text = "Forecasting Number of Customers")
forecast_frame.grid(row =0 , column =1,padx=20 ,pady=20)
availability_frame = LabelFrame(root, text = "Store Capacity Message")
availability_frame.grid(row =1 , column =1,padx=20 ,pady=20)

# Treeview Scrollbar
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

# Create Treeview
my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
# Pack to the screen
my_tree.pack()

#Configure the scrollbar
tree_scroll.config(command=my_tree.yview)

# Define Our Columns
my_tree['columns'] = ("ID", "Time Stamp", "Height", "Flaginout", "Count", "Adult", "Children", "Total")

# Formate Our Columns
my_tree.column("#0", width=0, stretch=NO)
my_tree.column("ID", anchor=CENTER, width=50)
my_tree.column("Time Stamp", anchor=W, width=100)
my_tree.column("Height", anchor=CENTER, width=60)
my_tree.column("Flaginout", anchor=CENTER, width=60)
my_tree.column("Count", anchor=W, width=60)
my_tree.column("Adult", anchor=CENTER, width=60)
my_tree.column("Children", anchor=CENTER, width=60)
my_tree.column("Total", anchor=CENTER, width=60)



# Create Headings 
my_tree.heading("#0", text="", anchor=W)
my_tree.heading("ID", text="ID", anchor=CENTER)
my_tree.heading("Time Stamp", text="Time Stamp", anchor=W)
my_tree.heading("Height", text="Height", anchor=CENTER)
my_tree.heading("Flaginout", text="Flaginout", anchor=CENTER)
my_tree.heading("Count", text="Count",anchor= W)
my_tree.heading("Adult", text="Adult", anchor=CENTER)
my_tree.heading("Children", text="Children", anchor=CENTER)
my_tree.heading("Total", text="Total", anchor=CENTER)


# Create striped row tags
my_tree.tag_configure('oddrow', background="white")
my_tree.tag_configure('evenrow', background="lightblue")

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
forecastAdult = clf.predict(forecast_data)
forecastCild = clf2.predict(forecast_data)



def myClick():
    cap = e.get()
    global max_cap
    max_cap = int(cap)


e = Entry(availability_frame, width=4, font=('Helvetica', 10))
e.grid(row =0 , column =0,padx=20 ,pady=20)
e.insert(0, "20")

max_Button = Button(availability_frame, text="Max Capacity", command=myClick)
max_Button.grid(row =1 , column =0,padx=20 ,pady=20)


#global records
global count, row
count = 0

def updat_tree():
    global records
    mydb = mysql.connector.connect(
		host = "sep769.fantinatti.net",
		user = "ro",
		passwd = "ro123",
		database = "SEP769",
	)
    c = mydb.cursor()
    c.execute("SELECT * FROM SEP769.SEP769")
    records = c.fetchall()
    mydb.commit()
    row = 0
    for record in records:
        count = record[4]
        if row % 2 == 0:
            my_tree.insert(parent='', index='end',  text="", values=(record[0], record[1], record[2],record[3],record[4],record[5],record[6],record[7]), tags=('evenrow',))
        else:
            my_tree.insert(parent='', index='end',  text="", values=(record[0], record[1], record[2],record[3],record[4],record[5],record[6],record[7]), tags=('oddrow',))
        row += 1
    mydb.close()
    if count >= max_cap:
        msg_Lable = Label(availability_frame, bd = 8, relief = "solid", font = "Times 24 bold", bg = "red", fg = "white", text = "Store is FULL")
        msg_Lable.grid(row =2 , column =0,padx=20 ,pady=20)
    else:
        msg_Lable = Label(availability_frame, bd = 8, relief = "solid", font = "Times 22 bold", bg = "green", fg = "white", text = "Available for: " + str(max_cap - count ))
        msg_Lable.grid(row =2 , column =0,padx=20 ,pady=20)

            
refresh = Button(tree_frame, text="Refresh", command=updat_tree)
refresh.pack()


#my_tree.after(5000, updat_tree)
ex = np.arange(9,22)
f = Figure(figsize=(5,3.5), dpi = 100)
a = f.add_subplot(111)

a.bar(ex, forecastAdult, width = 0.25, color='r')
a.bar(ex,forecastCild, color = 'b', width = 0.25, bottom=forecastAdult)
a.set_ylabel('Number of Customers')
a.set_title('Hourly Forecast Number of Customers ')
a.set_xticks(ex, ('G1', 'G2', 'G3', 'G4', 'G5'))
a.set_yticks(np.arange(0, 60, 10))
a.legend(labels=['Adults', 'Children'])

canvas = FigureCanvasTkAgg(f,graph_frame)
canvas.get_tk_widget().pack(expand = True)

Ad = Label(forecast_frame, text="Adult")
Ad.grid(row=0, column=1)
Ch = Label(forecast_frame, text="Chile")
Ch.grid(row=0, column=2)
total= Label(forecast_frame, text="Total")
total.grid(row=0, column=3)
mn = Label(forecast_frame, text="9 a.m")
mn.grid(row=1, column=0)
Ad1 = Label(forecast_frame, text=int(forecastAdult[0]),bg = "white")
Ad1.grid(row=1, column=1)
Ch1 = Label(forecast_frame, text=int(forecastCild[0]),bg = "white")
Ch1.grid(row=1, column=2)
t1 = Label(forecast_frame, text=int(forecastAdult[0]+int(forecastCild[0])),bg = "white")
t1.grid(row=1, column=3)
mn1 = Label(forecast_frame, text="10 a.m")
mn1.grid(row=2, column=0)
Ad2 = Label(forecast_frame, text=int(forecastAdult[1]),bg = "white")
Ad2.grid(row=2, column=1)
Ch2 = Label(forecast_frame, text=int(forecastCild[1]),bg = "white")
Ch2.grid(row=2, column=2)
t2= Label(forecast_frame, text=int(forecastAdult[1]+int(forecastCild[1])),bg = "white")
t2.grid(row=2, column=3)
mn2 = Label(forecast_frame, text="11 a.m")
mn2.grid(row=3, column=0)
Ad3 = Label(forecast_frame, text=int(forecastAdult[2]),bg = "white")
Ad3.grid(row=3, column=1)
Ch3 = Label(forecast_frame, text=int(forecastCild[2]),bg = "white")
Ch3.grid(row=3, column=2)
t3 = Label(forecast_frame, text=int(forecastAdult[2]+int(forecastCild[2])),bg = "white")
t3.grid(row=3, column=3)
mn3 = Label(forecast_frame, text="12 a.m")
mn3.grid(row=4, column=0)
Ad4 = Label(forecast_frame, text=int(forecastAdult[3]),bg = "white")
Ad4.grid(row=4, column=1)
Ch4 = Label(forecast_frame, text=int(forecastCild[3]),bg = "white")
Ch4.grid(row=4, column=2)
t1 = Label(forecast_frame, text=int(forecastAdult[3]+int(forecastCild[3])),bg = "white")
t1.grid(row=4, column=3)
mn4 = Label(forecast_frame, text="1 p.m")
mn4.grid(row=5, column=0)
Ad5 = Label(forecast_frame, text=int(forecastAdult[4]),bg = "white")
Ad5.grid(row=5, column=1)
Ch5 = Label(forecast_frame, text=int(forecastCild[4]),bg = "white")
Ch5.grid(row=5, column=2)
t5 = Label(forecast_frame, text=int(forecastAdult[4]+int(forecastCild[4])),bg = "white")
t5.grid(row=5, column=3)
mn5 = Label(forecast_frame, text="2 p.m")
mn5.grid(row=6, column=0)
Ad6 = Label(forecast_frame, text=int(forecastAdult[5]),bg = "white")
Ad6.grid(row=6, column=1)
Ch6 = Label(forecast_frame, text=int(forecastCild[5]),bg = "white")
Ch6.grid(row=6, column=2)
t6 = Label(forecast_frame, text=int(forecastAdult[5]+int(forecastCild[5])),bg = "white")
t6.grid(row=6, column=3)
mn6 = Label(forecast_frame, text="3 p.m")
mn6.grid(row=7, column=0)
Ad7 = Label(forecast_frame, text=int(forecastAdult[6]),bg = "white")
Ad7.grid(row=7, column=1)
Ch7 = Label(forecast_frame, text=int(forecastCild[6]),bg = "white")
Ch7.grid(row=7, column=2)
t7 = Label(forecast_frame, text=int(forecastAdult[6]+int(forecastCild[6])),bg = "white")
t7.grid(row=7, column=3)
mn7 = Label(forecast_frame, text="4 p.m")
mn7.grid(row=8, column=0)
Ad8 = Label(forecast_frame, text=int(forecastAdult[7]),bg = "white")
Ad8.grid(row=8, column=1)
Ch8 = Label(forecast_frame, text=int(forecastCild[7]),bg = "white")
Ch8.grid(row=8, column=2)
t8 = Label(forecast_frame, text=int(forecastAdult[7]+int(forecastCild[7])),bg = "white")
t8.grid(row=8, column=3)
mn8 = Label(forecast_frame, text="5 a.m")
mn8.grid(row=9, column=0)
Ad9 = Label(forecast_frame, text=int(forecastAdult[8]),bg = "white")
Ad9.grid(row=9, column=1)
Ch9 = Label(forecast_frame, text=int(forecastCild[8]),bg = "white")
Ch9.grid(row=9, column=2)
t1 = Label(forecast_frame, text=int(forecastAdult[8]+int(forecastCild[8])),bg = "white")
t1.grid(row=9, column=3)
mn9 = Label(forecast_frame, text="6 a.m")
mn9.grid(row=10, column=0)
Ad10 = Label(forecast_frame, text=int(forecastAdult[9]),bg = "white")
Ad10.grid(row=10, column=1)
Ch10 = Label(forecast_frame, text=int(forecastCild[9]),bg = "white")
Ch10.grid(row=10, column=2)
t1 = Label(forecast_frame, text=int(forecastAdult[9]+int(forecastCild[9])),bg = "white")
t1.grid(row=10, column=3)
mn10 = Label(forecast_frame, text="7 a.m")
mn10.grid(row=11, column=0)
Ad11 = Label(forecast_frame, text=int(forecastAdult[10]),bg = "white")
Ad11.grid(row=11, column=1)
Ch11 = Label(forecast_frame, text=int(forecastCild[10]),bg = "white")
Ch11.grid(row=11, column=2)
t11 = Label(forecast_frame, text=int(forecastAdult[10]+int(forecastCild[10])),bg = "white")
t11.grid(row=11, column=3)
mn11 = Label(forecast_frame, text="8 a.m")
mn11.grid(row=12, column=0)
Ad12 = Label(forecast_frame, text=int(forecastAdult[11]),bg = "white")
Ad12.grid(row=12, column=1)
Ch12 = Label(forecast_frame, text=int(forecastCild[11]),bg = "white")
Ch12.grid(row=12, column=2)
t12 = Label(forecast_frame, text=int(forecastAdult[11]+int(forecastCild[11])),bg = "white")
t12.grid(row=12, column=3)
mn12 = Label(forecast_frame, text="9 a.m")
mn12.grid(row=13, column=0)
Ad13 = Label(forecast_frame, text=int(forecastAdult[12]),bg = "white")
Ad13.grid(row=13, column=1)
Ch13 = Label(forecast_frame, text=int(forecastCild[12]),bg = "white")
Ch13.grid(row=13, column=2)
t13 = Label(forecast_frame, text=int(forecastAdult[12]+int(forecastCild[12])),bg = "white")
t13.grid(row=13, column=3)



root.mainloop()
