import unittest
from abc import ABC
from project.Landmark import LandmarkFactory
from project.Team import TeamFactory


class GameInterface(ABC):
    def add_team(self, team):
        pass

    def remove_team(self, name):
        pass

    def modify_team(self, oldname, name=None, password=None):
        pass

    def add_landmark(self, landmark):
        pass

    def remove_landmark(self, landmark):
        pass

    def modify_landmark(self, oldlandmark, newlandmark):
        pass

    def set_point_penalty(self, points):
        pass

    def set_time_penalty(self, time):
        pass

    def start(self):
        pass

    def end(self):
        pass


class GameFactory:
    def getGame(self):
        return self.Game()

    class Game(GameInterface):
        def __init__(self):
            self.teams = [TeamFactory().Team]
            self.landmarks = [LandmarkFactory().Landmark]
            self.started = False
            self.penaltyValue = 0
            self.penaltyTime = 0

        def add_team(self, team):
            return False

        def remove_team(self, name):
            return False

        def modify_team(self, oldname, name=None, password=None):
            pass

        def add_landmark(self, landmark):
            return False

        def remove_landmark(self, landmark):
            pass

        def modify_landmark(self, oldlandmark, newlandmark):
            pass

        def set_point_penalty(self, points):
            pass

        def set_time_penalty(self, time):
            pass

        def start(self):
            pass

        def end(self):
            pass


class TestAddTeam(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()

    def test_add_team(self):
        self.game.started = False
        self.assertTrue(self.game.add_team(TeamFactory().getTeam("Team1", "1232")), "Did not add team")

    def test_add_team_duplicates(self):
        self.game.started = False
        self.game.teams.append(TeamFactory().getTeam("Team1", "1232"))
        self.assertFalse(self.game.add_team(TeamFactory().getTeam("Team1", "1232")), "duplicate teams!")

    def test_add_team_after_Game_started(self):
        self.game.started = True
        self.assertFalse(self.game.add_team(TeamFactory().getTeam("Team1", "1232")),
                         "should not add teams once Game starts")


class TestRemoveTeam(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()

    def test_remove_team(self):
        self.game.started = False
        team1 = TeamFactory().getTeam("Team1", "1232")
        self.game.teams.append(team1)
        self.assertTrue(self.game.remove_team(team1.username), "Failed to remove team")

    def test_remove_team_does_not_exist(self):
        self.game.started = False
        team1 = TeamFactory().getTeam("Team1", "1232")
        self.game.teams.append(team1)
        self.game.remove_team(team1.username)
        self.assertFalse(self.game.remove_team(team1.username), "Team does not exist")

    def test_remove_team_from_empty_team_list(self):
        self.game.started = False
        team1 = TeamFactory().getTeam("Team1", "1232")
        self.game.teams.clear()
        self.assertFalse(self.game.remove_team(team1.username), "Failed to remove team, list of teams empty")

    def test_remove_team_game_started(self):
        team1 = TeamFactory().getTeam("Team1", "1232")
        self.game.teams.append(team1)
        self.game.started = True
        self.assertFalse(self.game.remove_team("team1"), "should not remove teams once game starts")


class TestStartGame(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()

    def test_start_game(self):
        self.game.started = False
        self.game.start()
        self.assertTrue(self.game.started, "game in progress value not set")

    def test_start_while_game_in_progress(self):
        self.game.GameInProgress = True
        self.game.start()
        self.assertFalse(self.game.GameInProgress, "there is a game that has already has been started")


class TestAddLandmark(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()

    def test_add_landmark(self):
        self.game.started = False
        landmark = LandmarkFactory().getLandmark("New York", "Gift given by the French", "statue of liberty")
        self.assertTrue(self.game.add_landmark(landmark), "Failed to add landmark")

    def test_add_landmark_game_in_progress(self):
        self.game.started = True
        landmark = LandmarkFactory().getLandmark("New York", "Gift given by the French", "statue of liberty")
        self.assertFalse(self.game.add_landmark(landmark), "Cannot add landmark once game has started")

    def test_add_landmark_duplicates(self):
        self.game.started = False
        ld = LandmarkFactory().getLandmark("New York", "Gift given by the French", "statue of liberty")
        self.game.landmarks.append(ld)
        self.assertFalse(self.game.add_landmark(ld), "Cannot add duplicate landmarks")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAddTeam))
    suite.addTest(unittest.makeSuite(TestRemoveTeam))
    suite.addTest(unittest.makeSuite(TestStartGame))
    suite.addTest(unittest.makeSuite(TestAddLandmark))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
