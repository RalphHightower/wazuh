from dataclasses import asdict
from typing import List, Optional, Union

from opensearchpy import exceptions
from uuid6 import UUID

from .base import BaseIndex, IndexerKey, remove_empty_values, POST_METHOD
from .utils import convert_enums
from wazuh.core.exception import WazuhError, WazuhResourceNotFound
from wazuh.core.indexer.models.commands import Action, Command, Result, Source, Status, Target, TargetType, \
    CreateCommandResponse, ResponseResult
 
DOC_ID_KEY = 'id'
TARGET_ID_KEY = 'target.id'
STATUS_KEY = 'status'
COMMAND_USER_NAME = 'Management API'


class CommandsManager(BaseIndex):
    """Set of methods to interact with the commands manager."""

    INDEX = '.commands'
    PLUGIN_URL = '/_plugins/_command_manager'

    async def create(self, command: Command) -> CreateCommandResponse:
        """Create a new command.
        
        Parameters
        ----------
        command : Command
            New command.
        
        Returns
        -------
        CreateCommandResponse
            Indexer command manager response.
        """
        try:
            response = await self._client.transport.perform_request(
                method=POST_METHOD,
                url=f'{self.PLUGIN_URL}/commands',
                body=asdict(command, dict_factory=convert_enums),
            )
        except exceptions.RequestError as e:
            raise WazuhError(1761, extra_message=str(e))

        return CreateCommandResponse(
            index=response.get(IndexerKey._INDEX),
            document_id=response.get(IndexerKey._ID),
            result=ResponseResult(response.get(IndexerKey.RESULT)),
        )


def create_restart_command(agent_id: str) -> Command:
    """Create a restart command for an agent with the ID specified.
    
    Parameters
    ----------
    agent_id : str
        Agent ID.
    
    Returns
    -------
    Command
        Restart command.
    """
    # The restart command hasn't been designed yet, this is a sample value.
    # To be defined in https://github.com/wazuh/wazuh-agent/issues/54.
    return Command(
        source=Source.SERVICES,
        target=Target(
            type=TargetType.AGENT,
            id=agent_id,
        ),
        action=Action(
            name='restart',
            version='5.0.0'
        ),
        user=COMMAND_USER_NAME,
        timeout=100,
    )


def create_set_group_command(agent_id: str, groups: List[str]) -> Command:
    """Create a set group command for an agent with the ID specified.
    
    Parameters
    ----------
    agent_id : str
        Agent ID.
    groups : List[str]
        Group names list.
    
    Returns
    -------
    Command
        Set group command.
    """
    return Command(
        source=Source.SERVICES,
        target=Target(
            type=TargetType.AGENT,
            id=agent_id,
        ),
        action=Action(
            name='set-group',
            args=groups,
            version='5.0.0'
        ),
        user=COMMAND_USER_NAME,
        timeout=100,
    )


def create_update_group_command(agent_id: str) -> Command:
    """Create a update group command for an agent with the ID specified.
    
    Parameters
    ----------
    agent_id : str
        Agent ID.
    
    Returns
    -------
    Command
        Update group command.
    """
    return Command(
        source=Source.SERVICES,
        target=Target(
            type=TargetType.AGENT,
            id=agent_id,
        ),
        action=Action(
            name='update-group',
            version='5.0.0'
        ),
        user=COMMAND_USER_NAME,
        timeout=100,
    )
