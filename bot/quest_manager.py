
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
from bot.sql_database import SQLDatabase
from bot.models import Quest, QuestProgress, QuestRank, QuestStatus, ProgressStatus


class QuestManager:
    """Manages quest operations"""
    
    def __init__(self, database: SQLDatabase):
        self.database = database
    
    async def create_quest(self, title: str, description: str, creator_id: int, guild_id: int,
                          requirements: str = "", reward: str = "", rank: str = QuestRank.NORMAL,
                          category: str = "other", required_role_ids: List[int] = None) -> Quest:
        """Create a new quest"""
        if required_role_ids is None:
            required_role_ids = []
        
        quest_id = str(uuid.uuid4())[:8]
        
        quest = Quest(
            quest_id=quest_id,
            title=title,
            description=description,
            creator_id=creator_id,
            guild_id=guild_id,
            requirements=requirements,
            reward=reward,
            rank=rank,
            category=category,
            status=QuestStatus.AVAILABLE,
            created_at=datetime.now(),
            required_role_ids=required_role_ids
        )
        
        await self.database.save_quest(quest)
        return quest
    
    async def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID"""
        return await self.database.get_quest(quest_id)
    
    async def get_available_quests(self, guild_id: int) -> List[Quest]:
        """Get all available quests for a guild"""
        return await self.database.get_guild_quests(guild_id, QuestStatus.AVAILABLE)
    
    async def get_guild_quests(self, guild_id: int) -> List[Quest]:
        """Get all quests for a guild"""
        return await self.database.get_guild_quests(guild_id)
    
    async def accept_quest(self, quest_id: str, user_id: int, user_role_ids: List[int], 
                          channel_id: int) -> Tuple[Optional[QuestProgress], Optional[str]]:
        """Accept a quest"""
        quest = await self.get_quest(quest_id)
        if not quest:
            return None, "Quest not found!"
        
        if quest.status != QuestStatus.AVAILABLE:
            return None, "Quest is not available for acceptance!"
        
        # Check if user already has this quest
        existing_progress = await self.database.get_user_quest_progress(user_id, quest_id)
        if existing_progress:
            if existing_progress.status in [ProgressStatus.ACCEPTED, ProgressStatus.COMPLETED]:
                return None, "You have already accepted this quest!"
            elif existing_progress.status == ProgressStatus.REJECTED:
                # Check if 24 hours have passed since rejection
                if existing_progress.completed_at:
                    time_since_rejection = datetime.now() - existing_progress.completed_at
                    if time_since_rejection < timedelta(hours=24):
                        hours_left = 24 - int(time_since_rejection.total_seconds() / 3600)
                        return None, f"You must wait {hours_left} more hours before attempting this quest again!"
        
        # Check role requirements
        if quest.required_role_ids:
            if not any(role_id in user_role_ids for role_id in quest.required_role_ids):
                return None, "You don't have the required roles for this quest!"
        
        # Create progress entry
        progress = QuestProgress(
            quest_id=quest_id,
            user_id=user_id,
            guild_id=quest.guild_id,
            status=ProgressStatus.ACCEPTED,
            accepted_at=datetime.now(),
            accepted_channel_id=channel_id
        )
        
        await self.database.save_quest_progress(progress)
        return progress, None
    
    async def complete_quest(self, quest_id: str, user_id: int, proof_text: str, 
                           proof_image_urls: List[str]) -> Optional[QuestProgress]:
        """Complete a quest (submit proof)"""
        progress = await self.database.get_user_quest_progress(user_id, quest_id)
        if not progress or progress.status != ProgressStatus.ACCEPTED:
            return None
        
        progress.status = ProgressStatus.COMPLETED
        progress.completed_at = datetime.now()
        progress.proof_text = proof_text
        progress.proof_image_urls = proof_image_urls
        
        await self.database.save_quest_progress(progress)
        return progress
    
    async def approve_quest(self, quest_id: str, user_id: int, approved: bool) -> Optional[QuestProgress]:
        """Approve or reject a completed quest"""
        progress = await self.database.get_user_quest_progress(user_id, quest_id)
        if not progress or progress.status != ProgressStatus.COMPLETED:
            return None
        
        if approved:
            progress.status = ProgressStatus.APPROVED
            progress.approval_status = "approved"
        else:
            progress.status = ProgressStatus.REJECTED
            progress.approval_status = "rejected"
        
        await self.database.save_quest_progress(progress)
        return progress
    
    async def get_user_quests(self, user_id: int, guild_id: int) -> List[QuestProgress]:
        """Get all quests for a user in a guild"""
        return await self.database.get_user_quests(user_id, guild_id)
    
    async def delete_quest(self, quest_id: str) -> bool:
        """Delete a quest"""
        try:
            await self.database.delete_quest(quest_id)
            return True
        except Exception as e:
            print(f"Error deleting quest: {e}")
            return False
    
    async def get_pending_approvals(self, creator_id: int, guild_id: int) -> List[tuple]:
        """Get quests pending approval for a creator"""
        return await self.database.get_pending_approvals(creator_id, guild_id)
