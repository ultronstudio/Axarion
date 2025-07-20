
# 🎯 Axarion Studio Workflow Guide

**Modern Approach to 2D Game Development**

This document describes the complete workflow for working in Axarion Studio - from first launch to final game distribution. Learn to efficiently use all features of this professional game studio.

## 🚀 First Launch and Environment

### Starting Axarion Studio

```bash
python axarion_studio.py
```

### Studio Interface

**Main Areas:**
- **Menu Bar** - File, Edit, View, Build, Help
- **Toolbar** - Quick actions (New, Open, Save, Run, Build)
- **Project Explorer** (left) - project tree structure
- **Code Editor** (center) - main editor with IntelliSense
- **Properties Panel** (right) - selected object properties
- **Asset Manager Panel** - all game assets management
- **Console Output** (bottom) - errors, warnings, debug output

### Keyboard Shortcuts (mnemonics)

| Shortcut | Action | Tip |
|----------|--------|-----|
| `Ctrl+N` | **N**ew project | **N**ew |
| `Ctrl+O` | **O**pen project | **O**pen |
| `Ctrl+S` | **S**ave file | **S**ave |
| `F5` | Run game | F5 = **F**ast **5**-second run |
| `Shift+F5` | Build EXE | **Shift** = extra action |
| `Ctrl+Shift+A` | **A**sset Manager | **A**ssets |
| `Ctrl+F` | **F**ind in code | **F**ind |
| `Ctrl+/` | Toggle comment | / = slash comment |
| `F11` | **F**ullscreen | **F**ull |

## 📁 Project Management

### Creating New Project

1. **Start Studio:** `python axarion_studio.py`
2. **New project:** `Ctrl+N` or "New Project" button
3. **Enter details:**
   ```
   Project Name: My Awesome Game
   Location: ~/Projects/
   Template: [Game Type Template]
   Engine Version: Latest
   ```
4. **Studio creates structure:**
   ```
   My_Awesome_Game/
   ├── game.js                 # Entry point with template code
   ├── project.json           # Project configuration
   ├── assets/                # Asset Manager folders
   │   ├── images/            # PNG, JPG images
   │   ├── sounds/            # WAV, MP3 audio
   │   ├── music/            # Background music
   │   └── fonts/            # TTF font files
   ├── scenes/               # Game scenes (.js files)
   ├── scripts/              # Script files (.js)
   ├── components/           # Reusable components
   └── build/               # Build outputs
   ```

### Opening Existing Project

**Method 1: File menu**
- `File → Open Project` or `Ctrl+O`
- Navigate to `project.json` file

**Method 2: Recent projects**
- Studio remembers last 10 projects
- Quick access from welcome screen

**Method 3: Drag & Drop**
- Drag `project.json` into Studio window

### Project Explorer Navigation

**Icons and meanings:**
- 📁 **Folders** - expandable containers
- 🟨 **Script files** (.js) - editable scripts
- 🎮 **Game files** (.js) - game logic
- 🎨 **Asset files** - images, sounds with preview
- ⚙️ **Config files** - JSON configuration
- 🔨 **Build files** - compilation outputs

**Quick actions (right click):**
- **New File** - create new file
- **New Folder** - new folder
- **Rename** - rename item
- **Delete** - delete (with confirmation)
- **Open in Explorer** - open in system browser
- **Copy Path** - copy path to clipboard

## 🎨 Asset Manager Workflow

### Accessing Asset Manager

**Opening:**
- `Ctrl+Shift+A` - keyboard shortcut
- Folder icon in toolbar
- `View → Asset Manager` from menu

### Asset Manager Interface

**Left sidebar navigation:**
- 📁 **Local Assets** - your imported files
- 🏪 **Asset Store** - thousands of community assets

**Local Assets section:**
- **Images** - all images with previews
- **Sounds** - audio files with play buttons
- **Music** - longer audio tracks
- **Fonts** - fonts with samples
- **Other** - other files

### Asset Import (Drag & Drop)

**Basic import:**
1. **Open Asset Manager**
2. **Drag files** from Windows Explorer
3. **Studio automatically:**
   - Copies to correct folder
   - Creates image previews
   - Detects file type
   - Optimizes for game use

**Supported formats:**
```
Images: .png, .jpg, .jpeg, .gif, .bmp, .webp
Audio:  .wav, .mp3, .ogg, .m4a, .flac
Fonts:  .ttf, .otf
Data:   .json, .txt, .csv
```

**Batch import:**
- Select multiple files at once
- Drag entire folder
- Studio processes all supported files

### Asset Store Integration

**Browsing Asset Store:**
1. **Click Asset Store tab**
2. **Categories:**
   - Characters & Sprites
   - Backgrounds & Tiles  
   - Sound Effects
   - Music Tracks
   - UI Elements
   - Fonts & Typography

**Downloading assets:**
1. **Browse categories** or use search
2. **Preview assets** - preview before download
3. **Click "Download"** - automatic download and import
4. **Assets immediately available** in Local Assets

**Free vs Premium:**
- 🟢 **Free assets** - thousands freely available
- 🟡 **Premium assets** - higher quality, requires account

### Asset Organization Tips

**Naming conventions:**
```
player_idle.png          # Good: descriptive name
playerRunning001.png     # Good: animation with numbers
bg_forest_01.png         # Good: type_description_variant
image1.png               # Bad: non-descriptive name
```

**Folder structure:**
```
assets/
├── images/
│   ├── characters/      # Characters
│   ├── environments/    # Backgrounds and environments
│   ├── ui/             # UI elements
│   └── effects/        # Particle textures
├── sounds/
│   ├── sfx/            # Sound effects
│   └── voices/         # Voice samples
└── music/
    ├── menu/           # Menu music
    └── gameplay/       # Game music
```

## ✏️ Code Editor Workflow

### Editing Script Files

**Syntax highlighting:**
- Studio automatically recognizes JavaScript
- Colorful highlighting of keywords
- Indentation highlighting for better readability

**IntelliSense features:**
- **Auto-completion** - completion while typing
- **Function signatures** - function help
- **Error highlighting** - red underline for errors
- **Import suggestions** - import suggestions

**Useful features:**
```javascript
// IntelliSense recognizes Axarion objects
var engine = createEngine(800, 600);
var player = createGameObject("Player", "sprite");

// When typing player. available methods are shown
player.set|  // ← IntelliSense offers setSprite(), setProperty() etc.
```

### Script Editing

**When editing .js files:**
- **JavaScript syntax** highlighting
- **Function detection** - recognizes update(), init() functions
- **Built-in function help** - help for move(), keyPressed() etc.

**Snippets and templates:**
```javascript
// Type 'player' and press Tab for snippet:
var speed = 200;
function update() {
    if (keyPressed("ArrowLeft")) move(-speed * deltaTime(), 0);
    if (keyPressed("ArrowRight")) move(speed * deltaTime(), 0);
}
```

### Live Coding Features

**Auto-save:**
- Studio automatically saves changes every 30 seconds
- No work loss during crashes
- Unsaved changes indicator in tab

**Error detection:**
- Errors shown in real-time
- Error panel below shows details
- Click on error = jump to line with error

**Hot reload (experimental):**
- Some changes apply without game restart
- Script code changes
- Asset changes (new images, sounds)

## 🎮 Testing and Debugging

### Running the Game

**Basic run:**
- `F5` or "Run" button 
- Studio starts game in new window
- Console output in Studio panel

**Debug mode:**
- `Shift+F5` - starts with debug information
- Shows collision bounds, FPS counter
- More verbose logging

### Debugging Tools

**Console output:**
```javascript
// In your code use console.log() for debug
console.log("Player position: " + player.position.x + ", " + player.position.y);
console.log("Enemies count: " + enemies.length);

// Use print() in scripts
function update() {
    var pos = getProperty("position");
    print("X: " + pos.x + ", Y: " + pos.y);
}
```

**In-game debug controls:**
- `D` - toggle debug view (collision boxes)
- `F` - toggle performance stats
- `1-9` - custom debug hotkeys (programmable)

### Error Handling

**Common errors and solutions:**
```
❌ Error: Sprite 'missing.png' not found
✅ Solution: Check Asset Manager, reimport image

❌ Error: Cannot call update() on destroyed object
✅ Solution: Add null checks before function calls

❌ Error: Audio device not found
✅ Solution: Check system audio settings
```

## 🔨 Build and Deployment

### Build Preparation

**Pre-build checklist:**
1. ✅ All assets imported and used
2. ✅ No broken links to missing files
3. ✅ Game works in all tested scenarios
4. ✅ Icon and metadata set

### Build Process

**Method 1: GUI Build**
1. `Menu → Build → Create Executable`
2. Choose target platform
3. Configure build options
4. Click "Build"

**Method 2: Command line**
```bash
# From Studio directory
python build_studio.py

# With parameters
python build_studio.py --project "MyGame" --target windows
```

### Build Configuration

Studio creates `build_config.json`:
```json
{
    "project_name": "My Game",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "Awesome game description",
    "icon": "game_icon.png",
    "target_platforms": ["windows", "web"],
    "optimization": {
        "compress_assets": true,
        "minify_code": false,
        "remove_debug": true
    },
    "include": {
        "all_assets": true,
        "source_code": false,
        "documentation": true
    }
}
```

### Build Outputs

**Windows build:**
```
build/windows/
├── MyGame.exe           # Main executable
├── assets/              # Optimized assets
├── README.txt           # Instructions for players
└── LICENSE.txt          # License information
```

**Web build:**
```
build/web/
├── index.html           # Entry point
├── game.js              # Converted JavaScript
├── assets/              # Web-optimized assets
└── manifest.json        # PWA manifest
```

## 🚀 Deployment Workflow

### Local Testing

**Test built version:**
1. Navigate to `build/windows/`
2. Run `.exe` file
3. Test on clean system (without Studio)

### Replit Deployment

**Automatic deployment:**
```bash
python build_studio.py --deploy replit

# Studio creates:
# - Web-optimized version
# - Replit-compatible configuration  
# - Public URL for sharing
```

**Manual Replit setup:**
1. Upload `build/web/` content to Replit
2. Set main file to `index.html`
3. Configure web server in `.replit` file

### Distribution Tips

**Professional distribution:**
1. **Create installer** - use NSIS or Inno Setup
2. **Code signing** - digital signature for trust
3. **Auto-updater** - automatic update system
4. **Analytics** - usage statistics tracking

## 📊 Performance Optimization

### Studio Performance Tools

**Built-in profiler:**
- `View → Performance Monitor`
- Tracks FPS, memory usage, render time
- Identifies code bottlenecks

**Asset optimization:**
```javascript
// Texture optimization
optimizeImages({
    maxSize: {width: 1024, height: 1024},
    format: "PNG",
    quality: 95
});

// Audio optimization
optimizeAudio({
    format: "OGG",
    bitrate: 192,
    normalize: true
});
```

### Code Optimization Tips

**Efficient object management:**
```javascript
// ✅ Good: Object pooling
function BulletPool(size) {
    this.bullets = [];
    this.active = [];
    this.inactive = [];
    
    for (var i = 0; i < size; i++) {
        var bullet = this.createBullet();
        this.bullets.push(bullet);
        this.inactive.push(bullet);
    }
    
    this.getBullet = function() {
        if (this.inactive.length > 0) {
            var bullet = this.inactive.pop();
            this.active.push(bullet);
            return bullet;
        }
        return null;
    };
}

// ❌ Bad: Constant object creation
function shoot() {
    var bullet = createGameObject("Bullet", "circle"); // Costly!
}
```

## 🔄 Version Control Integration

### Git Workflow with Studio

**Setup Git:**
```bash
cd my_game_project
git init
git add .
git commit -m "Initial commit from Axarion Studio"
```

**Studio Git integration:**
- `View → Version Control` panel
- Visual diff for changes
- One-click commit and push
- Branch management

**Recommended `.gitignore`:**
```gitignore
# Build outputs
build/
dist/
*.exe

# Temporary files
*.tmp
*.cache
.axarion_temp/

# OS files
.DS_Store
Thumbs.db

# IDE settings
.vscode/
.idea/
```

## 🤝 Collaboration Workflow

### Multi-developer Setup

**Project sharing:**
1. **Setup Git repository** (GitHub, GitLab)
2. **Each dev clones project**
3. **Asset syncing** via Git LFS for large files
4. **Code review** process for changes

**Merge conflicts in Studio:**
- Studio detects conflicts automatically
- Visual merge tool for resolution
- Asset conflicts resolved via Asset Manager

### Team Organization

**Role assignment:**
- **Lead programmer** - main game logic
- **Artist** - asset creation and import
- **Sound designer** - audio implementation
- **Level designer** - scene creation

---

**This workflow guide covers 90% of daily work in Axarion Studio!** 

For advanced features and troubleshooting, check additional documentation or use the built-in help system (`F1`).

**Axarion Studio - Efficient workflow for modern game development!** 🎮⚡
