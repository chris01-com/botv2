
import os
import asyncio
import asyncpg
from typing import List, Optional, Dict, Any
from datetime import datetime
from bot.models import Quest, QuestProgress, UserStats, ChannelConfig as ChannelConfigModel


class SQLDatabase:
    """PostgreSQL database interface for the quest bot"""

    def __init__(self):
        self.pool = None
        self.database_url = os.getenv('DATABASE_URL')
        print(f"DATABASE_URL found: {bool(self.database_url)}")
        print(f"DATABASE_URL starts with: {self.database_url[:20] if self.database_url else 'None'}")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required!")
        if not self.database_url.startswith(('postgresql://', 'postgres://')):
            raise ValueError(f"Invalid DATABASE_URL format. Must start with 'postgresql://' or 'postgres://'. Got: {self.database_url[:20]}")

    async def initialize(self):
        """Initialize the database connection pool and create tables"""
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            
            # Create tables
            await self._create_tables()
            print("SQL Database initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize SQL database: {e}")
            raise

    async def _create_tables(self):
        """Create all necessary tables"""
        async with self.pool.acquire() as conn:
            # Quests table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS quests (
                    quest_id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    creator_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    requirements TEXT DEFAULT '',
                    reward TEXT DEFAULT '',
                    rank VARCHAR(50) DEFAULT 'normal',
                    category VARCHAR(50) DEFAULT 'other',
                    status VARCHAR(50) DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    required_role_ids BIGINT[]
                )
            ''')

            # Quest progress table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS quest_progress (
                    id SERIAL PRIMARY KEY,
                    quest_id VARCHAR(255) NOT NULL,
                    user_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    status VARCHAR(50) DEFAULT 'accepted',
                    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    proof_text TEXT DEFAULT '',
                    proof_image_urls TEXT[] DEFAULT '{}',
                    approval_status VARCHAR(50) DEFAULT '',
                    accepted_channel_id BIGINT,
                    UNIQUE(user_id, quest_id)
                )
            ''')

            # User stats table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    quests_completed INTEGER DEFAULT 0,
                    quests_accepted INTEGER DEFAULT 0,
                    quests_rejected INTEGER DEFAULT 0,
                    first_quest_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_quest_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, guild_id)
                )
            ''')

            # Channel config table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS channel_config (
                    guild_id BIGINT PRIMARY KEY,
                    quest_list_channel BIGINT,
                    quest_accept_channel BIGINT,
                    quest_submit_channel BIGINT,
                    quest_approval_channel BIGINT,
                    notification_channel BIGINT
                )
            ''')

    async def close(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()

    # Quest methods
    async def save_quest(self, quest: Quest):
        """Save a quest to the database"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO quests (quest_id, title, description, creator_id, guild_id, 
                                  requirements, reward, rank, category, status, created_at, required_role_ids)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ON CONFLICT (quest_id) 
                DO UPDATE SET 
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    requirements = EXCLUDED.requirements,
                    reward = EXCLUDED.reward,
                    rank = EXCLUDED.rank,
                    category = EXCLUDED.category,
                    status = EXCLUDED.status,
                    required_role_ids = EXCLUDED.required_role_ids
            ''', quest.quest_id, quest.title, quest.description, quest.creator_id, 
                quest.guild_id, quest.requirements, quest.reward, quest.rank,
                quest.category, quest.status, quest.created_at, quest.required_role_ids)

    async def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM quests WHERE quest_id = $1', quest_id)
            if row:
                return Quest(
                    quest_id=row['quest_id'],
                    title=row['title'],
                    description=row['description'],
                    creator_id=row['creator_id'],
                    guild_id=row['guild_id'],
                    requirements=row['requirements'] or '',
                    reward=row['reward'] or '',
                    rank=row['rank'] or 'normal',
                    category=row['category'] or 'other',
                    status=row['status'] or 'available',
                    created_at=row['created_at'],
                    required_role_ids=list(row['required_role_ids']) if row['required_role_ids'] else []
                )
        return None

    async def get_guild_quests(self, guild_id: int, status: str = None) -> List[Quest]:
        """Get all quests for a guild, optionally filtered by status"""
        async with self.pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    'SELECT * FROM quests WHERE guild_id = $1 AND status = $2 ORDER BY created_at DESC',
                    guild_id, status
                )
            else:
                rows = await conn.fetch(
                    'SELECT * FROM quests WHERE guild_id = $1 ORDER BY created_at DESC',
                    guild_id
                )
            
            quests = []
            for row in rows:
                quest = Quest(
                    quest_id=row['quest_id'],
                    title=row['title'],
                    description=row['description'],
                    creator_id=row['creator_id'],
                    guild_id=row['guild_id'],
                    requirements=row['requirements'] or '',
                    reward=row['reward'] or '',
                    rank=row['rank'] or 'normal',
                    category=row['category'] or 'other',
                    status=row['status'] or 'available',
                    created_at=row['created_at'],
                    required_role_ids=list(row['required_role_ids']) if row['required_role_ids'] else []
                )
                quests.append(quest)
            return quests

    async def delete_quest(self, quest_id: str):
        """Delete a quest and all associated progress"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute('DELETE FROM quest_progress WHERE quest_id = $1', quest_id)
                await conn.execute('DELETE FROM quests WHERE quest_id = $1', quest_id)

    # Quest Progress methods
    async def save_quest_progress(self, progress: QuestProgress):
        """Save quest progress to the database"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO quest_progress (quest_id, user_id, guild_id, status, accepted_at, 
                                          completed_at, proof_text, proof_image_urls, 
                                          approval_status, accepted_channel_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (user_id, quest_id)
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    completed_at = EXCLUDED.completed_at,
                    proof_text = EXCLUDED.proof_text,
                    proof_image_urls = EXCLUDED.proof_image_urls,
                    approval_status = EXCLUDED.approval_status,
                    accepted_channel_id = EXCLUDED.accepted_channel_id
            ''', progress.quest_id, progress.user_id, progress.guild_id, progress.status,
                progress.accepted_at, progress.completed_at, progress.proof_text,
                progress.proof_image_urls, progress.approval_status, progress.accepted_channel_id)

    async def get_user_quest_progress(self, user_id: int, quest_id: str) -> Optional[QuestProgress]:
        """Get progress for a specific user and quest"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM quest_progress WHERE user_id = $1 AND quest_id = $2',
                user_id, quest_id
            )
            if row:
                return QuestProgress(
                    quest_id=row['quest_id'],
                    user_id=row['user_id'],
                    guild_id=row['guild_id'],
                    status=row['status'],
                    accepted_at=row['accepted_at'],
                    completed_at=row['completed_at'],
                    proof_text=row['proof_text'] or '',
                    proof_image_urls=list(row['proof_image_urls']) if row['proof_image_urls'] else [],
                    approval_status=row['approval_status'] or '',
                    accepted_channel_id=row['accepted_channel_id']
                )
        return None

    async def get_user_quests(self, user_id: int, guild_id: int = None) -> List[QuestProgress]:
        """Get all quests for a user"""
        async with self.pool.acquire() as conn:
            if guild_id:
                rows = await conn.fetch(
                    'SELECT * FROM quest_progress WHERE user_id = $1 AND guild_id = $2 ORDER BY accepted_at DESC',
                    user_id, guild_id
                )
            else:
                rows = await conn.fetch(
                    'SELECT * FROM quest_progress WHERE user_id = $1 ORDER BY accepted_at DESC',
                    user_id
                )
            
            progresses = []
            for row in rows:
                progress = QuestProgress(
                    quest_id=row['quest_id'],
                    user_id=row['user_id'],
                    guild_id=row['guild_id'],
                    status=row['status'],
                    accepted_at=row['accepted_at'],
                    completed_at=row['completed_at'],
                    proof_text=row['proof_text'] or '',
                    proof_image_urls=list(row['proof_image_urls']) if row['proof_image_urls'] else [],
                    approval_status=row['approval_status'] or '',
                    accepted_channel_id=row['accepted_channel_id']
                )
                progresses.append(progress)
            return progresses

    async def get_pending_approvals(self, creator_id: int, guild_id: int) -> List[tuple]:
        """Get quests pending approval for a quest creator"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT qp.quest_id, qp.user_id, qp.proof_text, qp.proof_image_urls, q.title
                FROM quest_progress qp
                JOIN quests q ON qp.quest_id = q.quest_id
                WHERE qp.guild_id = $1 AND qp.status = 'completed' AND q.creator_id = $2
            ''', guild_id, creator_id)
            
            pending = []
            for row in rows:
                pending.append((
                    row['quest_id'],
                    row['user_id'],
                    row['proof_text'] or '',
                    list(row['proof_image_urls']) if row['proof_image_urls'] else [],
                    row['title']
                ))
            return pending

    # User Stats methods
    async def save_user_stats(self, stats: UserStats):
        """Save user statistics"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO user_stats (user_id, guild_id, quests_completed, quests_accepted, 
                                      quests_rejected, first_quest_date, last_quest_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (user_id, guild_id)
                DO UPDATE SET 
                    quests_completed = EXCLUDED.quests_completed,
                    quests_accepted = EXCLUDED.quests_accepted,
                    quests_rejected = EXCLUDED.quests_rejected,
                    first_quest_date = EXCLUDED.first_quest_date,
                    last_quest_date = EXCLUDED.last_quest_date
            ''', stats.user_id, stats.guild_id, stats.quests_completed,
                stats.quests_accepted, stats.quests_rejected,
                stats.first_quest_date, stats.last_quest_date)

    async def get_user_stats(self, user_id: int, guild_id: int) -> Optional[UserStats]:
        """Get user statistics"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM user_stats WHERE user_id = $1 AND guild_id = $2',
                user_id, guild_id
            )
            if row:
                return UserStats(
                    user_id=row['user_id'],
                    guild_id=row['guild_id'],
                    quests_completed=row['quests_completed'],
                    quests_accepted=row['quests_accepted'],
                    quests_rejected=row['quests_rejected'],
                    first_quest_date=row['first_quest_date'],
                    last_quest_date=row['last_quest_date']
                )
        return None

    async def get_guild_leaderboard(self, guild_id: int, limit: int = 10) -> List[UserStats]:
        """Get guild leaderboard"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM user_stats 
                WHERE guild_id = $1 
                ORDER BY quests_completed DESC 
                LIMIT $2
            ''', guild_id, limit)
            
            stats_list = []
            for row in rows:
                stats = UserStats(
                    user_id=row['user_id'],
                    guild_id=row['guild_id'],
                    quests_completed=row['quests_completed'],
                    quests_accepted=row['quests_accepted'],
                    quests_rejected=row['quests_rejected'],
                    first_quest_date=row['first_quest_date'],
                    last_quest_date=row['last_quest_date']
                )
                stats_list.append(stats)
            return stats_list

    async def get_total_guild_stats(self, guild_id: int) -> Dict[str, int]:
        """Get total guild statistics"""
        async with self.pool.acquire() as conn:
            # Get quest count
            quest_count = await conn.fetchval(
                'SELECT COUNT(*) FROM quests WHERE guild_id = $1', guild_id
            )
            
            # Get user stats totals
            stats_row = await conn.fetchrow('''
                SELECT 
                    COALESCE(SUM(quests_completed), 0) as total_completed,
                    COALESCE(SUM(quests_accepted), 0) as total_accepted,
                    COALESCE(SUM(quests_rejected), 0) as total_rejected,
                    COUNT(*) as active_users
                FROM user_stats 
                WHERE guild_id = $1
            ''', guild_id)
            
            return {
                'total_quests': quest_count,
                'total_completed': stats_row['total_completed'],
                'total_accepted': stats_row['total_accepted'],
                'total_rejected': stats_row['total_rejected'],
                'active_users': stats_row['active_users']
            }

    # Channel Config methods
    async def save_channel_config(self, config: ChannelConfigModel):
        """Save channel configuration"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO channel_config (guild_id, quest_list_channel, quest_accept_channel,
                                          quest_submit_channel, quest_approval_channel, notification_channel)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (guild_id)
                DO UPDATE SET 
                    quest_list_channel = EXCLUDED.quest_list_channel,
                    quest_accept_channel = EXCLUDED.quest_accept_channel,
                    quest_submit_channel = EXCLUDED.quest_submit_channel,
                    quest_approval_channel = EXCLUDED.quest_approval_channel,
                    notification_channel = EXCLUDED.notification_channel
            ''', config.guild_id, config.quest_list_channel, config.quest_accept_channel,
                config.quest_submit_channel, config.quest_approval_channel, config.notification_channel)

    async def get_channel_config(self, guild_id: int) -> Optional[ChannelConfigModel]:
        """Get channel configuration"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM channel_config WHERE guild_id = $1', guild_id
            )
            if row:
                return ChannelConfigModel(
                    guild_id=row['guild_id'],
                    quest_list_channel=row['quest_list_channel'],
                    quest_accept_channel=row['quest_accept_channel'],
                    quest_submit_channel=row['quest_submit_channel'],
                    quest_approval_channel=row['quest_approval_channel'],
                    notification_channel=row['notification_channel']
                )
        return None
