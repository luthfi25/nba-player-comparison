# This program is used to compare NBA player's average stats to calculate the percentage of improvement between 2 or more players
# Originally I use this to help me updating my Fantasy NBA roster

# TODO:
# - Set year dynamically

# import urllib.request, json
from datetime import date
import xlsxwriter
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd
import math

today = date.today()
print("Collecting all player based on today's ({0}) data...".format(today))

# playerDataUrl = "https://data.nba.net/10s/prod/v1/2021/players.json"
# playerStatsUrl = "https://data.nba.net/data/10s/prod/v1/2021/players/{0}_profile.json"
# playerDataJSON = {}

# with urllib.request.urlopen(playerDataUrl) as url:
# 	playerDataJSON = json.loads(url.read().decode())


def loadPlayerStats(mainPlayerName):
	print("Finding player data...")
	# playerStatsJSON = {}
	# playerID = -1

	# for playerData in playerDataJSON['league']['standard']:
	# 	if(playerData['firstName'].lower() == firstName and playerData['lastName'].lower() == lastName):
	# 		playerID = playerData['personId']
	# 		break

	# new implementation using nba_api
	player_dict = players.get_players()
	player = [player for player in player_dict if str(player['full_name']).lower() == mainPlayerName]
	player_id = player[0]['id']

	gamelog_player = playergamelog.PlayerGameLog(player_id=player_id, season='2021')
	df_player_games = gamelog_player.get_data_frames()[0]
	# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
	# 	print(df_player_games)

	if(player_id == -1):
		print("No player found!")
		return {}
	elif len(df_player_games) == 0:
		print("No games played yet!")
		return {}

	# with urllib.request.urlopen(playerStatsUrl.format(playerID)) as url:
	# 	playerStatsJSON = json.loads(url.read().decode())

	# if 'league' not in playerStatsJSON:
	# 	print("Stats not found!")
	# 	return {}

	# playerStats = playerStatsJSON['league']['standard']['stats']['latest']

	#calculate stats from last 5 games
	df_last_5_games = df_player_games.head(5)
	# print(df_last_5_games)

	compiledStats = {
		'playerName': mainPlayerName,
		'ppg': df_last_5_games["PTS"].mean(),
		'rpg': df_last_5_games["REB"].mean(),
		'apg': df_last_5_games["AST"].mean(),
		'spg': df_last_5_games["STL"].mean(),
		'bpg': df_last_5_games["BLK"].mean(),
		'topg': df_last_5_games["TOV"].mean(),
		'fgp': float(df_last_5_games["FGM"].sum() / df_last_5_games["FGA"].sum()),
		'ftp': float(df_last_5_games["FTM"].sum() / df_last_5_games["FTA"].sum()),
		'3pm': df_last_5_games["FG3M"].mean() 
	}

	# for i in compiledStats:
	# 	if type(compiledStats[i]) == float and compiledStats[i] <= 0.0:
	# 		compiledStats[i] += 0.1

	return compiledStats

def comparePlayer(player1, player2):
	percentages = []
	percentages.append(round((player2['ppg'] / (player2['ppg'] + player1['ppg']) * 100) - 50, 2))
	percentages.append(round((player2['rpg'] / (player2['rpg'] + player1['rpg']) * 100) - 50, 2))
	percentages.append(round((player2['apg'] / (player2['apg'] + player1['apg']) * 100) - 50, 2))
	percentages.append(round((player2['bpg'] / (player2['bpg'] + player1['bpg']) * 100) - 50, 2))
	percentages.append(round((player2['spg'] / (player2['spg'] + player1['spg']) * 100) - 50, 2))
	percentages.append(round((player1['topg'] / (player2['topg'] + player1['topg']) * 100) - 50, 2))
	percentages.append(round((player2['3pm'] / (player2['3pm'] + player1['3pm']) * 100) - 50, 2))

	if math.isnan(player1['fgp']) or math.isnan(player2['fgp']):
		percentages.append(0)
	else:
		percentages.append(round((player2['fgp'] / (player2['fgp'] + player1['fgp']) * 100) - 50, 2))
	
	if math.isnan(player1['ftp']) or math.isnan(player2['ftp']):
		percentages.append(0)
	else:
		percentages.append(round((player2['ftp'] / (player2['ftp'] + player1['ftp']) * 100) - 50, 2))


	average = round(sum(percentages[:9]) / 9, 2)
	print(percentages)
	
	betterCatCount = sum([1 for i in percentages if i > 0])

	percentages.append(betterCatCount)
	percentages.append(average)
	return percentages

def main():
	mainPlayerName = input("Enter player full name: ")
	# mainPlayerNameFmt = mainPlayerName.lower().split(" ")
	mainPlayerStats = loadPlayerStats(mainPlayerName.lower())
	
	if 'ppg' not in mainPlayerStats:
		exit()

	print("{0}'s stats PPG: {1}, RPG: {2}, APG: {3}, FG%: {4}, FT%: {5}, etc..".format(mainPlayerName, mainPlayerStats['ppg'], mainPlayerStats['rpg'], mainPlayerStats['apg'], mainPlayerStats['fgp'], mainPlayerStats['ftp']))

	isToCompare = True
	comparedPlayerName = []
	comparedPlayerStats = []
	improvementRate = []

	cpName = input("Enter player to compare full name: ")

	while(isToCompare):
		cpStats = loadPlayerStats(cpName.lower())

		if 'ppg' in cpStats:
			comparedPlayerName.append(cpName)
			comparedPlayerStats.append(cpStats)
			print("{0}'s stats PPG: {1}, RPG: {2}, APG: {3}, FG%: {4}, FT%: {5}, etc..".format(cpName, cpStats['ppg'], cpStats['rpg'], cpStats['apg'], cpStats['fgp'], cpStats['ftp']))

			improvement = comparePlayer(mainPlayerStats, cpStats)
			if improvement[-1] > 0:
				print("{0} is approximately {1}% better in {2} categories than {3}, get him now!".format(cpName, improvement[-1], improvement[-2], mainPlayerName))
			else:
				print("{0} is approximately {1}% worse in {2} categories than {3}, don't get him!".format(cpName, improvement[-1], 9-improvement[-2], mainPlayerName))

			improvementRate.append(improvement)

		cpName = input("Input other player's name or N to stop: ")
		if cpName == "N":
			isToCompare = False
			isExcel = input("Print to Excel? (Y/N) ")

			if isExcel == "Y":
				workbook = xlsxwriter.Workbook('{0} Comparison.xlsx'.format(mainPlayerName))
				worksheet = workbook.add_worksheet("Comparison Sheet")
				row = 0
				column = 0

				for i in ['Player Name', 'Point per Game', 'Rebound per Game', 'Assist per Game', 'Turnover per Game', 'Steal per Game', 'Block per Game', '3PT per Game', 'Field Goal %', 'Free Throw %', 'Better/Worse Percentage', 'Better categories count']:
					worksheet.write(row, column, i)
					column += 1
				
				column = 0
				row += 1

				for i in [mainPlayerName, mainPlayerStats['ppg'], mainPlayerStats['rpg'], mainPlayerStats['apg'], mainPlayerStats['fgp'], mainPlayerStats['ftp'], mainPlayerStats['topg'], mainPlayerStats['spg'], mainPlayerStats['bpg'],mainPlayerStats['3pm'],0.0, 0]:
					worksheet.write(row, column, i)
					column += 1

				column = 0
				row += 1

				for i in range(len(comparedPlayerName)):
					for j in [comparedPlayerName[i], comparedPlayerStats[i]['ppg'], comparedPlayerStats[i]['rpg'], comparedPlayerStats[i]['apg'], comparedPlayerStats[i]['fgp'], comparedPlayerStats[i]['ftp'], comparedPlayerStats[i]['topg'], comparedPlayerStats[i]['spg'], comparedPlayerStats[i]['bpg'],comparedPlayerStats[i]['3pm'], improvementRate[i][-1], improvementRate[i][-2]]:
						worksheet.write(row, column, j)
						column += 1
					column = 0
					row += 1

				workbook.close()
				print("Excel printed!")
			
			print("Happy fantasy balling!")

main()


