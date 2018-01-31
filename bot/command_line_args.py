import argparse  # used for passing configurations to the bot


class CommandLineArgs:
    def __init__(self):
        pass

    @staticmethod
    def get_args_dict():
        parser = argparse.ArgumentParser()
        parser.add_argument("IP-address", help="IP-address of your 7dtd game-server (127.0.0.1)", nargs='?',
                            default="127.0.0.1")
        parser.add_argument("Telnet-port", help="Telnet-port of your 7dtd game-server (8081)", nargs='?',
                            default="8081",
                            type=int)
        parser.add_argument("Telnet-password", help="Telnet-password of your 7dtd game-server (12345678)", nargs='?',
                            default="12345678")
        parser.add_argument("Database-file", help="prefix for the json files",
                            nargs='?',
                            default="dummy")
        parser.add_argument("IP-Token", help="access token for country codes (ipinfo.io)",
                            nargs='?',
                            default="dummy")
        parser.add_argument("--verbosity", help="what messages would you like to see? (INFO)", default="INFO")
        args = parser.parse_args()
        return vars(args)


args_dict = CommandLineArgs.get_args_dict()
