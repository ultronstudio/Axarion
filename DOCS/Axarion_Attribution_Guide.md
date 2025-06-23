Optional Attribution Guide for Axarion Engine
Why Attribution Matters
If you're using the Axarion Engine and want to show your support, you can choose to include a small credit in
your game. This is entirely optional and not required by the license.
Example Text Attribution
You may display something like:
 "Powered by Axarion Engine"
This can be shown in your game's splash screen, credits, or anywhere else you find appropriate.
Optional Code Snippet
If you're using Python with Axarion, here is a basic example of how you might display an attribution message
on screen:
 def show_engine_credit(screen, font):
 text = "Powered by Axarion Engine"
 surface = font.render(text, True, (150, 150, 150))
 screen.blit(surface, (10, screen.get_height() - 30))
You can call this function at the end of your splash screen or in the credits scene.
Freedom of Choice
Using this credit is fully optional. We believe in freedom for developers.
Your projects are yours, and your decision to show attribution is appreciated but never enforc