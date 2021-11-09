# This program is used to compare NBA player's average stats to calculate the percentage of improvement between 2 or more players
# Originally I use this to help me updating my Fantasy NBA roster

# TODO:
# - Set year dynamically

import urllib.request, json
from datetime import date
import csv
import xlsxwriter

today = date.today()
print("Collecting all player based on today's ({0}) data...".format(today))

playerDataUrl = "https://data.nba.net/10s/prod/v1/2021/players.json"
playerStatsUrl = "https://data.nba.net/data/10s/prod/v1/2021/players/{0}_profile.json"
playerDataJSON = {}

with urllib.request.urlopen(playerDataUrl) as url:
	playerDataJSON = json.loads(url.read().decode())


def loadPlayerStats(firstName, lastName):
	print("Finding player data...")
	playerStatsJSON = {}
	playerID = -1

	for playerData in playerDataJSON['league']['standard']:
		if(playerData['firstName'].lower() == firstName and playerData['lastName'].lower() == lastName):
			playerID = playerData['personId']
			break

	if(playerID == -1):
		print("No player found!")
		return {}

	with urllib.request.urlopen(playerStatsUrl.format(playerID)) as url:
		playerStatsJSON = json.loads(url.read().decode())

	if 'league' not in playerStatsJSON:
		print("Stats not found!")
		return {}

	playerStats = playerStatsJSON['league']['standard']['stats']['latest']
	compiledStats = {
		'ID': playerID,
		'firstName': firstName,
		'lastName': lastName,
		'ppg': float(playerStats['ppg']),
		'rpg': float(playerStats['rpg']),
		'apg': float(playerStats['apg']),
		'spg': float(playerStats['spg']),
		'bpg': float(playerStats['bpg']),
		'topg': float(playerStats['topg']),
		'fgp': float(playerStats['fgp']),
		'ftp': float(playerStats['ftp']),
		'3pm': float(float(playerStats['tpm']) / float(playerStats['gamesPlayed'])) 
	}

	for i in compiledStats:
		if type(compiledStats[i]) == float and compiledStats[i] <= 0.0:
			compiledStats[i] += 0.1

	return compiledStats

def comparePlayer(player1, player2):
	percentages = []
	percentages.append(round((player2['ppg'] / player1['ppg'] * 100) - 100, 2))
	percentages.append(round((player2['rpg'] / player1['rpg'] * 100) - 100, 2))
	percentages.append(round((player2['apg'] / player1['apg'] * 100) - 100, 2))
	percentages.append(round((player2['spg'] / player1['spg'] * 100) - 100, 2))
	percentages.append(round((player2['bpg'] / player1['bpg'] * 100) - 100, 2))
	percentages.append(round((player1['topg'] / player2['topg'] * 100) - 100, 2))
	percentages.append(round((player2['fgp'] / player1['fgp'] * 100) - 100, 2))
	percentages.append(round((player2['ftp'] / player1['ftp'] * 100) - 100, 2))
	percentages.append(round((player2['3pm'] / player1['3pm'] * 100) - 100, 2))
	average = round(sum(percentages[:9]) / 9, 2)
	betterCatCount = sum([1 for i in percentages if i > 0])

	percentages.append(betterCatCount)
	percentages.append(average)
	return percentages

def main():
	mainPlayerName = input("Enter player full name: ")
	mainPlayerNameFmt = mainPlayerName.lower().split(" ")
	mainPlayerStats = loadPlayerStats(mainPlayerNameFmt[0], ' '.join(mainPlayerNameFmt[1:]))
	if 'ppg' not in mainPlayerStats:
		exit()

	print("{0}'s stats PPG: {1}, RPG: {2}, APG: {3}, FG%: {4}, FT%: {5}, etc..".format(mainPlayerName, mainPlayerStats['ppg'], mainPlayerStats['rpg'], mainPlayerStats['apg'], mainPlayerStats['fgp'], mainPlayerStats['ftp']))

	isToCompare = True
	comparedPlayerName = []
	comparedPlayerStats = []
	improvementRate = []

	cpName = input("Enter player to compare full name: ")

	while(isToCompare):
		cpNameFmt = cpName.lower().split(" ")

		cpStats = loadPlayerStats(cpNameFmt[0], ' '.join(cpNameFmt[1:]))
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

				for i in ['Player Name', 'Point per Game', 'Rebound per Game', 'Assist per Game', 'Field Goal %', 'Free Throw %', 'Turnover per Game', 'Steal per Game', 'Block per Game', '3PT per Game', 'Better/Worse Percentage', 'Better categories count']:
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


