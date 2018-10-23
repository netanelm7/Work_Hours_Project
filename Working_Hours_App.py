from calendar import monthrange
import time
import pymongo

working_day_hours = 9.5

def Days_In_Given_Month(year,month):
 return monthrange(year,month)[1]

def Get_Day_Name(day):
    if day == 0:
        return "Monday"
    if day == 1:
        return "Tuesday"
    if day == 2:
        return "Wednesday"
    if day == 3:
        return "Thursday"
    if day == 4:
        return "Friday"
    if day == 5:
        return "Saturday"
    if day == 6:
        return "Sunday"


def bussiness_days_in_month(year,month):
    num_of_days = Days_In_Given_Month(int(year),int(month))
    bussiness_days = 0

    if type(month) == int:
        month = str(month)
    if type(year) == int:
        year = str(year)

    if len(year) != 2:
        year = year[2:]

    for day in range(1, num_of_days + 1, 1):
        time_object = time.strptime("{} {} {}".format(day, month, year),"%d %m %y")
        day_str = Get_Day_Name(time_object.tm_wday)
        if day_str != "Saturday" and day_str != "Friday":
            bussiness_days = bussiness_days + 1

    return bussiness_days

def Calculate_Work_Minutes(hour_str):
    temp_arr = hour_str.split(":")

    hours_calculator = int(temp_arr[0]) * 60
    minutes_calculator = hours_calculator + int(temp_arr[1])

    return minutes_calculator

def Connect_To_MongoDB(db_name):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    try:
        mydb = myclient[db_name]
    except pymongo.errors.ServerSelectionTimeoutError:
        print("The mongod server is not started, can't connect to the mongo server")
        return False

    try:
        db_len = myclient.list_database_names()
    except pymongo.errors.ServerSelectionTimeoutError:
        print("The mongod server is not started, can't connect to the mongo server")
        return False

    if len(db_len) == 0:
        print("The mongod server is not started, can't connect to the mongo server")
        return False

    mycollection = mydb["Work_Hours_Table"]

    if len(mydb.list_collection_names()) == 0:
        print("The db name isnt correct, can't connect to the db name")
        return False

    return mycollection

def Check_Time_String(time_str):
    if not ":" in time_str:
        print("No : in the string")
        return False

    if type(time_str) != str:
        print("The time string isn't a str")
        return False

    if len(time_str.split(":")) > 2:
        print("too many :")
        return False

    hours = time_str.split(":")[0]
    minutes = time_str.split(":")[1]

    try:
        int(hours)
    except ValueError:
        print("Not a number")
        return False

    try:
        int(minutes)
    except ValueError:
        print("Not a number")
        return False

    if int(hours) > 23 or int(hours) < 0:
        print("No such hours")
        return False

    if int(minutes) > 59 or int(minutes) < 0:
        print("No such minutes")
        return False

    return True

def Calculate_All_Current_Month_Hours(my_collection):
    all_records = my_collection.find()
    sum_working_hours = 0
    current_date = time.strftime("%d-%m-%Y")
    currect_month = int(current_date.split("-")[1])
    currect_year = int(current_date.split("-")[2])

    for record in all_records:
        if (record["month"] == currect_month) and (record["year"] == currect_year):
            sum_working_hours = sum_working_hours + record["working_hours"]

    return sum_working_hours

def main():
    mycollection = Connect_To_MongoDB("Work_Hours_DB")
    if mycollection == False:
        return False

    # Getting the corrent day, month, year
    current_date = time.strftime("%d-%m-%Y")
    currect_day = int(current_date.split("-")[0])
    currect_month = int(current_date.split("-")[1])
    currect_year = int(current_date.split("-")[2])

    global working_day_hours

    # Get the working hours of the corrent month
    working_days = bussiness_days_in_month(currect_year,currect_month)
    working_month_hours = working_day_hours*working_days

    print("The corrent working hours for {}-{} is {}".format(currect_month,currect_year,working_month_hours))

    work_entrance = input("When did you start the work? ")
    if Check_Time_String(work_entrance) == False:
        return False
    entrance = Calculate_Work_Minutes(work_entrance)
    work_left = input("When did you left the work? ")
    left = Calculate_Work_Minutes(work_left)
    diff = (float(left) - float(entrance))/60

    # Making the float 2 decimal places
    diff = "{:.2f}".format(diff)
    diff = float(diff)

    # Which means the start time is higher then the ending time
    if diff < 0:
        diff = diff * (-1)

    DB_dict = { "day" : currect_day, "month" : currect_month, "year": currect_year, "start_working_time" : work_entrance,
             "end_working_time" :  work_left, "working_hours" : diff, "need_to_work_this_month" : working_month_hours }

    mycollection.insert_one(DB_dict)

    current_working_hours = Calculate_All_Current_Month_Hours(mycollection)

    print("You have worked {} hours\nHave {} left to complete\nAnd total {}".format(current_working_hours,working_month_hours-current_working_hours,working_month_hours))

main()