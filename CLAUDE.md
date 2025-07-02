# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Install dependencies:**
```bash
# This project uses uv for dependency management
uv sync
```

**Run the application:**
```bash
uv run python main.py
```

**Round System Controls:**
- Click to select characters and plan movement
- SPACE: End turn and execute planned actions
- Characters can only move once per round

**Generate config model from YAML:**
```bash
uv run datamodel-codegen --input ./config/config.yaml --input-file-type yaml --output ./config/model.py --class-name Config --disable-timestamp
```

## Architecture Overview

This is a pygame-based tile-based game demo called "ITB Demo" (Into the Breach style). The architecture follows an event-driven pattern with clear separation between game logic, rendering, and configuration.

### Core Components

**Configuration System (`config/`)**
- `config.yaml`: Main configuration file defining screen size, tile dimensions, game parameters
- `loader.py`: Loads YAML config using pydantic-yaml parser
- `model.py`: Pydantic models for type-safe configuration (generated from YAML)

**Game Engine (`game/`)**
- `map.py`: Core Map class managing tile-based game board, unit positioning, pathfinding
- `units.py`: Unit hierarchy with base Unit class, AnimatedUnit, and Character classes
- `tile.py`: Pydantic-based Tile model with coordinate validation and neighbor logic
- `factories.py`: Factory pattern for creating different unit types (characters, terrain, backgrounds)
- `screen.py`: Pygame screen management and display updates

**Event System**
- `events.py`: EventHandler singleton managing click states (select, move, attack) and game interactions

**Resource Management (`resource/`)**
- `loader.py`: Image loading utilities for character and terrain sprites
- `characters/` and `terrains/`: PNG sprite assets

### Key Patterns

- **Observer Pattern**: Units subscribe to map updates for position changes
- **Factory Pattern**: Unit creation abstracted through type-specific factories  
- **Singleton Pattern**: EventHandler for centralized event management
- **State Machine**: Click modes (NOTHING, SELECTED, MOVING) for game interaction

### Game Logic Flow

1. Main loop (`main.py`) initializes screen, map, and event handler
2. Map generates background tiles, terrain blockers, and character units
3. EventHandler processes mouse clicks to select units and trigger movement
4. Characters can move within defined range using Manhattan distance pathfinding
5. Units support health systems, animation, and observer-based position updates

### Data Models

- Configuration uses Pydantic models for validation
- Tiles are Pydantic models with coordinate bounds checking  
- Units implement pygame.sprite.Sprite interface for rendering
- Pathfinding returns tile paths for character movement animation