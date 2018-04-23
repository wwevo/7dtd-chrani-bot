import argparse  # used for passing configurations to the bot


class CommandLineArgs:
    def __init__(self):
        pass

    @staticmethod
    def get_args_dict():
        parser = argparse.ArgumentParser()
        parser.add_argument("Database-file", help="prefix for the json files",
                            nargs='?',
                            default="testbot")
        parser.add_argument("--verbosity", help="what messages would you like to see? (INFO)", default="INFO")
        args = parser.parse_args()
        return vars(args)


args_dict = CommandLineArgs.get_args_dict()
