from models.agent_type import AgentType
from models.transport import Transport

def agent_type_json(agent_type):
    architectures = []
    configurations = []
    formats = []
    operating_systems = []
    versions = []
    agent_transports = []
    available_transports = []

    for architecture in agent_type.AgentTypeArchitectures:
        result = {
            "Id": architecture.Id,
            "Name": architecture.Name,
        }
        architectures.append(result)

    for config in agent_type.AgentTypeConfigurations:
        result = {
            "Id": config.Id,
            "Name": config.Name,
        }
        configurations.append(result)

    for format in agent_type.AgentTypeFormats:
        result = {
            "Id": format.Id,
            "Name": format.Name,
        }
        formats.append(result)

    for operating_system in agent_type.OperatingSystems:
        result = {
            "Id": operating_system.Id,
            "Name": operating_system.Name,
        }
        operating_systems.append(result)

    for version in agent_type.Versions:
        result = {
            "Id": version.Id,
            "Name": version.Name,
        }
        versions.append(result)

    for transport in agent_type.AgentTransportTypes:
        result = {
            "Id": transport.Id,
            "Name": transport.Name,
            "TransportTypeGuid": transport.TransportTypeGuid
        }
        agent_transports.append(result)

        associated_transports = Transport.query.filter_by(Guid=transport.TransportTypeGuid)

        for associated_transport in associated_transports:
            if associated_transport.Visible:
                available_transports.append({
                    "Id": associated_transport.Id,
                    "AgentTransportName": transport.Name,
                    "AgentTransportId": transport.Id,
                    "Name": associated_transport.Name,
                    "Guid": associated_transport.Guid,
                    "Description": associated_transport.Description,
                    "Enabled": associated_transport.Enabled
                })



    return {
        "Id": agent_type.Id,
        "Name": agent_type.Name,
        "AgentTransports": agent_transports,
        "AvailableTransports": available_transports,
        "Architectures": architectures,
        "Configurations": configurations,
        "Formats": formats,
        "OperatingSystems": operating_systems,
        "Versions": versions
    }


def get_agent_type(agent_type_id='all'):
    results = []
    agent_types = []
    if agent_type_id == 'all':
        agent_types = AgentType.query.all()
    else:
        agent_types.append(AgentType.query.get(agent_type_id))
    for agent_type in agent_types:
        results.append(agent_type_json(agent_type))
    return {
        "Success": 'True',
        "Results": results
    }