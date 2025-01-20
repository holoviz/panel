from bokeh.command.subcommand import Subcommand


class OAuthSecret(Subcommand):
    ''' Subcommand to generate a new encryption key.

    '''

    name = "oauth-secret"

    help = "Create a Panel encryption key for use with Panel server"

    args = ()

    def invoke(self, args):
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        print(key.decode('utf-8'))  # noqa: T201
