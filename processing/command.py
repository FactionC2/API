from models.command import Command
from models.command_parameter import CommandParameter
from models.module import Module


def get_command(command_value):
    commands = Command.qu