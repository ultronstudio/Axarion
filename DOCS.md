
# 📚 Axarion Engine - Kompletní Dokumentace

## 🎮 Úvod

Axarion Engine je výkonný 2D herní engine navržený speciálně pro programátory, kteří preferují psaní her v čistém kódu bez grafických editorů.

## ✨ Klíčové Funkce

### 🎯 Core Features
- **Pure Code Approach**: Žádný GUI editor - hry se píší přímo v kódu
- **AXScript Integration**: Vestavěný skriptovací jazyk pro herní logiku
- **Asset Management**: Komplexní systém pro správu obrázků, zvuků a animací
- **Physics System**: Vestavěná 2D fyzikální simulace
- **Animation System**: Plynulé animace objektů
- **Particle Effects**: Exploze, oheň, kouř a další efekty

### 🎨 Asset Support
- **Obrázky**: PNG, JPG, GIF, BMP, TGA
- **Zvuky**: WAV, MP3, OGG, M4A
- **Animace**: Sprite sheets a složky s framy
- **Fonty**: TTF, OTF

## 🚀 Rychlý Start

### 1. Instalace a spuštění
```bash
# Spuštění demo hry
python test_fixed_engine.py

# Spuštění assets demo
python test_assets_demo.py

# Vytvoření sample assetů
python assets/create_sample_assets.py
```

### 2. Základní struktura hry
```python
from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager

# Vytvoření engine
engine = AxarionEngine(800, 600)
engine.initialize()

# Načtení assetů
asset_manager.load_all_assets()

# Vytvoření scény
scene = engine.create_scene("Main")
engine.current_scene = scene

# Vytvoření herního objektu
player = GameObject("Player", "sprite")
player.position = (100, 100)
player.set_sprite("ship")  # Použití sprite

# Spuštění hry
engine.run()
```

## 🎨 Asset Management

### Načítání Assetů

```python
from engine.asset_manager import asset_manager

# Načtení obrázku
asset_manager.load_image("ship", "assets/images/ship.png")

# Načtení zvuku
asset_manager.load_sound("laser", "assets/sounds/laser.wav")

# Načtení animace z složky
asset_manager.load_animation("explosion", "assets/animations/explosion/")

# Načtení sprite sheetu
asset_manager.load_sprite_sheet("player_walk", "sprites.png", 32, 48)

# Automatické načtení všech assetů
asset_manager.load_all_assets()
```

### Struktura Složek
```
assets/
├── images/          # Obrázky (.png, .jpg, .gif, .bmp)
├── sounds/          # Zvuky (.wav, .mp3, .ogg)
├── animations/      # Animace (složky s framy)
│   ├── explosion/
│   ├── spinning_coin/
│   └── engine_thrust/
└── fonts/           # Fonty (.ttf, .otf)
```

## 🎮 GameObject API

### Základní Vlastnosti
```python
# Vytvoření objektu
obj = GameObject("MyObject", "sprite")
obj.position = (100, 200)
obj.velocity = (50, 0)
obj.rotation = 45
obj.mass = 1.5
obj.friction = 0.3
obj.bounce = 0.8

# Tagy pro kategorizaci
obj.add_tag("enemy")
obj.add_tag("flying")
```

### Sprite a Animace
```python
# Nastavení sprite
obj.set_sprite("ship")

# Nastavení animace
obj.set_animation("explosion", speed=2.0, loop=False)

# Ovládání animace
obj.play_animation("walk")
obj.pause_animation()
obj.resume_animation()
obj.stop_animation()

# Přehrání zvuku
obj.play_sound("laser_shot")
```

### Fyzika
```python
# Aplikace síly
obj.apply_force(100, -200)

# Pohyb směrem k cíli
obj.move_towards((400, 300), speed=150)

# Otočení k pozici
obj.look_at((mouse_x, mouse_y))

# Detekce země/platformy
if obj.is_on_ground():
    obj.velocity = (obj.velocity[0], -jump_force)
```

## 📜 AXScript Reference

### Základní Funkce
```javascript
// Pohyb a rotace
move(dx, dy)              // Pohyb o offset
rotate(angle)             // Rotace o úhel
setProperty(name, value)  // Nastavení vlastnosti
getProperty(name)         // Získání vlastnosti

// Pozice a transformace
var pos = getProperty("position");
setProperty("position", {x: 100, y: 200});
setProperty("rotation", 45);
setProperty("scale", {x: 1.5, y: 1.5});
```

### Input Systém
```javascript
// Klávesnice
if (keyPressed("Space")) {          // Klávesa stisknuta
    jump();
}
if (keyJustPressed("Enter")) {      // Klávesa právě stisknuta
    startGame();
}

// Myš
if (mousePressed(0)) {              // Levé tlačítko myši
    shoot();
}
var mousePos = getMousePos();       // Pozice myši
```

### Matematické Funkce
```javascript
// Základní matematika
var result = sin(angle);
var distance = sqrt(dx*dx + dy*dy);
var randomValue = random();         // 0-1
var clamped = clamp(value, 0, 100);

// Užitečné funkce
var dist = distance(x1, y1, x2, y2);
var angle = atan2(dy, dx) * 180 / Math.PI;
```

### Audio
```javascript
// Zvukové efekty
playSound("explosion");
playSound("music", -1);             // Opakovat nekonečně

// Hudba
playMusic("background.mp3");
stopMusic();
setVolume(0.7, 0.5);               // Hudba, efekty
```

### Animace a Efekty
```javascript
// Animace objektu
setAnimation("walk", 1.5, true);    // Název, rychlost, loop
playAnimation("jump");
pauseAnimation();

// Částicové efekty
createExplosion(x, y, size);
createSmoke(x, y, duration);
```

## 🎯 Typy Objektů

### rectangle
```python
obj = GameObject("Box", "rectangle")
obj.set_property("width", 100)
obj.set_property("height", 50)
obj.set_property("color", (255, 0, 0))
```

### circle
```python
obj = GameObject("Ball", "circle")
obj.set_property("radius", 25)
obj.set_property("color", (0, 255, 0))
```

### sprite
```python
obj = GameObject("Player", "sprite")
obj.set_sprite("player_idle")  # Načte obrázek
```

### animated_sprite
```python
obj = GameObject("Character", "animated_sprite")
obj.set_animation("walk_cycle", speed=1.0, loop=True)
```

## 🎨 Renderer API

### Základní Kreslení
```python
# Přístup k rendereru
renderer = engine.renderer

# Základní tvary
renderer.draw_rect(x, y, width, height, color)
renderer.draw_circle(x, y, radius, color)
renderer.draw_line(x1, y1, x2, y2, color, width)

# Sprite
renderer.draw_sprite(x, y, sprite_surface, rotation)

# Text
renderer.draw_text("Hello World", x, y, color, font)
```

### Kamera
```python
# Nastavení kamery
renderer.set_camera(x, y)
renderer.move_camera(dx, dy)

# Sledování objektu
renderer.follow_object(player, offset_x=0, offset_y=-100)

# Převod souřadnic
world_pos = renderer.screen_to_world(screen_x, screen_y)
screen_pos = renderer.world_to_screen(world_x, world_y)
```

### Debug Režim
```python
# Debug funkce
renderer.enable_debug(True)
renderer.show_object_bounds(True)
renderer.show_velocity_vectors(True)
```

## 🔧 Scene Management

### Vytvoření Scény
```python
# Nová scéna
scene = Scene("Level1")
scene.set_gravity(0, 400)          # Gravitace
scene.set_bounds(0, 0, 1200, 800)  # Hranice světa

# Přidání objektů
scene.add_object(player)
scene.add_object(enemy)

# Získání objektů
player = scene.get_object("Player")
enemies = scene.get_objects_with_tag("enemy")
```

### Správa Scén v Engine
```python
# Vytvoření a přepínání scén
main_scene = engine.create_scene("Main")
menu_scene = engine.create_scene("Menu")

engine.current_scene = main_scene
engine.switch_scene("Menu")
```

## 🎵 Audio System

### Načítání Zvuků
```python
from engine.asset_manager import asset_manager

# Načtení zvukových efektů
asset_manager.load_sound("jump", "sounds/jump.wav", volume=0.8)
asset_manager.load_sound("coin", "sounds/coin.wav")

# Přehrání
asset_manager.play_sound("jump")
```

### Hudba
```python
# Nastavení a přehrání hudby
from engine.audio_system import audio_system

audio_system.load_music("music/background.mp3")
audio_system.play_music(loops=-1)  # Nekonečné opakování
audio_system.set_music_volume(0.6)
```

## 💫 Animation System

### Jednoduché Animace
```python
from engine.animation_system import animation_system

# Pohyb k pozici
animation_system.move_to(obj, target_x, target_y, duration=2.0)

# Rotace
animation_system.rotate_to(obj, 180, duration=1.0)

# Změna velikosti
animation_system.scale_to(obj, 2.0, 2.0, duration=0.5)

# Efekty
animation_system.bounce(obj, height=50, duration=1.0)
animation_system.pulse(obj, scale_factor=1.5, duration=0.8)
```

### Easing Funkce
```python
from engine.animation_system import Easing

# Různé typy easing
animation_system.move_to(obj, x, y, 2.0, Easing.ease_out_quad)
animation_system.rotate_to(obj, 360, 3.0, Easing.bounce_out)
animation_system.scale_to(obj, 0.5, 0.5, 1.0, Easing.ease_in_out_quad)
```

## 🎪 Particle System

### Základní Efekty
```python
from engine.particle_system import particle_system

# Exploze
particle_system.create_explosion(x, y, particle_count=50)

# Kouř
particle_system.create_smoke(x, y, duration=3.0)

# Vlastní částice
particle_system.emit_particles(
    x, y, 
    count=20,
    velocity_range=(50, 100),
    color=(255, 100, 0),
    lifetime=2.0
)
```

## 🎯 Kompletní Příklad: Space Shooter

```python
#!/usr/bin/env python3
"""
Kompletní příklad: Space Shooter hra
"""

from engine.core import AxarionEngine
from engine.game_object import GameObject
from engine.asset_manager import asset_manager

def create_space_shooter():
    # Inicializace
    engine = AxarionEngine(800, 600)
    engine.initialize()
    
    # Načtení assetů
    asset_manager.load_all_assets()
    
    # Vytvoření scény
    scene = engine.create_scene("SpaceShooter")
    engine.current_scene = scene
    
    # Hráčova loď
    player = GameObject("Player", "sprite")
    player.position = (400, 500)
    player.set_sprite("ship")
    player.mass = 1.0
    player.add_tag("player")
    
    # Ovládání hráče
    player.script_code = """
var speed = 200;
var shootCooldown = 0;

function update() {
    shootCooldown -= 0.016;
    
    // Pohyb
    if (keyPressed("ArrowLeft")) {
        move(-speed * 0.016, 0);
    }
    if (keyPressed("ArrowRight")) {
        move(speed * 0.016, 0);
    }
    
    // Střelba
    if (keyPressed("Space") && shootCooldown <= 0) {
        var pos = getProperty("position");
        createBullet(pos.x + 16, pos.y);
        playSound("laser");
        shootCooldown = 0.2;
    }
    
    // Hranice
    var pos = getProperty("position");
    if (pos.x < 0) setProperty("position", {x: 0, y: pos.y});
    if (pos.x > 768) setProperty("position", {x: 768, y: pos.y});
}

function createBullet(x, y) {
    // Vytvořit projektil
    var bullet = instantiate("circle", x, y);
    bullet.setProperty("radius", 3);
    bullet.setProperty("color", [255, 255, 0]);
    bullet.setProperty("velocity", {x: 0, y: -400});
    bullet.addTag("bullet");
}
"""
    
    scene.add_object(player)
    
    # Nepřátelé
    for i in range(5):
        enemy = GameObject(f"Enemy_{i}", "sprite")
        enemy.position = (100 + i * 120, 100)
        enemy.set_sprite("enemy")
        enemy.velocity = (50, 0)
        enemy.add_tag("enemy")
        
        enemy.script_code = f"""
var direction = 1;
var moveSpeed = 50;

function update() {{
    var pos = getProperty("position");
    var vel = getProperty("velocity");
    
    // Bounce off sides
    if (pos.x <= 0 || pos.x >= 772) {{
        direction *= -1;
        pos.y += 30;
        setProperty("position", {{x: pos.x, y: pos.y}});
    }}
    
    setProperty("velocity", {{x: direction * moveSpeed, y: 0}});
}}
"""
        scene.add_object(enemy)
    
    return engine

# Spuštění hry
if __name__ == "__main__":
    engine = create_space_shooter()
    engine.run()
```

## 🔧 Pokročilé Funkce

### Custom Game Systems
```python
class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.lives = 3
    
    def add_score(self, points):
        self.score += points
    
    def lose_life(self):
        self.lives -= 1
        return self.lives <= 0

# Přidání do engine
score_system = ScoreSystem()
engine.add_game_system(score_system)
```

### Event System
```python
# Registrace událostí
engine.subscribe_event("enemy_destroyed", on_enemy_destroyed)
engine.subscribe_event("player_died", on_player_died)

# Emitování událostí
engine.emit_event("enemy_destroyed", {"points": 100})

def on_enemy_destroyed(data):
    score_system.add_score(data["points"])
```

### Uložení a Načítání
```python
# Uložení hry
engine.save_game("savegame.json")

# Načtení hry
engine.load_game("savegame.json")

# Export/Import projektů
from utils.file_manager import FileManager
fm = FileManager()
fm.export_project_archive("my_game", "game.zip")
fm.import_project_archive("game.zip", "imported_games/")
```

## 🎮 Tipy a Triky

### Optimalizace Výkonu
```python
# Culling objektů mimo obrazovku
for obj in scene.get_all_objects():
    if renderer.is_on_screen(obj):
        obj.update(delta_time)

# Batch rendering podobných objektů
# Použití object poolingu pro často vytvářené objekty
```

### Debugování
```python
# Debug informace
obj.show_debug = True

# Console output v skriptech
print("Debug info: " + someVariable);

# Performance monitoring
engine.show_performance_stats = True
```

### Složitější Kolize
```python
# Vlastní kolizní detekce
def custom_collision_check(obj1, obj2):
    # Implementace vlastní logiky
    return collision_detected

# Collision layers
scene.add_collision_layer("enemies", enemy_objects)
scene.add_collision_layer("bullets", bullet_objects)
```

## 🚀 Deployment

### Příprava pro Distribuci
```python
# Optimalizace assetů
asset_manager.optimize_assets()

# Komprese obrázků
asset_manager.compress_images(quality=85)

# Export finální hry
engine.export_game("my_game_final/")
```

---

## 📞 Podpora a Komunita

- **GitHub**: [Axarion Engine Repository](https://github.com/your-repo/axarion-engine)
- **Dokumentace**: Tento soubor + inline komentáře v kódu
- **Příklady**: Složka `examples/` obsahuje ukázkové projekty

---

## 🎉 Závěr

Axarion Engine poskytuje výkonný a flexibilní framework pro tvorbu 2D her s důrazem na code-first přístup. S kompletním asset managementem, physics systemem a AXScript jazykem můžete vytvářet komplexní hry rychle a efektivně.

Začněte s jednoduchými příklady a postupně se propracujte k pokročilejším funkcím. Dokumentace je živý dokument - přidávejte vlastní poznámky a vylepšení!

**Happy Coding! 🎮**
