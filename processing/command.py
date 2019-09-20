from models.agent import Agent
from models.command import Command


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
    results = []
    for module in agent.AvailableModules:
        commands = Command.query.filter_by(ModuleId=module.Id)
        for command in commands:
            results.append(command_json(command))
    return results
