import os


class Environment:
    """
    Handles sensitive variables required in the application context (environment)
    """
    parsed = False
    dir = 'env/'

    vars = {}

    @staticmethod
    def parse_env():
        if Environment.parsed:
            return

        for filename in os.listdir(Environment.dir):
            var_name = filename.split('.')[0]

            with open(Environment.dir + filename) as file:
                var_value = file.read()
                Environment.vars[var_name] = var_value

        Environment.parsed = True
        print(Environment.vars)

    @staticmethod
    def get_variable(var_name):
        if Environment.parsed is False:
            Environment.parse_env()

        return Environment.vars[var_name]
