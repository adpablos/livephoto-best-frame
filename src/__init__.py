"""
LivePhoto Best Frame Picker package.
A tool for managing iPhone Live Photos and their metadata.
"""

__version__ = "0.1.0"
__author__ = "Alex de Pablos"
__email__ = "alex@alexdepablos.com"

# Expose main classes for easier imports
from .metadata_handler import MetadataHandler
from .photo_date_fixer import PhotoDateFixer
from .photo_metadata_homogenizer import PhotoMetadataHomogenizer 