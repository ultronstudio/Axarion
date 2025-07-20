"""
Axarion Engine Asset Manager

This module provides asset management functionality for the Axarion Engine editor,
including local asset import via drag-and-drop and Asset Store integration.
"""

__version__ = "1.0.0"
__author__ = "Axarion Engine Team"

from .asset_manager import AssetManagerWindow
from .asset_utils import AssetUtils

__all__ = ['AssetManagerWindow', 'AssetUtils']
