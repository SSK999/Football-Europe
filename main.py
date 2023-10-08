infomsg = "Y"
filepath = "D:/Football/"
dohistory = "N"

#Step 00 declare pandas library
if infomsg == "Y":  print('Step 00')

import pandas as pd
import os

def proc_country(v_country,v_mode):
    # Step 01 Read in Football Config file
    if infomsg == "Y":  print('Step 01')
    df = pd.read_csv(filepath + v_country + ' Football Config.csv')
    if infomsg == "Y":  print(df)

    # Step 02 only Process Current Season
    if infomsg == "Y":  print('Step 02')
    if v_mode == 'Current':
        cond1 = df["Current Season"] == "Y"
    else:
        cond1 = df["Current Season"] != "Y"

    df = df[cond1]

    # Step 03 Read in Season Header file
    if infomsg == "Y":  print('Step 03')
    Season_Header = pd.read_csv(filepath + 'SeasonHeader1.csv')
    if infomsg == "Y":  print(Season_Header)

    # Step 04 Create working_df
    if infomsg == "Y":  print('Step 04')
    # Initialise
    intial_df = Season_Header
    working_df = intial_df

    # Process each row from Football Config file using a for loop
    for rowname in df.index:
        row = df.loc[rowname]
        print('Processing: ',row['League'], row['Season'], row['Level'], row['Season_ID'], row['DivName'])

        # season 2000-2001 will generate season_id of 1 not 0001
        # seasons after 2000-2001 will generate three character season_ids so add a leding space
        if row['Season_ID'] == 1:
            df1url = 'https://www.football-data.co.uk/mmz4281/0001/' \
                     + row['Level'] + ".csv"
        elif row['Season_ID'] < 1000:
            df1url = 'https://www.football-data.co.uk/mmz4281/0' + row['Season_ID'].astype(str) + '/' \
                     + row['Level'] + ".csv"
        else:
            df1url = 'https://www.football-data.co.uk/mmz4281/' + row['Season_ID'].astype(str) + '/' \
                     + row['Level'] + ".csv"

        if infomsg == "Y":  print(df1url)
#        df1 = pd.read_csv(df1url, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8], parse_dates=['Date'], infer_datetime_format=True)
        df1 = pd.read_csv(df1url, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8], parse_dates=['Date'], encoding='cp1252' )
        df1 = df1.dropna(how='all').dropna(axis=1, how='all')
        df1.insert(1, column='DivName', value=row['DivName'])
        df1.insert(1, column='Season', value=row['Season'])
        df1.insert(1, column='League', value=row['League'])
        working_df = pd.concat(objs=[working_df, df1])

    # Step 05 Check shape
    if infomsg == "Y":
        print('Step 05')
        print(working_df.shape)

    # Step 06 Check info
    if infomsg == "Y":
        print('Step 06')
        working_df.info()

    # Step 07 Check counts
    if infomsg == "Y":
        print('Step 07')
        print(working_df["Season"].value_counts().sort_values())

    # Step 10  Create MatchesIn
    if infomsg == "Y":  print('Step 10')
    cols = ["League", "Div", "Season", "DivName", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
    MatchesIn = working_df[cols]

    # Step 11 Create MatchesHome
    if infomsg == "Y":  print('Step 11')
    cols = ["League", "Div", "Season", "DivName", "Date", "HomeTeam", "FTHG", "FTAG"]
    MatchesHome = MatchesIn[cols]

    # Step 12 Rename MatchesHome columns
    if infomsg == "Y":  print('Step 12')
    MatchesHome = MatchesHome.rename(columns={'HomeTeam': 'Team', 'FTHG': 'GF', 'FTAG': 'GA'})

    # Step 13 Create MatchesAway
    if infomsg == "Y":  print('Step 13')
    cols2 = ["League", "Div", "Season", "DivName", "Date", "AwayTeam", "FTAG", "FTHG"]
    MatchesAway = MatchesIn[cols2]

    # Step 14 Rename MatchesAway columns
    if infomsg == "Y":  print('Step 14')
    MatchesAway = MatchesAway.rename(columns={'AwayTeam': 'Team', 'FTAG': 'GF', 'FTHG': 'GA'})

    # Step 15 Merge MatchesHome,MatchesAway into MatchesMerged
    if infomsg == "Y":  print('Step 15')
    MatchesMerged = pd.concat(objs=[MatchesHome, MatchesAway])

    # Step 17 Calculate Goal Difference from GF and GA
    if infomsg == "Y":  print('Step 17')
    MatchesMerged["GD"] = MatchesMerged["GF"] - MatchesMerged["GA"]

    # Step 23 drop any rows with non numeric values in ['GF','GA','GD']
    if infomsg == "Y":  print('Step 23')
    MatchesMerged = MatchesMerged.dropna(subset=['GF', 'GA', 'GD'])
    MatchesMerged

    # Step 25 use this option to stop getting warning about updating dataframes inplace.
    if infomsg == "Y":  print('Step 24')
    pd.options.mode.chained_assignment = None

    # Step 26 Set datatypes to save space/memory
    if infomsg == "Y":  print('Step 26')
    MatchesMerged["League"] = MatchesMerged["League"].astype("category")
    MatchesMerged["Div"] = MatchesMerged["Div"].astype("category")
    MatchesMerged["Season"] = MatchesMerged["Season"].astype("category")
    MatchesMerged["DivName"] = MatchesMerged["DivName"].astype("category")
    MatchesMerged["Team"] = MatchesMerged["Team"].astype("category")
    MatchesMerged["GF"] = MatchesMerged["GF"].astype("int")
    MatchesMerged["GA"] = MatchesMerged["GA"].astype("int")
    MatchesMerged["GD"] = MatchesMerged["GD"].astype("int")

    # Step 28 select matches that were won set Win/Draw/Loss/Points
    if infomsg == "Y":  print('Step 28')
    MatchesWon = MatchesMerged.query("GF > GA")
    MatchesWon["Played"] = 1
    MatchesWon["Win"] = 1
    MatchesWon["Draw"] = 0
    MatchesWon["Loss"] = 0
    MatchesWon["Points"] = 3
    # MatchesWon

    # Step 29 select matches that were drawn set Win/Draw/Loss/Points
    if infomsg == "Y":  print('Step 29')
    MatchesDraw = MatchesMerged.query("GF == GA")
    MatchesDraw["Played"] = 1
    MatchesDraw["Win"] = 0
    MatchesDraw["Draw"] = 1
    MatchesDraw["Loss"] = 0
    MatchesDraw["Points"] = 1
    # MatchesDraw

    # Step 30 select matches that were lost set Win/Draw/Loss/Points
    if infomsg == "Y":  print('Step 30')
    MatchesLoss = MatchesMerged.query("GF < GA")
    MatchesLoss["Played"] = 1
    MatchesLoss["Win"] = 0
    MatchesLoss["Draw"] = 0
    MatchesLoss["Loss"] = 1
    MatchesLoss["Points"] = 0
    # MatchesLoss

    # Step 31 Merge won/drawn/lost matches
    if infomsg == "Y":  print('Step 31')
    AllMatches = pd.concat([MatchesWon, MatchesDraw, MatchesLoss])
    AllMatches.dropna(how="any")
    AllMatches
    if infomsg == "Y":  print(AllMatches.info())

    # Step 32 write Summary_df.to_csv
    if infomsg == "Y":  print('Step 32')
    #AllMatches.to_csv(filepath + v_country + '_AllMatches_df.csv', index=False)

    # Step 33 Define Aggregation level to sum up GF,GA,GD...
    if infomsg == "Y":  print('Step 33')
    grouped_df = AllMatches.groupby(["League", "Season", "DivName", "Team"])
    # grouped_df.to_csv("D:/pyfiles/Greece_grouped_df.csv",index=False) AttributeError: 'DataFrameGroupBy' object has no attribute 'to_csv'
    # grouped_df

    # Step 34 Aggregate (sum up)  GF,GA,GD...
    if infomsg == "Y":  print('Step 34')

    Summary_df = grouped_df.sum(['GF', 'GA', 'GD', 'Played', 'Win', 'Draw', 'Loss', 'Points'])
    # Summary_df

    # Step 35 Sort Data by "Season" asc,"DivName" asc,"Points" desc,"GD" desc
    if infomsg == "Y":  print('Step 35')
    Summary_df = Summary_df.sort_values(by=["Season", "DivName", "Points", "GD"], ascending=[True, True, False, False])
    # Summary_df

    # Step 36 write Summary_df.to_csv
    if infomsg == "Y":  print('Step 36')
    Summary_df.to_csv(filepath + v_country + '_Summary_df.csv', index=True)

    # Step 37 read Summary_df.to_csv back to remove grouping and calculate position
    if infomsg == "Y":  print('Step 37')
    Summary_df = pd.read_csv(filepath + v_country + '_Summary_df.csv')
    # Summary_df

    os.remove(filepath + v_country + '_Summary_df.csv')

    # Step 38 rename 'DivName' to 'Division'
    if infomsg == "Y":  print('Step 38')
    Summary_df.rename(columns={'DivName': 'Division'}, inplace=True)
    # Summary_df

    # Step 39 Create Divkey from 'League	Season	Division'
    if infomsg == "Y":  print('Step 39')
    Summary_df.insert(3, column='DivKey', value=Summary_df["League"] + Summary_df["Season"] + Summary_df["Division"])

    # Summary_df

    # Step 40 Define a function to calculate position and apply in to Summary_df
    def calculate_position(data):
        """
        Calculates position based on points, goals scored and goal difference.
        """
        data['Position'] = (data.sort_values(['Points', 'GD', 'GF'], ascending=False)
                            .groupby('DivKey')
                            .cumcount() + 1)
        return data

    # Step 41 Apply the function to the dataframe
    if infomsg == "Y":  print('Step 41')
    df1 = Summary_df.groupby('DivKey').apply(calculate_position).reset_index(drop=True)
    # Print the resulting dataframe
    Summary_df = df1

    # Step 43 write Summary_df.to_csv
    if infomsg == "Y":  print('Step 43')

    if v_mode == 'Current':
        filename = filepath + v_country + '_Current_df.csv'
    else:
        filename = filepath + v_country + '_Historic_df.csv'
    Summary_df.to_csv(filename, index=False)

#######################################################################################
###
###   Main Program
###
#######################################################################################

Country_List = ['Belgium','England','France','Germany','Greece','Italy','Netherlands' \
                ,'Portugal','Scotland','Spain','Turkey']

if dohistory == "Y":

# Load all previous seasons
    for country in Country_List:
        print('Processing ' + country)
        proc_country(country,'Historic')

# Merge all countries - previous seasons
    df_historic = pd.DataFrame()
    for country in Country_List:
        filename = filepath + country + '_Historic_df.csv'
        print('Merging ' + filename)
        df = pd.read_csv(filename)
        df_historic = pd.concat([df_historic,df])
    df_historic.to_csv(filepath + 'Historic_df.csv', index=False)

# Load all Current seasons
for country in Country_List:
    print('Processing ' + country)
    proc_country(country,'Current')

# Merge all countries - current  seasons
df_current = pd.DataFrame()
for country in Country_List:
    filename = filepath + country + '_Current_df.csv'
    print('Merging ' + filename)
    df = pd.read_csv(filename)
    df_current = pd.concat([df_current,df])

df_current.to_csv(filepath + 'Current_df.csv', index=False)

df_historic = pd.read_csv(filepath + 'Historic_df.csv')
df_all_leagues = pd.concat([df_current,df_historic])
df_all_leagues.to_csv(filepath + 'all_leagues.csv', index=False)




