
# Axarion Engine Attribution Guide

## Why Attribution Matters

If you're using the Axarion Engine and want to show your support, you can choose to include a small credit in your game. **This is entirely optional and not required by the license.**

Attribution helps:
- Support the engine's development
- Show appreciation for the tools you're using
- Help other developers discover Axarion Engine

## Simple Text Attribution

You may display something like:

```
"Powered by Axarion Engine"
```

or

```
"Made with Axarion Engine"
```

This can be shown in:
- Your game's splash screen
- Credits menu
- About section
- Loading screen
- Anywhere else you find appropriate

## Code Implementation

If you're using Python with Axarion, here's a basic example of how you might display an attribution message on screen:

```python
def show_engine_credit(renderer, x=10, y=None):
    """Display Axarion Engine credit on screen"""
    text = "Powered by Axarion Engine"
    
    # Position at bottom of screen if y not specified
    if y is None:
        y = renderer.screen.get_height() - 30
    
    renderer.draw_text(text, x, y, (150, 150, 150))
```

### Usage Examples

**In your splash screen:**
```python
def show_splash_screen(engine):
    engine.renderer.clear()
    engine.renderer.draw_text("My Awesome Game", 100, 100, (255, 255, 255))
    show_engine_credit(engine.renderer)
    engine.renderer.present()
```

**In your credits scene:**
```python
def show_credits(engine):
    credits = [
        "Game Developer: Your Name",
        "Art: Your Artist",
        "Music: Your Composer",
        "",
        "Powered by Axarion Engine"
    ]
    
    for i, credit in enumerate(credits):
        y = 100 + i * 30
        engine.renderer.draw_text(credit, 50, y, (200, 200, 200))
```

## Creative Attribution Ideas

Feel free to get creative with your attribution:

- Include the Axarion logo (if you have one)
- Add it to your game's loading animation
- Include it in your game's documentation
- Mention it in your social media posts about the game
- Add it to your game's trailer or promotional materials

## Freedom of Choice

**Using this credit is fully optional.** We believe in freedom for developers.

Your projects are yours, and your decision to show attribution is appreciated but never enforced. The Axarion Engine is designed to empower your creativity without restrictions.

## Supporting the Project

If you want to support Axarion Engine beyond attribution:

- Share your games made with Axarion
- Report bugs and suggest improvements
- Contribute to the documentation
- Help other developers in the community
- Star the project repository (if available)

---

*Thank you for considering attribution! Every mention helps the Axarion Engine community grow.*
