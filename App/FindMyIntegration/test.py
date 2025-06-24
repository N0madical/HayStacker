import os
from os.path import dirname

print(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys", '*.keys'))