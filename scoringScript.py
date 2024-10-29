import requests
import statsapi

class AltPlayer:
   def __init__(self, name, points):
       self.name = name
       self.points = points




class Game:
   def __init__(self, points, played, gameId):
       self.points = points
       self.played = played
       self.gameId = gameId




class Player:
   def __init__(self, fullName, boxscoreName, id, position, team, games, seriesPoints):
       self.fullName = fullName
       self.boxscoreName = boxscoreName
       self.id = id
       self.position = position
       self.team = team
       self.games = games
       # Necessary? Could sum up gamePoints
       self.seriesPoints = seriesPoints




class GameResult:
   def __init__(self, win, points):
       self.win = win
       self.points = points




class SkeletonRoster:
   def __init__(self, playerIds):
       self.playerIds = playerIds




class PopulatedRoster:
   def __init__(self, players):
       self.players = players




class Manager:
   def __init__(self, name, totalPoints, gameResults, roster):
       self.name = name
       self.points = totalPoints
       self.gameResults = gameResults
       self.roster = roster




def getAdditionalPlayerStats(gameInfo, playerBoxscoreName):
   errorCount = 0
   caughtStealingCount = 0
   for infoObject in gameInfo:
       if infoObject.get("title") == "FIELDING":
           for object in infoObject.get("fieldList"):
               if object.get("label") == "E":
                   for entry in object.get("value").split(";"):
                       if playerBoxscoreName in entry:
                           playerSplitText = entry.split("(")[0]
                           try:
                               errorCount = int(playerSplitText[-1])
                           except ValueError:
                               # When only one error is committed, no number is returned, so add one
                               errorCount = 1


       elif infoObject.get("title") == "BASERUNNING":
           for object in infoObject.get("fieldList"):
               if object.get("label") == "CS":
                   for entry in object.get("value").split(";"):
                       if playerBoxscoreName in entry:
                           playerSplitText = entry.split("(")[0]
                           try:
                               caughtStealingCount = int(playerSplitText[-1])
                           except ValueError:
                               # When a player is only caught stealing once, no number is returned, so add one
                               caughtStealingCount = 1


   return errorCount, caughtStealingCount




# Get stats for an individual batter
def getBattingStats(
   playerStatsFromService,
   managerName: str,
   playerFromManagerRoster,
   gameInfo,
   isAlternate=False,
):
   playerTeam = playerFromManagerRoster.team
   playerFullName = playerFromManagerRoster.fullName
   errors, caughtStealing = getAdditionalPlayerStats(
       gameInfo=gameInfo, playerBoxscoreName=playerFromManagerRoster.boxscoreName
   )


   battingStats = playerStatsFromService.get("stats").get("batting")
   doubles = int(battingStats.get("doubles"))
   triples = int(battingStats.get("triples"))
   homeRuns = int(battingStats.get("homeRuns"))
   # No details on singles, so hits less everything else...
   hits = int(battingStats.get("hits"))
   singles = hits - doubles - triples - homeRuns
   runs = int(battingStats.get("runs"))
   rbi = int(battingStats.get("rbi"))
   stolenBase = int(battingStats.get("stolenBases"))
   walks = int(battingStats.get("baseOnBalls"))
   nameText = ""
   if isAlternate:
       nameText = (
           playerFullName
           + " ("
           + managerName
           + " ** Alternate ** "
           + playerTeam
           + " Batter)"
       )
   else:
       nameText = (
           playerFullName + " (" + managerName + " -- " + playerTeam + " Batter)"
       )
   print(nameText)
   # 1 point/single
   # 2 points/double
   # 3 points/triple
   # 4 points/HR
   # 1 point/run scored
   # 1 point/RBI
   # 2 points/stolen base
   # 1 point/walk (does not include HBP)
   # -1 point/error
   # -1 point/caught stealing
   pointsScored = (
       singles
       + 2 * doubles
       + 3 * triples
       + 4 * homeRuns
       + runs
       + rbi
       + 2 * stolenBase
       + walks
       - errors
       - caughtStealing
   ) * 1.0
   print(
       str(pointsScored)
       + " points via "
       + str(singles)
       + " S, "
       + str(doubles)
       + " D, "
       + str(triples)
       + " T, "
       + str(homeRuns)
       + " HR, plus "
       + str(rbi)
       + " RBIs, "
       + str(runs)
       + " R, "
       + str(stolenBase)
       + " SB, "
       + str(walks)
       + " BB, minus "
       + str(errors)
       + " E, "
       + str(caughtStealing)
       + " CS"
   )
   print()
   return pointsScored




# Get stats for an individual pitcher
def getPitchingStats(playerStatsFromService, managerName: str, playerFromManagerRoster):
   playerTeam = playerFromManagerRoster.team
   playerFullName = playerFromManagerRoster.fullName
   pitchingStats = playerStatsFromService.get("stats").get("pitching")
   note = str(pitchingStats.get("note"))
   noteText = "No decision"
   decision = 0
   if "(W" in note:
       decision = 4
       noteText = "Win"
   elif "(L" in note:
       decision = -2
       noteText = "Loss"
   elif "(S" in note:
       decision = 3
       noteText = "Save"
   elif "(H" in note:
       decision = 1
       noteText = "Hold"
   elif "(BS" in note:
       decision = -4
       noteText = "Blown Save"
   innings = float(pitchingStats.get("inningsPitched"))
   earnedRuns = float(pitchingStats.get("earnedRuns"))
   strikeouts = int(pitchingStats.get("strikeOuts"))
   nameText = playerFullName + " (" + managerName + " -- " + playerTeam + " Pitcher)"
   print(nameText)
   # 4 point/win
   # -2 points/loss
   # 3 points/save
   # 1 points/hold
   # -4 points/blown save
   # 1 point/inning
   # -1 points/earned run
   # 1 point/strikeout
   pointsScored = decision + innings - earnedRuns + 0.5 * strikeouts
   print(
       str(pointsScored)
       + " points via "
       + noteText
       + ", "
       + str(innings)
       + " IP, "
       + str(earnedRuns)
       + " ER, "
       + str(strikeouts)
       + " K"
   )
   print()
   return pointsScored




def pitchingStatsPerManager(manager, gameId, teamData):
   managerPitchers = manager.roster
   managerPitcherPoints = 0.0


   gamePitchers = teamData.get("players")


   for index, orderedRoster in enumerate(managerPitchers.players):
       pitcherID = "ID" + str(orderedRoster.id)
       pitcherDetails = gamePitchers.get(pitcherID)
       if pitcherDetails and pitcherDetails.get("stats").get("pitching"):
           pitcherPoints = getPitchingStats(
               playerStatsFromService=pitcherDetails,
               managerName=manager.name,
               playerFromManagerRoster=orderedRoster,
           )
           managerPitcherPoints += pitcherPoints
           managerPitchers.players[index].games.append(
               Game(points=pitcherPoints, played=True, gameId=gameId)
           )
           managerPitchers.players[index].seriesPoints += pitcherPoints


   return managerPitcherPoints




def batterStatsPerManager(manager, gameId, teamData):
   managerRoster = manager.roster
   managerBatterPoints = 0.0
   managerPlayersUsed = 0


   gameBatters = teamData.get("players")
   # Errors and Caught Stealing live in the "info" block
   gameInfo = teamData.get("info")


   for index, orderedRoster in enumerate(managerRoster.players):
       batterID = "ID" + str(orderedRoster.id)
       batterDetails = gameBatters.get(batterID)
       if (
           managerPlayersUsed < 4
           and batterDetails
           and batterDetails.get("stats").get("batting")
       ):
           batterPoints = getBattingStats(
               playerStatsFromService=batterDetails,
               managerName=manager.name,
               playerFromManagerRoster=orderedRoster,
               gameInfo=gameInfo,
           )
           managerBatterPoints += batterPoints
           managerRoster.players[index].games.append(
               Game(points=batterPoints, played=True, gameId=gameId)
           )
           managerRoster.players[index].seriesPoints += batterPoints
           managerPlayersUsed += 1


   return managerBatterPoints




def detailedGameOutput(manager, gameNumber, games):
   playerList = []
   for player in manager.roster.players:
       for game in player.games:
           if game.gameId == games[gameNumber - 1]:
               playerList.append(tuple([game.points, player.fullName]))


   topPerformers = sorted(playerList, key=lambda x: x[0], reverse=True)
   print("Game Top Performers:")
   for player in topPerformers[:3]:
       print(player[1] + " scored " + str(player[0]))


   print()
   print("Game Worst Performers:")
   for player in topPerformers[-3:]:
       print(player[1] + " scored " + str(player[0]))




# Print out the Game outcome including winner and points
def generateGameOutput(managerList, gameNumber, games):
   gameIsValid = False
   for manager in managerList:
       game = manager.gameResults[-1]
       if game.win:


           otherManagers = [x for x in managerList if x != manager]
           gameIsValid = game.points > 0


           if gameIsValid:
               print()
               print(
                   "********************* Game "
                   + str(gameNumber)
                   + " Summary ***********************"
               )
               print()


               print(manager.name + " wins with " + str(game.points) + " points")
               detailedGameOutput(manager=manager, gameNumber=gameNumber, games=games)
               print()


               for losingManager in otherManagers:
                   print(
                       losingManager.name
                       + " scored "
                       + str(losingManager.gameResults[-1].points)
                       + " points"
                   )
                   detailedGameOutput(
                       manager=losingManager, gameNumber=gameNumber, games=games
                   )


               generateSeriesOutput(
                   managerList=managerList, gameNumber=gameNumber, games=games
               )




def generateSeriesOutput(managerList, gameNumber, games):
   print()
   print("********************* Series Update ***********************")
   print()


   # region Winning Managers
   winningManager = max(managerList, key=lambda x: x.points)
   seriesUpdateString = " leads with " + str(winningManager.points) + " points"
   if gameNumber == int(len(games)):
       seriesUpdateString = " wins with " + str(winningManager.points) + " points"


   print(winningManager.name + seriesUpdateString)
   print("Series Top Performers:")


   topPerformers = sorted(
       winningManager.roster.players, key=lambda x: x.seriesPoints, reverse=True
   )
   for player in topPerformers[:3]:
       print(player.fullName + " scored " + str(player.seriesPoints))
   print()
   print("Series Worst Performers:")
   for player in topPerformers[-3:]:
       print(player.fullName + " scored " + str(player.seriesPoints))
   # endregion


   print()


   # region Losing Managers
   otherManagers = [x for x in managerList if x != winningManager]
   for losingManager in otherManagers:
       seriesUpdateString = " trails with " + str(losingManager.points) + " points"
       if gameNumber == int(len(games)):
           seriesUpdateString = " loses with " + str(losingManager.points) + " points"
       print(losingManager.name + seriesUpdateString)
       print("Series Top Performers:")
       topPerformers = sorted(
           losingManager.roster.players, key=lambda x: x.seriesPoints, reverse=True
       )
       for player in topPerformers[:3]:
           print(player.fullName + " scored " + str(player.seriesPoints))
       print()
       print("Series Worst Performers:")
       for player in topPerformers[-3:]:
           print(player.fullName + " scored " + str(player.seriesPoints))
   # endregion


   print()
   print("********************************************")
   print()




def getGameStats(index, gameId, managerList):
   print("Scoring Game: " + str(index + 1))


   boxscore = statsapi.boxscore_data(gamePk=gameId)


   managerPoints = [0.0, 0.0]


   # region AWAY BATTERS
   playersInQuestion = boxscore.get("away")
   for index, manager in enumerate(managerList):
       managerPoints[index] += batterStatsPerManager(
           manager, gameId, playersInQuestion
       )
   # endregion


   # region HOME BATTERS
   playersInQuestion = boxscore.get("home")
   for index, manager in enumerate(managerList):
       managerPoints[index] += batterStatsPerManager(
           manager, gameId, playersInQuestion
       )
   # endregion


   # region AWAY PITCHERS
   playersInQuestion = boxscore.get("away")
   for index, manager in enumerate(managerList):
       managerPoints[index] += pitchingStatsPerManager(
           manager, gameId, playersInQuestion
       )
   # endregion


   # region HOME PITCHERS
   playersInQuestion = boxscore.get("home")
   for index, manager in enumerate(managerList):
       managerPoints[index] += pitchingStatsPerManager(
           manager, gameId, playersInQuestion
       )
   # endregion


   return managerPoints




def populateRoster(roster2):
   startingPlayers = []
   starterIds = ", ".join(roster2.playerIds)
   starters = statsapi.get(
       "people", {"personIds": starterIds, "hydrate": "currentTeam"}
   )


   # TODO Logging to ensure all players can be found...?
   # if len(roster2.starterIds) != len(starters.get("people")):
   #     print("COULD NOT FIND PLAYER")


   # TODO Ensure roster is full
   # if (len(managerOne.roster.players) != 10 and len(managerOne.roster.alternates) != 4):
   #   print("ERROR! managerOne has invalid team sizes." + "Starters: " + len(managerOne.roster.players) + "Alternates: " + len(managerOne.roster.alternates))


   # if (len(managerTwo.roster.players) != 10 and len(managerTwo.roster.alternates) != 4):
   #   print("ERROR! managerTwo has invalid team sizes." + "Starters: " + len(managerTwo.roster.players) + "Alternates: " + len(managerTwo.roster.alternates))


   for player in starters.get("people"):
       startingPlayers.append(
           Player(
               fullName=player.get("firstLastName"),
               boxscoreName=player.get("boxscoreName"),
               id=player.get("id"),
               position=player.get("primaryPosition").get("abbreviation"),
               team=player.get("currentTeam").get("name"),
               games=[],
               seriesPoints=0.0,
           )
       )


   return PopulatedRoster(players=startingPlayers)




def main():


   // TODO -- insert gameIDs
   gameIds = []


   managerList = [
       Manager(
           // TODO -- insert name
           name="",
           totalPoints=0.0,
           gameResults=[],
           roster=populateRoster(
               SkeletonRoster(
                   // TODO -- insert roster
                   playerIds=[],
               )
           ),
       ),
       Manager(
           // TODO -- insert name
           name="",
           totalPoints=0.0,
           gameResults=[],
           roster=populateRoster(
               SkeletonRoster(
                   // TODO -- insert roster
                   playerIds=[],
               )
           ),
       ),
   ]


   for gameIndex, gameId in enumerate(gameIds):
       managerPoints = getGameStats(gameIndex, gameId, managerList)
       for managerIndex, managerPoint in enumerate(managerPoints):
           managerList[managerIndex].points += managerPoint
           managerList[managerIndex].gameResults.append(
               GameResult(win=managerPoint == max(managerPoints), points=managerPoint)
           )


       generateGameOutput(managerList, gameIndex + 1, gameIds)




if __name__ == "__main__":
   main()



