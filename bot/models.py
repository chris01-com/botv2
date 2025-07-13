
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


class QuestRank:
    """Quest difficulty ranks"""
    EASY = "easy"
    NORMAL = "normal"
    MEDIUM = "medium"
    HARD = "hard"
    IMPOSSIBLE = "impossible"


class QuestCategory:
    """Quest categories"""
    HUNTING = "hunting"
    GATHERING = "gathering"
    COLLECTING = "collecting"
    CRAFTING = "crafting"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    SOCIAL = "social"
    BUILDING = "building"
    TRADING = "trading"
    PUZZLE = "puzzle"
    SURVIVAL = "survival"
    OTHER = "other"


class QuestStatus:
    """Quest status values"""
    AVAILABLE = "available"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ProgressStatus:
    """Quest progress status values"""
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Quest:
    """Quest data model"""
    quest_id: str
    title: str
    description: str
    creator_id: int
    guild_id: int
    requirements: str = ""
    reward: str = ""
    rank: str = QuestRank.NORMAL
    category: str = QuestCategory.OTHER
    status: str = QuestStatus.AVAILABLE
    created_at: datetime = field(default_factory=datetime.now)
    required_role_ids: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "creator_id": self.creator_id,
            "guild_id": self.guild_id,
            "requirements": self.requirements,
            "reward": self.reward,
            "rank": self.rank,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "required_role_ids": self.required_role_ids
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Quest':
        """Create from dictionary"""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()

        return cls(
            quest_id=data["quest_id"],
            title=data["title"],
            description=data["description"],
            creator_id=data["creator_id"],
            guild_id=data["guild_id"],
            requirements=data.get("requirements", ""),
            reward=data.get("reward", ""),
            rank=data.get("rank", QuestRank.NORMAL),
            category=data.get("category", QuestCategory.OTHER),
            status=data.get("status", QuestStatus.AVAILABLE),
            created_at=created_at,
            required_role_ids=data.get("required_role_ids", [])
        )


@dataclass
class QuestProgress:
    """Quest progress data model"""
    quest_id: str
    user_id: int
    guild_id: int
    status: str
    accepted_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    proof_text: str = ""
    proof_image_urls: List[str] = field(default_factory=list)
    channel_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "quest_id": self.quest_id,
            "user_id": self.user_id,
            "guild_id": self.guild_id,
            "status": self.status,
            "accepted_at": self.accepted_at.isoformat() if isinstance(self.accepted_at, datetime) else self.accepted_at,
            "completed_at": self.completed_at.isoformat() if self.completed_at and isinstance(self.completed_at, datetime) else self.completed_at,
            "approved_at": self.approved_at.isoformat() if self.approved_at and isinstance(self.approved_at, datetime) else self.approved_at,
            "proof_text": self.proof_text,
            "proof_image_urls": self.proof_image_urls,
            "channel_id": self.channel_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'QuestProgress':
        """Create from dictionary"""
        accepted_at = data.get("accepted_at")
        if isinstance(accepted_at, str):
            accepted_at = datetime.fromisoformat(accepted_at)
        elif not isinstance(accepted_at, datetime):
            accepted_at = datetime.now()

        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        approved_at = data.get("approved_at")
        if isinstance(approved_at, str):
            approved_at = datetime.fromisoformat(approved_at)

        return cls(
            quest_id=data["quest_id"],
            user_id=data["user_id"],
            guild_id=data["guild_id"],
            status=data["status"],
            accepted_at=accepted_at,
            completed_at=completed_at,
            approved_at=approved_at,
            proof_text=data.get("proof_text", ""),
            proof_image_urls=data.get("proof_image_urls", []),
            channel_id=data.get("channel_id")
        )


@dataclass
class UserStats:
    """User statistics data model"""
    user_id: int
    guild_id: int
    quests_completed: int = 0
    quests_accepted: int = 0
    quests_rejected: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "guild_id": self.guild_id,
            "quests_completed": self.quests_completed,
            "quests_accepted": self.quests_accepted,
            "quests_rejected": self.quests_rejected,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UserStats':
        """Create from dictionary"""
        last_updated = data.get("last_updated")
        if isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated)
        elif not isinstance(last_updated, datetime):
            last_updated = datetime.now()

        return cls(
            user_id=data["user_id"],
            guild_id=data["guild_id"],
            quests_completed=data.get("quests_completed", 0),
            quests_accepted=data.get("quests_accepted", 0),
            quests_rejected=data.get("quests_rejected", 0),
            last_updated=last_updated
        )


@dataclass
class ChannelConfig:
    """Channel configuration data model"""
    guild_id: int
    quest_list_channel_id: Optional[int] = None
    quest_accept_channel_id: Optional[int] = None
    quest_submit_channel_id: Optional[int] = None
    quest_approval_channel_id: Optional[int] = None
    notification_channel_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "guild_id": self.guild_id,
            "quest_list_channel_id": self.quest_list_channel_id,
            "quest_accept_channel_id": self.quest_accept_channel_id,
            "quest_submit_channel_id": self.quest_submit_channel_id,
            "quest_approval_channel_id": self.quest_approval_channel_id,
            "notification_channel_id": self.notification_channel_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ChannelConfig':
        """Create from dictionary"""
        return cls(
            guild_id=data["guild_id"],
            quest_list_channel_id=data.get("quest_list_channel_id"),
            quest_accept_channel_id=data.get("quest_accept_channel_id"),
            quest_submit_channel_id=data.get("quest_submit_channel_id"),
            quest_approval_channel_id=data.get("quest_approval_channel_id"),
            notification_channel_id=data.get("notification_channel_id")
        )
