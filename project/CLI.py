import unittest
import shlex
import StringConst as sc

from Game import GameFactory, make_game
from GameMaker import GMFactory


def need_admin(func):
    def wrapper(*args):
        if not args[0].current_user or not args[0].current_user.is_admin():
            return sc.permission_denied
        return func(*args)
    return wrapper


def need_self(func):
    def wrapper(*args):
        try:
            if not args[0].current_user:
                return sc.permission_denied
            if not args[0].current_user.is_admin() and not args[0].current_user.get_username() == args[1][1]:
                return sc.permission_denied
        except IndexError:
            return sc.invalid_param
        return func(*args)
    return wrapper


def login(self, args):
    if self.current_user:
        return sc.existing_login
    try:
        self.current_user = self.gm.login(args[1], args[2])
        if self.current_user:
            return sc.login_success
        if self.game:
            self.current_user = self.game.teams[args[1]].login(args[1], args[2])
            if self.current_user:
                return sc.login_success
    except IndexError:
        return sc.invalid_param
    except KeyError:
        return sc.login_fail
    return sc.login_fail


def logout(self, _):
    if not self.current_user:
        return "No user logged in"
    self.current_user = None
    return sc.logout


@need_admin
def add_team(self, args):
    try:
        added = self.game.add_team(args[1], args[2])
    except IndexError:
        return sc.invalid_param
    if added:
        return sc.team_add
    return sc.team_add_fail


@need_admin
def remove_team(self, args):
    try:
        removed = self.game.remove_team(args[1])
    except IndexError:
        return sc.invalid_param
    if removed:
        return sc.team_remove
    return sc.team_remove_fail


@need_admin
def add_landmark(self, args):
    try:
        added = self.game.add_landmark(args[1], args[2], args[3])
    except IndexError:
        return sc.invalid_param
    if added:
        return sc.landmark_add
    return sc.landmark_add_fail


@need_admin
def remove_landmark(self, args):
    try:
        removed = self.game.remove_landmark(args[1])
    except IndexError:
        return sc.invalid_param
    if removed:
        return sc.landmark_remove
    return sc.landmark_remove_fail


@need_admin
def start(self, _):
    try:
        self.game.start()
    except IndexError:
        return sc.invalid_param
    if self.game.started:
        return "Started Game"
    return "Failed to start Game"


@need_admin
def create(self, _):
    try:
        self.game = GameFactory(make_game).create_game()
    except IndexError:
        return sc.invalid_param
    if self.game:
        return "Game Created"
    return "Game Failed"


@need_self
def edit_team(self, args):
    name_index = None
    pass_index = None
    try:
        name_index = args.index('name', 2)
    except ValueError:
        pass

    try:
        pass_index = args.index('password', 2)
    except ValueError:
        pass

    try:
        if name_index:
            name = args[name_index + 1]
            password = None
            if pass_index:
                password = args[pass_index + 1]
            if self.game.modify_team(oldname=args[1], newname=name, newpassword=password):
                return "Team changed"
            else:
                return "Team new name already exists"
        if pass_index:
            if self.game.modify_team(oldname=args[1], newpassword=args[pass_index + 1]):
                return "Team changed"
        return "No Changes"
    except IndexError:
        return sc.invalid_param


commands = {"login": login, "addteam": add_team, "addlandmark": add_landmark, "removeteam": remove_team, "start": start,
            "create": create, "logout": logout, "editteam": edit_team, "removelandmark": remove_landmark}


class CLI:
    def __init__(self, command_dict):
        self.gm = GMFactory().get_gm()
        self.commands = command_dict
        self.current_user = None
        self.game = None

    def command(self, args):
        inp = shlex.split(args)
        try:
            return self.commands[inp[0].lower()](self, inp)
        except KeyError:
            return "Invalid command"
        except IndexError:
            return sc.invalid_param


class TestGMLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)

    def test_login_success(self):
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")

    def test_login_bad_password(self):
        self.assertEqual(sc.login_fail, self.cli.command("login gamemaker 4321"), "Login return message not correct")

    def test_login_bad_username(self):
        self.assertEqual(sc.login_fail, self.cli.command("login ___ 1234"), "Login return message not correct")

    def test_login_bad_args(self):
        self.assertEqual(sc.invalid_param, self.cli.command("login gamemaker"), sc.invalid_param)


class TestTeamExistsLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Valid login failed")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")
        self.assertEqual(sc.team_add, self.cli.command("addteam teamName teamPassword"), "Failed to add Team")
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to log out")

    def test_login_success(self):
        self.assertEqual(sc.login_success, self.cli.command("login teamName teamPassword"), "Valid login failed")

    def test_login_bad_password(self):
        self.assertEqual(sc.login_fail, self.cli.command("login teamName 1234"), "Invalid login succeeded")

    def test_login_bad_username(self):
        self.assertEqual(sc.login_fail, self.cli.command("login ___ teamPassword"), "Invalid login succeeded")


class TestTeamNotExistsLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Valid login failed")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to log out")

    def test_login(self):
        self.assertEqual(sc.login_fail, self.cli.command("login teamName teamPassword"), "Invalid login failed")


class TestEditTeams(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")
        self.assertEqual(sc.team_add, self.cli.command("addteam Team1 239103"))
        self.assertEqual(sc.team_add, self.cli.command("addteam Team2 Rocks"))
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to log out")

    def test_team_edit_name_logged_in(self):
        self.assertEqual(sc.login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual("Team changed", self.cli.command("editteam Team1 name ILikeCheese"),
                         "Failed to change username")

    def test_team_edit_password_logged_in(self):
        self.assertEqual(sc.login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual("Team changed", self.cli.command("editteam Team1 password ThisIsSecure"),
                         "Failed to change pass")

    def test_team_edit_name_and_password_logged_in(self):
        self.assertEqual(sc.login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual("Team changed", self.cli.command("editteam Team1 name ILikeCheese password ThisIsSecure"),
                         "Failed to change pass")

    def test_team_edit_name_not_logged_in(self):
        self.assertEqual(sc.permission_denied, self.cli.command("editteam Team1 name ILikeCheese"),
                         "no team is logged in")

    def test_team_edit_password_not_logged_in(self):
        self.assertEqual(sc.permission_denied, self.cli.command("editteam Team1 password ThisIsSecure"),
                         "no team is logged in")

    def test_team_edit_other_team_name(self):
        self.assertEqual(sc.login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(sc.permission_denied, self.cli.command("editteam Team2 password ThisIsSecure"),
                         "Only edit self")

    def test_team_edit_name_but_there_is_a_team_with_same_name(self):
        self.assertEqual(sc.login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual("Team new name already exists", self.cli.command("editteam Team1 name Team2"),
                         "Only edit self")

    def test_team_edit_name_but_there_is_a_team_with_same_name_v2(self):
        self.assertEqual(sc.login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual("Team new name already exists",
                         self.cli.command("editteam Team1 name Team2 password ThisIsSecure"), "Only edit self")

    def test_gm_edit_team_name(self):
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Team changed", self.cli.command("editteam Team1 name ILikeCheese"), "Failed to change name")

    def test_gm_edit_team_pass(self):
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Team changed", self.cli.command("editteam Team1 password ThisIsSecure"),
                         "Failed to change pass")

    def test_team_edit_bad_args(self):
        self.assertEqual(sc.login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual("No Changes", self.cli.command("editteam Team1"), "check for bad input")


class TestAddTeam(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")

    def test_add_team_is_gm(self):
        self.assertEqual(sc.team_add, self.cli.command("addteam Team1 1234"), sc.team_add_fail)

    def test_add_team_not_gm(self):
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(sc.permission_denied, self.cli.command("addteam Team1 1234"), "Only game maker can add teams")

    def test_add_team_duplicate(self):
        self.assertEqual(sc.team_add, self.cli.command("addteam Team1 1234"), sc.team_add_fail)
        self.assertEqual(sc.team_add_fail, self.cli.command("addteam Team1 1234"), "can not have duplicate teams")

    def test_add_team_bad_args(self):
        self.assertEqual(sc.invalid_param, self.cli.command("addteam"), sc.invalid_param)


class TestRemoveTeam(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")
        self.assertEqual(sc.team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(sc.team_add, self.cli.command("addteam Team2 02ka"), "setup failed")
        self.assertEqual(sc.team_add, self.cli.command("addteam Team3 192j"), "setup failed")

    def test_remove_team_is_gm(self):
        self.assertEqual(sc.team_remove, self.cli.command("removeteam Team1"), "Failed to remove team")

    def test_remove_team_is_not_gm(self):
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(sc.permission_denied, self.cli.command("removeteam Team1"), "only game maker can remove")

    def test_remove_team_does_not_exist(self):
        del self.cli.game.teams["Team3"]
        self.assertEqual(sc.team_remove_fail, self.cli.command("removeteam Team3"), "team does not exist")

    def test_remove_team_from_empty_team_list(self):
        self.cli.game.teams.clear()
        self.assertEqual(sc.team_remove_fail, self.cli.command("removeteam Team1"), "list of teams empty")

    def test_remove_team_bad_args(self):
        self.cli.is_gm = True
        self.assertEqual(sc.invalid_param, self.cli.command("removeteam"), sc.invalid_param)


class TestStartGame(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")
        self.assertEqual(sc.team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(sc.team_add, self.cli.command("addteam Team2 02ka"), "setup failed")
        self.assertEqual(sc.landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         sc.landmark_add_fail)

    def test_start_game_is_gm(self):
        self.assertEqual("Started Game", self.cli.command("start"), "Failed to start game")

    def test_start_game_is_not_gm(self):
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(sc.permission_denied, self.cli.command("start"), "Only admin can not start a Game")

    def test_start_team_bad_args(self):
        self.assertEqual(sc.invalid_param, self.cli.command(""), sc.invalid_param)


class TestCreate(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")

    def test_create_is_gm(self):
        self.assertEqual(None, self.cli.game)
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to Create Game")

    def test_create_not_gm(self):
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(sc.permission_denied, self.cli.command("create"), "Only admin can Create a new Game")


class TestAddLandmark(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to Create Game")

    def test_add_landmark_is_gm(self):
        self.assertEqual(sc.landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         sc.landmark_add_fail)

    def test_add_landmark_not_gm(self):
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(sc.permission_denied,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "Only admin can add landmarks")

    def test_add_landmark_duplicate(self):
        self.assertEqual(sc.landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         sc.landmark_add_fail)
        self.assertEqual(sc.landmark_add_fail,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "no duplicate landmarks")

    def test_add_landmark_bad_args(self):
        self.assertEqual(sc.invalid_param, self.cli.command("addlandmark"), sc.invalid_param)


class TestRemoveLandmark(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(commands)
        self.assertEqual(sc.login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")
        self.assertEqual(sc.team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(sc.landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         sc.landmark_add_fail)
        self.assertEqual(sc.landmark_add,
                         self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         sc.landmark_add_fail)

    def test_remove_landmark_is_gm(self):
        self.assertEqual(sc.landmark_remove, self.cli.command("removelandmark UWM"), "Failed to remove landmark")

    def test_remove_landmark_is_not_gm(self):
        self.assertEqual(sc.logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(sc.permission_denied, self.cli.command('removelandmark "New York"'),
                         "only game maker can remove")

    def test_remove_landmark_does_not_exist(self):
        self.cli.game.landmarks.pop()
        self.assertEqual(sc.landmark_remove_fail, self.cli.command("removelandmark UWM"), "landmark does not exist")

    def test_remove_landmark_from_empty_landmark_list(self):
        self.cli.game.landmarks.clear()
        self.assertEqual(sc.landmark_remove_fail, self.cli.command("removelandmark UWM"), "list of teams empty")

    def test_remove_landmark_bad_args(self):
        self.cli.is_gm = True
        self.assertEqual(sc.invalid_param, self.cli.command("removelandmark"), sc.invalid_param)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGMLogin))
    suite.addTest(unittest.makeSuite(TestTeamExistsLogin))
    suite.addTest(unittest.makeSuite(TestTeamNotExistsLogin))
    suite.addTest(unittest.makeSuite(TestEditTeams))
    suite.addTest(unittest.makeSuite(TestAddTeam))
    suite.addTest(unittest.makeSuite(TestRemoveTeam))
    suite.addTest(unittest.makeSuite(TestStartGame))
    suite.addTest(unittest.makeSuite(TestAddLandmark))
    suite.addTest(unittest.makeSuite(TestRemoveLandmark))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures:
        print(i[1])
