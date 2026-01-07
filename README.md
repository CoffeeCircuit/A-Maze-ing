*This project has been created as part of the 42 curriculum by abalcu, ksmailov.*

# A-Maze-ing 🌀

A Python-based maze generator that creates perfect or imperfect mazes with interactive terminal visualization. This project implements multiple maze generation algorithms and provides a reusable library for maze generation in other projects.

## 📖 Description

A-Maze-ing is a command-line maze generation tool that:
- 🎲 Generates random mazes using configurable algorithms (DFS and Hunt-and-Kill)
- 🎯 Creates perfect mazes (single path between entry and exit) or imperfect mazes (multiple paths)
- 💾 Outputs mazes in a hexadecimal wall representation format
- 🖥️ Provides an interactive terminal-based visualization with color customization
- 🔍 Includes BFS-based pathfinding for shortest path calculation
- 🎨 Embeds a visible "42" pattern using fully closed cells (when maze size permits)
- 📦 Packages maze generation logic as a reusable Python library (via wheel file)

The project emphasizes clean code architecture, type safety with mypy, and modern Python development practices.

---

## ✨ Features

- **Two maze generation algorithms:**
  - 🌳 Depth-First Search (DFS) with recursive backtracking
  - 🎯 Hunt-and-Kill algorithm for varied maze structures
- **Perfect and imperfect maze support**
- **Reproducible generation** with optional seed parameter
- **Interactive terminal visualizer** with:
  - Real-time maze regeneration
  - Show/hide solution path toggle
  - Customizable colors for walls, path, and "42" logo
  - Clean Unicode box-drawing character rendering
- **Shortest path calculation** using Breadth-First Search (BFS)
- **"42" logo pattern** integrated into maze structure
- **Reusable library** packaged as a pip-installable wheel

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or later
- `uv` package manager (will be installed automatically if missing)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/CoffeeCircuit/A-Maze-ing.git
cd A-Maze-ing

# Build the package
make build

# Install dependencies and set up environment
make install
```

---

## 🎮 Usage

### Running the Program

```bash
# Run with default configuration
make run config.txt

# Or run directly with Python
python3 a_maze_ing.py config.txt
```

### Interactive Visualizer Controls

Once the visualizer opens:

```
┌─────────────────────────────────────┐
│  Interactive Menu:                  │
│  [N] - Generate new maze            │
│  [C] - Change colors                │
│  [P] - Toggle path visibility       │
│  [Q] - Quit                         │
└─────────────────────────────────────┘
```

### Configuration Example

Create or edit `config.txt`:

```bash
# Edit configuration interactively
make config
```

Example configuration:

```ini
# Maze dimensions
WIDTH=25
HEIGHT=20

# Entry and exit points
ENTRY=0,0
EXIT=24,19

# Output settings
OUTPUT_FILE=maze.txt
PERFECT=False

# Optional: Reproducibility and algorithm choice
SEED=42
ALGORITHM=hak
```

### Makefile Targets

```bash
make build         # Build the mazegen wheel package
make install       # Install dependencies and setup venv
make run           # Run the maze generator
make debug         # Run in debug mode (pdb)
make config        # Edit configuration file
make lint          # Run flake8 and mypy
make lint-strict   # Run strict mypy checks
make clean         # Remove cache and generated files
make fclean        # Removes the wheel file (used in development)
make uninstall     # Remove all dependencies
make help          # Show all available targets
```

---

## 📋 Configuration File Structure

The configuration file uses a simple `KEY=VALUE` format. Lines starting with `#` are comments.

### Mandatory Keys

| Key | Description | Example | Valid Values |
|-----|-------------|---------|--------------|
| `WIDTH` | Maze width in cells | `WIDTH=25` | Integer > 0 |
| `HEIGHT` | Maze height in cells | `HEIGHT=20` | Integer > 0 |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` | Valid cell coords |
| `EXIT` | Exit coordinates (x,y) | `EXIT=24,19` | Valid cell coords |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` | Any valid filename |
| `PERFECT` | Perfect maze flag | `PERFECT=True` | True/False |

### Optional Keys

| Key | Description | Example | Valid Values |
|-----|-------------|---------|--------------|
| `SEED` | Random seed | `SEED=42` | Any integer |
| `ALGORITHM` | Algorithm choice | `ALGORITHM=hak` | `dfs` or `hak` |

---

## 📄 Output File Format

The maze is encoded using hexadecimal digits where each digit represents a cell's walls using bit flags.

### Wall Encoding System

```
     N (bit 0)
        |
 W ─────█───── E (bit 1)
(bit 3) |
        S (bit 2)
```

| Bit Position | Wall Direction | Binary Value |
|--------------|----------------|--------------|
| 0 (LSB) | North | 0001 |
| 1 | East | 0010 |
| 2 | South | 0100 |
| 3 | West | 1000 |

**Examples:**
- `9` (binary `1001`) = North ✓ + West ✓ walls closed
- `A` (binary `1010`) = East ✓ + West ✓ walls closed
- `F` (binary `1111`) = All walls closed (used for "42" pattern)
- `0` (binary `0000`) = All walls open

### File Structure

```
BBCA96CA...    ← Maze grid (hexadecimal)
9515391539...
...

0, 0           ← Entry coordinates
24, 19         ← Exit coordinates
EESSEESSWW...  ← Shortest path (N/E/S/W)
```

### Example Output

```
9515391539551795151151153
EBABAE812853C1412BA812812
96A8416A84545412AC4282C2A
...

1,1
19,14
SWSESWSESWSSSEESEEENESESESSEESSSEEEENNENE
```

---

## 🧠 Maze Generation Algorithms

### 1. Depth-First Search (DFS) - Recursive Backtracker

**Implementation:** [`mazegen/dfs.py`](mazegen/dfs.py)

```python
# Usage
ALGORITHM=dfs
```

**How it works:**
1. Start at the entry point
2. Randomly choose an unvisited neighbor
3. Carve a passage by removing walls
4. Recursively visit the new cell
5. Backtrack when stuck

**Characteristics:**
- ✅ Creates long, winding corridors ("river" factor)
- ✅ Memory efficient (iterative stack-based)
- ✅ Guaranteed perfect mazes
- ✅ Natural maze-solving intuition

**Why we chose DFS:**
- Simple and elegant implementation
- Produces aesthetically pleasing mazes with long passages
- Well-established algorithm with proven correctness
- Easy to understand and maintain

### 2. Hunt-and-Kill Algorithm

**Implementation:** [`mazegen/hak.py`](mazegen/hak.py)

```python
# Usage
ALGORITHM=hak
```

**How it works:**
1. **Kill Phase:** Random walk carving passages until dead end
2. **Hunt Phase:** Scan for unvisited cell next to visited cell
3. Repeat until all cells visited

**Characteristics:**
- ✅ Creates different texture than DFS
- ✅ Shorter dead ends, more branching
- ✅ Better balance of difficulty
- ✅ More uniform passage distribution

**Why we added Hunt-and-Kill:**
- Provides algorithmic variety
- Demonstrates versatility
- Better for certain maze topologies
- Interesting for comparative analysis

### Imperfect Maze Generation

**Implementation:** [`mazegen/imperfect.py`](mazegen/imperfect.py)

```python
# Usage
PERFECT=False
```

When `PERFECT=False`:
1. Generate a perfect maze first
2. Identify dead ends
3. Randomly remove walls (10-15% by default, can be editted by setting other probability)
4. Creates loops and multiple paths

### Pathfinding Algorithm

**Implementation:** [`pathfinder.py`](pathfinder.py)

Uses **Breadth-First Search (BFS)**:
- ✅ Guarantees shortest path
- ✅ O(V + E) time complexity
- ✅ Universal design (works with any maze)
- ✅ Reads from output file format

---

## 📦 Using MazeGen as a Library

### Installation

```bash
# Install the wheel package
pip install mazegen-0.7.0-py3-none-any.whl
```

### Basic Usage

```python
from mazegen import MazeGenerator

# Create and configure generator
maze = MazeGenerator()
maze.width = 25
maze.height = 20
maze.entry = (0, 0)
maze.exit = (24, 19)
maze.perfect = True
maze.seed = 42          # Optional: reproducibility
maze.algorithm = "dfs"  # or "hak"

# Generate the maze
maze.generate()

# Access the grid
grid = maze.grid  # list[list[int]] with wall bitmasks

# Write to file
maze.output = "output.txt"
maze.write()
```

### Loading from Configuration

```python
from mazegen import MazeGenerator

# Load configuration from file
maze = MazeGenerator()
maze.read("config.txt")

# Generate and save
maze.generate()
maze.write()
```

### Advanced Usage with Visualization

```python
from mazegen import MazeGenerator, Visualizer

# Generate maze
maze = MazeGenerator()
maze.read("config.txt")
maze.generate()
maze.write()

# Visualize interactively
vis = Visualizer()
vis.read(maze.output)
regenerate, new_seed = vis.render()

# Handle regeneration
if regenerate:
    maze.seed = new_seed
    maze.reset()
    maze.generate()
```

### Accessing Maze Data

```python
from mazegen import MazeGenerator

maze = MazeGenerator()
maze.read("config.txt")
maze.generate()

# Access configuration
width = maze.width      # int
height = maze.height    # int
entry = maze.entry      # tuple[int, int]
exit = maze.exit        # tuple[int, int]
is_perfect = maze.perfect  # bool

# Access grid data
grid = maze.grid  # list[list[int]]

# Check specific cell walls
cell_walls = grid[0][0]  # int (0-15)
has_north_wall = bool(cell_walls & (1 << 0))
has_east_wall = bool(cell_walls & (1 << 1))
has_south_wall = bool(cell_walls & (1 << 2))
has_west_wall = bool(cell_walls & (1 << 3))
```

### Package Exports

```python
from mazegen import (
    MazeGenerator,      # Main generator class
    Visualizer,         # Terminal visualizer
    Graphics,           # ANSI utilities
    dfs,                # DFS algorithm
    hak,                # Hunt-and-Kill algorithm
    make_imperfect,     # Imperfect converter
    make_p42_mask,      # 42 pattern mask
)
```

---

## 🔧 What Parts are Reusable for Future Projects

The `mazegen` library is designed to be integrated into any Python project that needs procedural maze generation. Here's what can be reused:

### Fully Reusable Components

#### 1. **MazeGenerator Class** - Core maze generation
```python
from mazegen import MazeGenerator

# Can be used in any project needing mazes
maze = MazeGenerator()
maze.width = 20
maze.height = 15
maze.generate()
grid = maze.grid  # Access generated maze data
```

**Use cases:**
- Game level generation (roguelikes, puzzle games, strategy games)
- Educational tools (algorithm visualization, teaching)
- Procedural content generation
- Random map generation for simulations

#### 2. **Generation Algorithms** - Standalone algorithm implementations
```python
from mazegen import dfs, hak

# Direct algorithm usage
dfs(maze)  # Depth-first search with long corridors
hak(maze)  # Hunt-and-kill with balanced structure
```

**Use cases:**
- Comparing algorithm performance
- Custom algorithm pipelines
- Research and benchmarking
- Teaching graph algorithms

#### 3. **PathFinder Module** - BFS shortest path calculator
```python
from pathfinder import PathFinder

# Works with any maze following the output format
finder = PathFinder("maze_output.txt")
shortest_path = finder.find_path()  # Returns "NESW" string
```

**Use cases:**
- AI navigation in games
- Solution hint systems
- Maze difficulty rating
- Automated testing of mazes

#### 4. **Output Format Specification** - Standard maze encoding
- Hexadecimal wall representation (bit flags)
- Documented in README for interoperability
- Can be read/written by any project

**Use cases:**
- Maze sharing between projects
- Level editors and converters
- Save/load game states
- Cross-project compatibility

#### 5. **Utility Functions**
```python
from mazegen import make_imperfect, make_p42_mask

# Create loops in perfect mazes
make_imperfect(maze, blocked=None, probability=0.5)

# Apply custom masks (can adapt for any pattern)
blocked_cells = make_p42_mask(maze)
```

**Use cases:**
- Adjusting maze difficulty
- Creating themed patterns
- Custom obstacle placement
- Special game mechanics

### What is Project-Specific (Not Reusable)

- `a_maze_ing.py` - CLI tool specific to this project
- Configuration file parser - May need adaptation
- Terminal visualizer UI - Terminal-specific implementation
- "42" pattern specifics - School project requirement

### Integration Guide for Future Projects

**Step 1: Install the package**
```bash
pip install mazegen-0.7.0-py3-none-any.whl
```

**Step 2: Import components**
```python
from mazegen import MazeGenerator
```

**Step 3: Configure and generate**
```python
maze = MazeGenerator()
maze.width = 25
maze.height = 20
maze.entry = (0, 0)
maze.exit = (24, 19)
maze.seed = 42           # Optional: reproducible
maze.algorithm = "dfs"   # or "hak"
maze.perfect = True      # or False for loops
maze.generate()
```

**Step 4: Access the data**
```python
# Get the grid (list[list[int]] - wall bitmasks)
grid = maze.grid

# Check walls for any cell
cell = grid[y][x]
has_north_wall = bool(cell & (1 << 0))
has_east_wall = bool(cell & (1 << 1))
has_south_wall = bool(cell & (1 << 2))
has_west_wall = bool(cell & (1 << 3))
```

**Step 5: Convert to your format**
```python
# Example: Convert to a different game format
game_grid = []
for y, row in enumerate(maze.grid):
    for x, walls in enumerate(row):
        game_cell = {
            'position': (x, y),
            'walls': walls,
            'walkable': walls != 15,  # Not fully blocked
        }
        game_grid.append(game_cell)
```

### Why This Design is Reusable

| Design Aspect | Benefit for Reusability |
|---------------|------------------------|
| **Zero dependencies** | No version conflicts with other projects |
| **Type hints** | Easy integration with type-checked codebases |
| **Modular** | Import only what you need |
| **Documented format** | Standard hex encoding well-specified |
| **Seed support** | Reproducible generation for testing |
| **Algorithm choice** | Flexibility for different maze styles |
| **Clean API** | Simple, intuitive method names |

---

## 👥 Team and Project Management

### Team Members and Roles

#### **ksmailov**
- 🔧 Implemented Hunt-and-Kill algorithm
- 🔍 Developed pathfinding module (BFS-based)
- 🎲 Created imperfect maze generation logic
- 🛠️ Designed and implemented Makefile
- 📝 Documentation and README preparation

#### **abalcu**
- 🌳 Implemented DFS (recursive backtracking) algorithm
- 🖥️ Developed interactive terminal visualizer
- 🎨 Created "42" pattern masking system
- 📦 Built package structure and wheel distribution
- 🔄 Project refactoring and code organization

#### **Collaborative Work**
- 🤝 Main program (`a_maze_ing.py`) integration
- ⚙️ Configuration parser design
- 💾 Output file format implementation
- 🔍 Code review and debugging
- ✅ Testing and validation

### Project Timeline

#### **Anticipated Planning (2 weeks)**
```
Week 1: Research → Design → Setup
Week 2: Implement → Test → Document
```

#### **Actual Evolution**

```
Phase 1 (Days 1-3):   Project setup, config parser, maze structure
Phase 2 (Days 4-6):   Parallel dev - algorithms + visualizer
Phase 3 (Days 7-9):   Pathfinding, 42 pattern, imperfect mazes
Phase 4 (Days 10-12): Integration, refactoring, packaging
Phase 5 (Days 13-14): Testing, documentation, polish
```

**Delays caused by:**
- Learning Python packaging (pyproject.toml, wheels)
- Visualizer polish (menus, ANSI sequences)
- Git workflow coordination

### What Worked Well ✅

- ✅ **Clear division of responsibilities** - Each member owned specific modules
- ✅ **Parallel development** - No blocking dependencies
- ✅ **Modular architecture** - Easy component integration
- ✅ **Regular communication** - Daily syncs prevented issues
- ✅ **Modern tooling** - `uv` streamlined workflow
- ✅ **Type hints from start** - Caught bugs early

### What Could Be Improved ⚠️

- ⚠️ **Earlier integration testing** - Would catch issues sooner
- ⚠️ **More detailed initial design** - Avoided some refactoring
- ⚠️ **Git workflow planning** - Reduce merge conflicts
- ⚠️ **Documentation alongside code** - Not at the end
- ⚠️ **Test-driven development** - Write tests earlier

### Tools Used

| Category | Tools |
|----------|-------|
| **Version Control** | Git, GitHub |
| **Package Management** | uv (modern Python manager) |
| **Linting/Type Checking** | flake8, mypy |
| **Development** | Python 3.11, venv |
| **Communication** | Whatsapp |
| **Documentation** | Markdown, Google-style docstrings |
| **Debugging** | pdb, print debugging |

---

## 📚 Resources

### Documentation
- [Python Official Documentation](https://docs.python.org/3/) - Complete Python reference
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/) - Docstring standards
- [Type Hints (typing module)](https://docs.python.org/3/library/typing.html) - Type annotation guide
- [Python Packaging Guide](https://packaging.python.org/en/latest/) - Building and distributing packages

### Maze Generation Algorithms
- [Wikipedia - Maze Generation](https://en.wikipedia.org/wiki/Maze_generation_algorithm) - Algorithm overview
- [Jamis Buck's Mazes Blog](https://weblog.jamisbuck.org/2011/2/7/maze-generation-recursive-backtracking) - DFS deep dive
- [Think Labyrinth - Maze Algorithms](http://www.astrolog.org/labyrnth/algrithm.htm) - Comprehensive algorithm reference
- [Maze Generation on Rosetta Code](https://rosettacode.org/wiki/Maze_generation) - Implementation examples

### Pathfinding Algorithms
- [BFS Algorithm - GeeksforGeeks](https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/) - BFS tutorial
- [Graph Traversal Visualized](https://visualgo.net/en/dfsbfs) - Interactive visualization
- [Red Blob Games - Pathfinding](https://www.redblobgames.com/pathfinding/a-star/introduction.html) - Comprehensive guide
- [Shortest Path Algorithms](https://cp-algorithms.com/graph/breadth-first-search.html) - Competitive programming reference

### Python Best Practices
- [Real Python - Tutorials](https://realpython.com/) - High-quality Python tutorials
- [Effective Python](https://effectivepython.com/) - Best practices book
- [Flake8 Documentation](https://flake8.pycqa.org/) - Style guide enforcement
- [Mypy Documentation](https://mypy.readthedocs.io/) - Static type checking

### Terminal/ANSI Programming
- [ANSI Escape Codes Gist](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797) - Complete ANSI reference (used in our visualizer)
- [Terminal Control Sequences](https://www.gnu.org/software/screen/manual/html_node/Control-Sequences.html) - Terminal programming guide

### AI Usage

**Tools Used:** ChatGPT (GPT-4), GitHub Copilot

**Tasks Assisted by AI:**

| Task | How AI Helped | Our Validation |
|------|---------------|----------------|
| **Algorithm implementation** | Translated pseudocode to Python | Manual tracing, tested various sizes |
| **Type hints** | Generated complex type annotations | Ran mypy strict, understood all types |
| **Documentation** | Docstring templates, README structure | Reviewed accuracy, added specifics |
| **Debugging** | Analyzed errors, suggested fixes | Understood root cause, tested fixes |
| **ANSI codes** | Quick reference lookup | Tested all sequences in terminal |
| **Makefile syntax** | Rule patterns, phony targets | Tested all targets, understood each |

**Our Validation Process:**
1. ✅ Read and analyze before accepting
2. ✅ Refactor to match our architecture
3. ✅ Add comprehensive comments
4. ✅ Test edge cases
5. ✅ Peer review all changes

**What We Built Ourselves:**
- Core algorithm logic and maze structure
- Integration between all components
- Configuration system design
- "42" pattern masking
- Visualizer menu system
- Output format implementation

---

## 🧪 Testing

### Running Tests

```bash
# Code quality checks
make lint

# Strict type checking
make lint-strict

# Debug mode
make debug config.txt
```

### Manual Testing Checklist

```bash
# Test different configurations
make run ARG=config.txt

# Test with different seeds
echo "SEED=42" >> config.txt
make run config.txt

# Test both algorithms
sed -i '' 's/ALGORITHM=.*/ALGORITHM=dfs/' config.txt
make run config.txt
```

### Validation

The subject provides a validation script to check output coherency. Test your generated mazes:

```bash
python output_validator.py output.txt
```

---

## 📂 Project Structure

```
A-Maze-ing/
├── 📄 a_maze_ing.py              # Main entry point
├── 🔍 pathfinder.py              # BFS pathfinding module
├── ⚙️  config.txt                # Default configuration
├── 🛠️  Makefile                  # Build automation
├── 📦 pyproject.toml             # Package metadata
├── 📖 README.md                  # This file
├── 🎯 mazegen/                   # Reusable library package
│   ├── __init__.py
│   ├── mazegen.py               # MazeGenerator class
│   ├── dfs.py                   # DFS algorithm
│   ├── hak.py                   # Hunt-and-Kill algorithm
│   ├── imperfect.py             # Imperfect maze logic
│   ├── mask_42.py               # "42" pattern masking
│   └── visualizer.py            # Terminal visualization
└── 📦 mazegen*.whl              # Installable package
```

---

## ⚠️ Known Issues and Limitations

- 🔸 "42" pattern requires minimum 7×7 maze (warning displayed for smaller)
- 🔸 Terminal visualizer requires ANSI support (works on macOS/Linux)
- 🔸 Large mazes (>100×100) may have slower visualization
- 🔸 Windows terminal may need additional configuration for Unicode characters

---

## 🚧 Future Improvements

- [ ] Add more algorithms (Prim's, Kruskal's, Eller's, Wilson's)
- [ ] Improve maze solving animation (show alternative paths when available)
- [ ] Support hexagonal and circular maze topologies
- [ ] MLX-based graphical visualization
- [ ] Web interface using Flask
- [ ] 3D maze generation
- [ ] Export to image formats (PNG, SVG)
- [ ] Configurable "42" pattern (custom logos)

---

## 📜 License

This project is part of the 42 curriculum and follows school guidelines.

---

## 👨‍💻 Authors

**abalcu** - [@CoffeeCircuit](https://github.com/CoffeeCircuit)  
**ksmailov** - [@ksr2code](https://github.com/ksr2code)

---

<div align="center">

**Made with ☕ and 🧠 at 42 Heilbronn**

*"A labyrinth is not a place to be lost, but a path to be found."*

</div>
