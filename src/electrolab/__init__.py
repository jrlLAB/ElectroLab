"""
ElectroLab library

"""

from . import fluid
from . import controller

__version__ = "0.0.2"
__author__ = 'Oliver Rodriguez, Nikita Lukhanin'

# modules to import when user does 'from electrolab import *':
__all__ = ['fluid', 'controller']
