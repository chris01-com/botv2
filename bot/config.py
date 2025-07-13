
from typing import Optional
from bot.sql_database import SQLDatabase
from bot.models import ChannelConfig as ChannelConfigModel


class ChannelConfig:
    """Manages channel configuration for guilds"""
    
    def __init__(self, database: SQLDatabase):
        self.database = database
    
    async def initialize(self):
        """Initialize the channel config manager"""
        # No special initialization needed for SQL version
        pass
    
    async def set_guild_channels(self, guild_id: int, quest_list_channel: int,
                               quest_accept_channel: int, quest_submit_channel: int,
                               quest_approval_channel: int, notification_channel: int):
        """Set channel configuration for a guild"""
        config = ChannelConfigModel(
            guild_id=guild_id,
            quest_list_channel=quest_list_channel,
            quest_accept_channel=quest_accept_channel,
            quest_submit_channel=quest_submit_channel,
            quest_approval_channel=quest_approval_channel,
            notification_channel=notification_channel
        )
        await self.database.save_channel_config(config)
    
    async def get_guild_config(self, guild_id: int) -> Optional[ChannelConfigModel]:
        """Get channel configuration for a guild"""
        return await self.database.get_channel_config(guild_id)
    
    async def get_quest_list_channel(self, guild_id: int) -> Optional[int]:
        """Get quest list channel for a guild"""
        config = await self.get_guild_config(guild_id)
        return config.quest_list_channel if config else None
    
    async def get_quest_accept_channel(self, guild_id: int) -> Optional[int]:
        """Get quest accept channel for a guild"""
        config = await self.get_guild_config(guild_id)
        return config.quest_accept_channel if config else None
    
    async def get_quest_submit_channel(self, guild_id: int) -> Optional[int]:
        """Get quest submit channel for a guild"""
        config = await self.get_guild_config(guild_id)
        return config.quest_submit_channel if config else None
    
    async def get_quest_approval_channel(self, guild_id: int) -> Optional[int]:
        """Get quest approval channel for a guild"""
        config = await self.get_guild_config(guild_id)
        return config.quest_approval_channel if config else None
    
    async def get_notification_channel(self, guild_id: int) -> Optional[int]:
        """Get notification channel for a guild"""
        config = await self.get_guild_config(guild_id)
        return config.notification_channel if config else None
