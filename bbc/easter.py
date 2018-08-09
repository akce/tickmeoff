import random

random.seed()

cookies = [
    # What a legend!
    'Go hard or go home',
    'Hey Charger',
    # Billy Madison
    'Principal: Mr. Madison, what you’ve just said is one of the most insanely idiotic things I have ever heard. At no point in your rambling, incoherent response were you even close to anything that could be considered a rational thought. Everyone in this room is now dumber for having listened to it. I award you no points, and may God have mercy on your soul.',
    # Burgundy
    'I love lamp',
    'Stay classy',
    ]

def getcookie():
    return random.choice(cookies)
