# Discord Quest Bot

## Overview

This is a comprehensive Discord quest management system that allows servers to create, manage, and track quests for their members. The bot provides a complete workflow from quest creation to completion and approval, with user statistics tracking and role-based permissions. The system features enhanced visual embed designs with professional formatting, color-coded status indicators, and structured layouts for optimal user experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture Pattern
The bot follows a modular architecture with clear separation of concerns:

- **Command Layer**: Discord.py commands and app_commands for user interaction
- **Business Logic Layer**: Quest management, user statistics, and permission handling
- **Data Layer**: JSON-based file storage with Git integration for data persistence
- **Infrastructure Layer**: Flask web server for health checks and Discord bot integration

### Data Storage Strategy
The application uses a JSON file-based database instead of a traditional database system:
- **Rationale**: Simplicity, portability, and built-in version control through Git
- **Trade-offs**: Limited scalability but excellent for small to medium Discord servers
- **Git Integration**: Automatic commits ensure data persistence and version history

## Key Components

### 1. Quest Management System (`bot/quest_manager.py`)
- **Purpose**: Core business logic for quest lifecycle management
- **Features**: Create, retrieve, update quest status, handle quest workflows
- **Dependencies**: JSON database, quest models

### 2. JSON Database (`bot/json_database.py`)
- **Purpose**: File-based data persistence with Git integration
- **Storage**: Separate JSON files for quests, progress, stats, and configuration
- **Auto-commit**: Automatically commits changes to Git for data safety

### 3. User Statistics (`bot/user_stats.py`)
- **Purpose**: Track user quest participation and completion rates
- **Metrics**: Quests completed, accepted, rejected, participation dates
- **Integration**: Updates automatically based on quest actions

### 4. Channel Configuration (`bot/config.py`)
- **Purpose**: Manage Discord channel assignments for different quest workflows
- **Flexibility**: Separate channels for listings, acceptance, submissions, approvals

### 5. Permission System (`bot/permissions.py`)
- **Purpose**: Role-based access control for quest creation and management
- **Hierarchy**: Server owner > Administrator > Moderator > Quest Creator roles
- **Granular**: Different permissions for creation vs. management

### 6. Command Interface (`bot/commands.py`)
- **Purpose**: Discord slash commands for user interaction
- **Features**: Quest creation, viewing, acceptance, submission, approval
- **User Experience**: Rich embeds with color coding and detailed information

## Data Flow

### Quest Creation Flow
1. User invokes `/create_quest` command
2. Permission check via `permissions.py`
3. Quest created through `quest_manager.py`
4. Data saved to JSON files via `json_database.py`
5. Automatic Git commit for persistence
6. Quest posted to designated channel

### Quest Completion Flow
1. User accepts quest → Status updated to "accepted"
2. User submits proof → Status updated to "completed"
3. Moderator reviews submission → Status updated to "approved" or "rejected"
4. User statistics updated automatically
5. All changes committed to Git

### Configuration Flow
1. Administrator runs `/setup_channels` command
2. Channel mappings stored in `channel_config.json`
3. Bot uses these channels for quest workflow automation

## External Dependencies

### Required Packages
- **discord.py**: Discord API interaction and bot framework
- **Flask**: Web server for health checks and uptime monitoring
- **asyncpg**: PostgreSQL support (future migration path)
- **PyNaCl**: Discord voice support (optional)

### External Services
- **Discord API**: Primary platform integration
- **Git**: Version control for data persistence
- **Replit/Cloud Platform**: Hosting with PORT environment variable support

## Deployment Strategy

### Environment Setup
- **TOKEN**: Discord bot token (required)
- **PORT**: Web server port (defaults to 5000)
- **Git Configuration**: Automatic repository initialization

### Startup Process
1. Initialize Flask web server for health checks
2. Initialize JSON database and load existing data
3. Set up Discord bot with proper intents
4. Register command handlers and event listeners
5. Connect to Discord and start bot

### Data Persistence
- **Local Storage**: JSON files in `data/` directory
- **Version Control**: Automatic Git commits on data changes
- **Backup Strategy**: Git history provides complete change tracking

### Health Monitoring
- **Flask Routes**: `/` and `/health` endpoints for uptime monitoring
- **Thread Management**: Flask runs in separate daemon thread
- **Error Handling**: Comprehensive logging and error recovery

## Development Notes

### Code Organization
- **Modular Design**: Each component has single responsibility
- **Type Hints**: Comprehensive typing for better IDE support
- **Async/Await**: Proper asynchronous programming throughout
- **Error Handling**: Graceful handling of Discord API limitations

### Visual Design
- **Enhanced Embeds**: All Discord embeds feature professional visual design with structured layouts
- **Color Coding**: Status-based color schemes for easy identification (green for success, red for errors, blue for information)
- **Structured Information**: Uses section headers (■) and formatted text blocks for clear information hierarchy
- **No Emojis**: Clean, professional appearance without emoji usage as per design requirements

### Extensibility
- **Plugin Architecture**: Easy to add new command categories
- **Database Abstraction**: Can switch from JSON to PostgreSQL easily
- **Permission System**: Flexible role-based access control
- **Configuration**: Channel-based workflow customization

The bot is designed to be simple to deploy and maintain while providing a rich quest management experience for Discord communities with professional visual presentation.