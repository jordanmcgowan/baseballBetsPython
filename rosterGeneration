import requests
import statsapi


def main():
   teams = [
       // TODO -- insert teamID and teamName
       {"teamId": 0, "teamName": ""},
       {"teamId": 0, "teamName": ""},
   ]
   for team in teams:
       roster = statsapi.get("team_roster", {"teamId": team.get("teamId")})
       print("*** " + team.get("teamName") + " ***")
       playerList = roster.get("roster")
       batters = []
       pitchers = []
       for player in playerList:
           if player.get("position").get("type") == "Pitcher":
               pitchers.append(player)
           else:
               batters.append(player)


       for pitcher in pitchers:
           stats = statsapi.player_stat_data(pitcher.get("person").get("id"))
           seasonStats = stats.get("stats")
           pitchingStats = [
               statLine
               for statLine in seasonStats
               if statLine.get("group") == "pitching"
           ]
           actualStats = pitchingStats[0].get("stats")
           wins = actualStats.get("wins")
           losses = actualStats.get("losses")
           era = actualStats.get("era")
           inningsPitched = actualStats.get("inningsPitched")
           strikeouts = actualStats.get("strikeOuts")
           saves = actualStats.get("saves")
           holds = actualStats.get("holds")
           pitcherOutput = (
               pitcher.get("person").get("fullName")
               + ","
               + team.get("teamName")
               + ","
               + str(pitcher.get("person").get("id"))
               + ","
               + "W: "
               + str(wins)
               + ","
               + "L: "
               + str(losses)
               + ","
               + "H: "
               + str(holds)
               + ","
               + "S: "
               + str(saves)
               + ","
               + "ERA: "
               + str(era)
               + ","
               + "IP: "
               + str(inningsPitched)
               + ","
               + "K: "
               + str(strikeouts)
               + ","
               + "Pitcher"
           )
           print(pitcherOutput)


       for batter in batters:
           stats = statsapi.player_stat_data(batter.get("person").get("id"))
           seasonStats = stats.get("stats")
           battingStats = [
               statLine
               for statLine in seasonStats
               if statLine.get("group") == "hitting"
           ]
           actualStats = battingStats[0].get("stats")
           hits = actualStats.get("hits")
           homeRuns = actualStats.get("homeRuns")
           average = actualStats.get("avg")
           rbis = actualStats.get("rbi")
           stolenBases = actualStats.get("stolenBases")
           runs = actualStats.get("runs")
           walks = actualStats.get("baseOnBalls")
           batterOutput = (
               batter.get("person").get("fullName")
               + ","
               + team.get("teamName")
               + ","
               + str(batter.get("person").get("id"))
               + ","
               + "H: "
               + str(hits)
               + ","
               + "HRs: "
               + str(homeRuns)
               + ","
               + "RBIs: "
               + str(rbis)
               + ","
               + "AVG: "
               + str(average)
               + ","
               + "SBs: "
               + str(stolenBases)
               + ","
               + "R: "
               + str(runs)
               + ","
               + "BB: "
               + str(walks)
               + ","
               + "Batter"
           )
           print(batterOutput)




if __name__ == "__main__":
   main()



