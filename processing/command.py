from models.agent import Agent
from models.command import Command

FACTION_COMMANDS = [
    {
        "Id": 10000,
        "Name": "help",
        "Description": "Get help with Faction commands",
        "Parameters": []
    },
    {
        "Id": 10001,
        "Name": "show",
        "Description": "Show available modules and commands",
        "Parameters": []
    },
    {
        "Id": 10002,
        "Name": "set",
        "Description": "Change agent settings",
        "Parameters": []
    },
    {
        "Id": 10003,
        "Name": "load",
        "Description": "Load module into agent. For a list of modules run 'show modules'",
        "Parameters": []
    }
]


def command_json(command):
    parameters = []
    for parameter in command.Parameters:
        parameter_json = {
            'Id': parameter.Id,
            'Name': parameter.Name,
            'Help': parameter.Help,
            'Required': parameter.Required,
            'Values': parameter.Values
        }
        parameters.append(parameter_json)

    result = {
        'Id': command.Id,
        'Name': command.Name,
        'Help': command.Help,
        'Description': command.Description,
        'MitreReference': command.MitreReference,
        'OpsecSafe': command.OpsecSafe,
        'Parameters': parameters
    }
    return result


def get_commands_by_agent_id(agent_id):
    agent = Agent.query.get(agent_id)
    print("[get_commands_by_agent_id] got request for agent id {}".format(agent_id))
    results = []
    results.extend(FACTION_COMMANDS)
    for command in agent.AgentType.Commands:
        print("[get_commands_by_agent_id] adding AgentType command: {}".format(command.Name))
        results.append(command_json(command))
    for module in agent.AvailableModules:
        commands = Command.query.filter_by(ModuleId=module.Id)
        print("[get_commands_by_agent_id] adding commands form Module: {}".format(module.Name))
        for command in commands:
            print("[get_commands_by_agent_id] adding Module command: {}".format(command.Name))
            results.append(command_json(command))
    return results
