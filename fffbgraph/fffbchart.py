import pymysql.cursors
import pickle
import sys
import harveyjdb
import svgoutput

YEAR_TO_ALL = ("select * from batting join master using (playerid) where"
" teamid = '%s' and yearid = '%s'")
PLAYER_TO_PLAYER_YEARS = "select * from batting where playerid='%s' order by yearid;"
MAX_YEAR = 2013

class PlayerYear(object):
    # The possible places a player could have played in a given year.
    (NONE, TEAM, OTHER) = range(3)

    def __init__(self, year, status, team):
        self.year = year
        self.status = status
        self.team = team

class Player(object):
    def __init__(self, name):
        self.name = name
        self.years = {}

    def min_year(self):
        min_year = MAX_YEAR
        for y in self.years.keys():
            min_year = min(min_year, y)
        return min_year

    def max_year(self):
        max_year = 0
        for y in self.years.keys():
            max_year = max(max_year, y)
        return max_year

class Team(object):
    def __init__(self, team_id, year):
        self.year = int(year)
        self.team_id = team_id
        self.players = []

    def load_team_from_db(self):
        connection = harveyjdb.get_connection()
        cursor = connection.cursor()
        try:
            ids = []
            ids_to_name = {}
            cursor.execute(YEAR_TO_ALL % (self.team_id, self.year))
            for row in cursor:
                ids.append(row[u'playerID'])
                ids_to_name[row[u'playerID']] = row[u'nameFirst'] + ' ' + row[u'nameLast']
            for id in ids:
                cursor.execute(PLAYER_TO_PLAYER_YEARS % (id))
                player = Player(ids_to_name[id])
                for row in cursor:
                    y_id = int(row[u'yearID'])
                    years = player.years.get(y_id, [])
                    years.append(row[u'teamID'])
                    player.years[y_id] = years
                self.players.append(player)
        finally:
            connection.close()

    def print_team(self):
        start_year = MAX_YEAR
        # Find the earliest possible year
        for p in self.players:
            for y in p.years.keys():
                start_year = min(start_year, y)
        ## Override to truncate the table width for now.
        #start_year = int(year) - 7

        # Print the header
        print " " * 25, 
        for y in range(start_year, MAX_YEAR):
            print y, 
        print ""

        # Print all the players
        for p in self.players:
            idx = 0

            # Padding so columns are aligned
            print p.name + (25 - len(p.name)) * " ",
            for y in range(start_year, MAX_YEAR):
                if y not in p.years:
                    print "----",
                    continue
                else:
                    # Ignore multiple teams for now
                    print p.years[y][0],
            print ""

def get_filename(team_name, year):
    return "%s-%s.pickle.v2" % (team_name, year)

def load_team(team_name, year):
    print "LOADING TEAM"
    team = Team(team_name, year)
    team.load_team_from_db()
    pickle.dump(team, open(get_filename(team_name, year), "w"))

def print_team(team_name, year):
    team = pickle.load(open(get_filename(team_name, year)))
    team.print_team()

def print_svg(team_name, year):
    team = pickle.load(open(get_filename(team_name, year)))
    svgoutput.print_team(team, 2000, 2009)

if __name__ == "__main__":
    if sys.argv[1] == "load": load_team(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "print": print_team(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "svg": print_svg(sys.argv[2], sys.argv[3])
