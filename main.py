# Michelle Vences
# CS 341, FALL 2024
# Project 1 - CTA Database App
# Description: Program that outputs and plots different info from the CTA stations/lines

import sqlite3
import matplotlib.pyplot as figure
#  connect to db
def connect_db(path):
    dbConn = sqlite3.connect(path)
    return dbConn
# function calls to initalize menu & output general stats
def initalize_program():
    dbConn = connect_db("datafiles/CTA2_L_daily_ridership.db")
    gen_stats(dbConn)
    menu(dbConn)
# program menu for inputs (1-9)
def menu(dbConn):
    while True:
        cmd = input('\nPlease enter a command (1-9, x to exit): ')
        if cmd == 'x':
            dbConn.close()
            break
        elif cmd == '1':
            retrieve_stations(dbConn)
        elif cmd == '2':
            ridership_percentage(dbConn)
        elif cmd == '3':
            get_weekdays_rs_by_station(dbConn)
        elif cmd == '4':
            get_stops_by_line_dir(dbConn)
        elif cmd == '5':
            total_stops_by_color(dbConn)
        elif cmd == '6':
            yearly_station_rs(dbConn)    
        elif cmd == '7':
            total_rs_monthly(dbConn)
        elif cmd == '8':
            compare_stations(dbConn)
        elif cmd == '9':
            stations_within_mile(dbConn)
        else:
            print('**Error, unknown command, try again...')
# retrieving general stats from database and printing 
def gen_stats(dbConn):
    dbCursor = dbConn.cursor() 
     
    sql_stations = """
        SELECT COUNT(*)
        FROM Stations;
    """
    sql_stops = """
        SELECT COUNT(*)
        FROM Stops;
    """
    sql_entries = """
        SELECT COUNT(*)
        FROM Ridership;
    """
    sql_date = """
        SELECT MIN(strftime('%Y-%m-%d', Ride_Date)), MAX(strftime('%Y-%m-%d',Ride_Date))
        FROM Ridership;
    """   
    sql_totalrs = """
        SELECT SUM(Num_Riders)
        FROM Ridership;
    """ 
    
    dbCursor.execute(sql_stations)
    stations = dbCursor.fetchone()[0]
    
    dbCursor.execute(sql_stops)
    stops = dbCursor.fetchone()[0]

    dbCursor.execute(sql_entries)
    ride_entries = dbCursor.fetchone()[0]
    
    dbCursor.execute(sql_date)
    date = dbCursor.fetchone()
    min_date, max_date = date
    
    dbCursor.execute(sql_totalrs)
    total_ridership = dbCursor.fetchone()[0]
        
    print('** Welcome to CTA L analysis app **\n')
    print(
        'General Statistics:',
        f'\n  # of stations: {stations:,}',
        f'\n  # of stops: {stops:,} ',
        f'\n  # of ride entries: {ride_entries:,}',
        f'\n  date range: {min_date} - {max_date}',
        f'\n  Total ridership: {total_ridership:,}'
    )
# command 1: finding all stations that match the user input & printing out the output
def retrieve_stations(dbConn):
    # returns station with their given station ID in alphabetical order
    sql = """
        SELECT Station_ID, Station_Name
        FROM Stations
        WHERE Station_Name
        LIKE ?
        ORDER BY Station_Name ASC;
        """
    
    name = input('\nEnter partial station name (wildcards _ and %): ')    
    dbCursor = dbConn.cursor()
    dbCursor.execute(sql, [name])
    res = dbCursor.fetchall()
    
    if not res:
        print("**No stations found...")
    else:
        for row in res:
            print(row[0], ":", row[1])
# command 2: retrieving the ridership on weekday, saturdays and sundays/holidays for a given station
def ridership_percentage(dbConn):
    name = input('\nEnter the name of the station you would like to analyze: ')
    dbCursor = dbConn.cursor()
    #  returns total ridership grouped by the type of day
    sql = """
        SELECT Type_of_Day, SUM(Num_Riders)
        FROM Stations
        JOIN Ridership
        ON Ridership.Station_ID =
            Stations.Station_ID
        WHERE Station_Name = ?
        GROUP BY Type_of_Day
        ;
    """
    dbCursor.execute(sql, [name])
    seperate_rs = dbCursor.fetchall()
    # returns the total ridership for all days
    sql_total = """
        SELECT SUM(Num_Riders)
        FROM Stations
        JOIN Ridership
        ON Ridership.Station_ID =
            Stations.Station_ID
        WHERE Station_Name = ?
        ;
    """
    
    dbCursor.execute(sql_total, [name])
    total_rs = dbCursor.fetchall()

    if not seperate_rs:
        print('**No data found...')
        return 
    else:
        for row in seperate_rs:
            if row[0] == 'W':
                weekly_rs = row[1]
            if row[0] == 'A':
                saturday_rs = row[1]
            if row[0] == 'U':
                sunday_rs = row[1]

    total = total_rs[0][0]
    weekday_percentage = (weekly_rs / total) * 100 
    sat_percentage = (saturday_rs / total) * 100
    sun_percentage = (sunday_rs / total) * 100
    
    print(
        "Percentage of ridership for the", name, "station:\n"
        "  Weekday ridership:", f"{weekly_rs:,}", f"({weekday_percentage:.2f}%)\n"
        "  Saturday ridership:", f"{saturday_rs:,}", f"({sat_percentage:.2f}%)\n"
        "  Sunday/holiday ridership:", f"{sunday_rs:,}", f"({sun_percentage:.2f}%)\n"
        "  Total ridership:", f"{total:,}"
    )
# command 3: Retrieving total ridership on weekdays for all stations & calculating percentage for every station
def get_weekdays_rs_by_station(dbConn):
    dbCursor = dbConn.cursor()
    # returns the total ridership at each station for weekedays
    sql = """
        SELECT Station_Name, SUM(Num_Riders) as riders
        FROM Stations
        JOIN Ridership
        ON Ridership.Station_ID =
        Stations.Station_ID
        WHERE Type_of_Day = 'W'
        GROUP BY Station_Name
        ORDER BY riders DESC
        ;
    """
    # returns the total ridership across all stations for weekdays
    sql_total = """
        SELECT SUM(Num_Riders)
        FROM Ridership
        WHERE Type_of_Day = 'W'
        ;
    """
    
    dbCursor.execute(sql)
    res = dbCursor.fetchall()
    
    dbCursor.execute(sql_total)
    total_sum = dbCursor.fetchone()[0]
    
    if not res:
        return
    else:
        print("Ridership on Weekdays for Each Station")
        for row in res:
            station, ridership = row[0], row[1]
            percentage = (ridership / total_sum) * 100
            print(station, ":", f"{ridership:,}", f"({percentage:.2f}%)") 
# command 4: given a line color & direction outputs all the stops if any 
def get_stops_by_line_dir(dbConn):
    dbCursor = dbConn.cursor() 
    user_color = input("\nEnter a line color (e.g. Red or Yellow): ")
    # checks if the color is in the database
    sql_color = """
        SELECT Color
        FROM Lines
        WHERE LOWER(Color) = LOWER(?);
    """
    
    dbCursor.execute(sql_color, [user_color])
    color = dbCursor.fetchone()
    
    if not color:
        print("**No such line...")
        return
    
    color = color[0]
    direction = input("Enter a direction (N/S/W/E): ")
    # return the direction & stop_name aswell as if it is handicap accessible
    sql_direction = """
        SELECT Direction, Stop_Name, ADA
        FROM Stops
        JOIN StopDetails
        ON StopDetails.Stop_ID = Stops.Stop_ID
        JOIN Lines
        ON Lines.Line_ID = StopDetails.Line_ID
        WHERE LOWER(Lines.Color) = LOWER(?)
        AND UPPER(Stops.Direction) = UPPER(?)
        ORDER BY Stop_Name ASC;
    """
    
    dbCursor.execute(sql_direction, (color, direction))
    stops = dbCursor.fetchall()
    
    if not stops:
        print("**That line does not run in the direction chosen...")
        return
    for row in stops:
        dir, stop, ada = row
        if ada == 1:
            print(f"{stop} : direction = {dir} (handicap accessible)")
        else:
            print(f"{stop} : direction = {dir} (not handicap accessible)")
# command 5: Retrieves stops for each color ordered by direction & outputs result
def total_stops_by_color(dbConn):
    print("Number of Stops For Each Color By Direction")
    dbCursor = dbConn.cursor() 
    # retrieves all stops orders by direction & color
    sql = """
        SELECT Color, COUNT(Stops.Stop_ID), Direction
        FROM Stops
        JOIN StopDetails
        ON Stops.Stop_ID = StopDetails.Stop_ID
        JOIN Lines
        ON StopDetails.Line_ID = Lines.Line_ID
        GROUP BY Color, Direction
        ORDER BY Color ASC, Direction ASC;
    """
    # retrieves total amount of stops
    sql_total = """
        SELECT COUNT(Stop_ID)
        FROM Stops;
    """

    dbCursor.execute(sql)
    stops = dbCursor.fetchall()
    
    dbCursor.execute(sql_total)
    total_stops = dbCursor.fetchone()[0]
    
    for row in stops:
        color, num_stops, dir = row
        percentage = (num_stops / total_stops) * 100
        print(f"{color} going {dir} : {num_stops} ({percentage:.2f}%)")
#  helper function to check if station name given returns single station or multiple
def check_stations_input(dbConn,input):
    dbCursor = dbConn.cursor() 
    # checks if the station name given exists in the db by returning all stations
    sql_station = """
        SELECT Station_Name
        FROM Stations
        WHERE Station_Name
        LIKE ?
        """
    dbCursor.execute(sql_station, [input])
    stations = dbCursor.fetchall()
    if not stations:
        print("**No station found...")
        return False
    if len(stations) > 1:
        print("**Multiple stations found...")
        return False
    return stations   
# command 6: Takes in a station name and outputs the result of the yearly ridership at the given station
def yearly_station_rs(dbConn):
    dbCursor = dbConn.cursor() 
    name = input("\nEnter a station name (wildcards _ and %): ")
    output = check_stations_input(dbConn, name)
    # returns the station name and total ridership grouped by every year
    sql_station_rs_year = """
        SELECT Station_Name, SUM(Num_Riders) as Riders, strftime('%Y', Ride_Date) as Year
        FROM Stations
        JOIN Ridership
        ON Ridership.Station_ID = Stations.Station_ID
        WHERE Station_Name LIKE ?
        GROUP BY Year
        ORDER BY Year ASC;
        """ 
        
    if output == False:
        return
    station_name = output[0][0]
     
    dbCursor.execute(sql_station_rs_year, [name])
    rs_year = dbCursor.fetchall()
    
    print(f"Yearly Ridership at {station_name}")
    for row in rs_year:
        name, ridership, year = row
        print(f"{year} :", f"{ridership:,}")
         
    res = input("\nPlot? (y/n) ")
    if res == "y":
        x = []
        y = []
        for row in rs_year:
            name, ridership, year = row
            x.append(year)
            y.append(ridership)
        x_label = "Year"
        y_label = "Number of Riders"
        title = "Yearly Ridership at UIC-Halsted Station"
        data_plot(x, y, x_label, y_label, title)
    else:
        return
# helper function to plot data 
def data_plot(x, y, x_label, y_label, title):
    # parameters follow as:
    # x : x-axis data as []
    # y : y-axis data as []
    # x_label : title for x axis
    # y_label : title for y axis
    # title : title of figure
    figure.xlabel(x_label)
    figure.ylabel(y_label)
    figure.title(title)
    figure.ioff()
    figure.plot(x,y)
    figure.show()
#  command 7: outputs monthly ridership given a year and station from the user  
def total_rs_monthly(dbConn):
    name = input("\nEnter a station name (wildcards _ and %): ")
    output = check_stations_input(dbConn, name)
    dbCursor = dbConn.cursor() 
    
    if output == False: 
        return
    year = input("Enter a year: ")
    # returns the total ridership grouped by every month in a year 
    sql_station_rs_monthly = """
        SELECT SUM(Num_Riders) as Riders, strftime('%m/%Y', Ride_Date) as Date
        FROM Stations
        JOIN Ridership
        ON Ridership.Station_ID = Stations.Station_ID
        WHERE Station_Name LIKE ? AND  strftime('%Y', Ride_Date) = ?
        GROUP BY Date
        ORDER BY Date ASC;
        """ 
        
    dbCursor.execute(sql_station_rs_monthly, [name, year])
    res = dbCursor.fetchall()
    station_name = output[0][0]

    # formatting output
    print(f"Monthly Ridership at {station_name} for {year}")
    for row in res:
        rs, month_year = row
        print(f"{month_year} : {rs:,}")
        
    plot_ans = input("\nPlot? (y/n) ")
    if plot_ans == "y":
        x = []
        y = []
        for row in res:
            rs, month_year  = row
            x.append(month_year[:2])
            y.append(rs)

        x_label = "Month"
        y_label = "Number of Riders"
        title = f"Monthly Ridership at {station_name} Station for {year}"
        data_plot(x, y, x_label, y_label, title)
    else:
        return
# command 8: compares two stations and outputs a portion of the total daily ridership
def compare_stations(dbConn):
    dbCursor = dbConn.cursor()
    user_year = input("\nYear to compare against? ")
    station_one = input("\nEnter station 1 (wildcards _ and %): ")
    output = check_stations_input(dbConn, station_one)
    if output == False: 
        return
    station_one_name = output[0][0]
    station_two = input("\nEnter station 2 (wildcards _ and %): ")
    output = check_stations_input(dbConn, station_two)
    if output == False: 
        return
    station_two_name = output[0][0]
    # returns the total ridership of every single day at every station 
    sql = """
            SELECT strftime('%Y-%m-%d', Ride_Date) as Date, SUM(Num_Riders) as Riders, Stations.Station_ID
            FROM Stations
            JOIN Ridership
            ON Stations.Station_ID = Ridership.Station_ID
            WHERE Station_Name LIKE ?
            AND strftime('%Y', Ride_Date) LIKE ?
            GROUP BY Date
            ORDER BY Date ASC;
    """
    
    dbCursor.execute(sql, [station_one_name, user_year])
    station_one_res = dbCursor.fetchall()
    
    print(f"Station 1: {station_one_res[0][2]} {station_one_name}")
    for i in range(len(station_one_res)):
        if i < 5 or i >= len(station_one_res) - 5:
            date, ridership, _ = station_one_res[i]
            print(date, ridership)

    dbCursor.execute(sql, [station_two_name, user_year])
    station_two_res = dbCursor.fetchall()
    
    print(f"Station 2: {station_two_res[0][2]} {station_two_name}")
    for i in range(len(station_two_res)):
        if i < 5 or i >= len(station_two_res) - 5:
            date, ridership, _ = station_two_res[i]
            print(date, ridership)

    plot_ans = input("\nPlot? (y/n) ")
    if plot_ans == "y":
        dbCursor.execute(sql, [station_one_name, user_year])
        station_one_data = dbCursor.fetchall()
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        day_counter = 1
        for row in station_one_data:
            _, ridership, _  = row
            x1.append(day_counter)
            y1.append(ridership)
            day_counter += 1
        # print(x1, y1)
        dbCursor.execute(sql, [station_two_name, user_year])
        station_two_data = dbCursor.fetchall()
        day_counter_2 = 1
        for row in station_two_data:
            _, ridership, _  = row
            x2.append(day_counter_2)
            y2.append(ridership)
            day_counter_2 += 1
        x_label = "Day"
        y_label = "Number of Riders"
        title = f"Ridership Each Day of {user_year}"
        plotting_two_stations(x1, y1, x2, y2, x_label, y_label, title, station_one_name, station_two_name)
    else:
        return
# helper function to plot two data sets takes in the necessary values needed
def plotting_two_stations(x1, y1, x2, y2, x_label, y_label, title, station_one, station_two):
    figure.xlabel(x_label)
    figure.ylabel(y_label)
    figure.title(title)
    figure.ioff()
    figure.plot(x1,y1, label=station_one)
    figure.plot(x2,y2, label=station_two)
    figure.show()
        
#  checking my input to make sure it does crash due to user inputting something other than a int
def check_input_before_convert(user_input):
    try: 
        res = float(user_input)
        return res
    except Exception as err:
        return False
    finally:
        pass

# command 9: takes in values for latitude & longitude and finds all stations within a mile radius
# plots the result as well if the user selects to do so 
def stations_within_mile(dbConn):
    # between 40-43 degrees
    latitude = input("\nEnter a latitude: ")
    lat_res = check_input_before_convert(latitude)
    if lat_res == False:
        return
    if  not (40 <= lat_res <= 43):
        print("**Latitude entered is out of bounds...")
        return
    # between -87 and -86
    longitude = input("Enter a longitude: ")
    long_res = check_input_before_convert(longitude)
    if long_res == False:
        return
    if not (-88 <= long_res <= -87):
        print("**Longitude entered is out of bounds...")
        return
    dbCursor = dbConn.cursor()
    lat_bound = 1 / 69
    long_bound = 1 / 51
    upper_bound = round(long_res + long_bound, 3)
    lower_bound = round(long_res - long_bound, 3)
    left_bound = round(lat_res - lat_bound, 3)
    right_bound = round(lat_res + lat_bound, 3)
    
    # list of stations within a mile given the station is within the bounds of the 
    # latitude and longitude
    sql = """
        SELECT DISTINCT Station_Name, Latitude, Longitude
        FROM Stations
        JOIN Stops
        ON Stations.Station_ID = Stops.Station_ID
        WHERE (Latitude >= ? AND Latitude <= ?) 
        AND (Longitude >= ? AND Longitude <= ?)
        ORDER BY Station_Name ASC;
    """
    dbCursor.execute(sql, [left_bound, right_bound, lower_bound, upper_bound])
    res = dbCursor.fetchall()
    
    if not res:
        print("**No stations found...")
        return
    print("\nList of Stations Within a Mile")
    for row in res:
        station, lat, long = row
        print(f"{station} : ({lat}, {long})")
        
    plot_input = input("\nPlot? (y/n) ")
    if plot_input == "y":
        x = []
        y = []
        image = figure.imread("datafiles/chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
        figure.imshow(image, extent=xydims)
        figure.title("Stations Near You")
        figure.xlim([-87.9277, -87.5569])
        figure.ylim([41.7012, 42.0868])

        for row in res:
            station, lat, long = row
            figure.annotate(station, (long, lat))
            x.append(long)
            y.append(lat)
        figure.plot(x,y)
        figure.show()
    else:
        return   
# starts the program 
initalize_program()