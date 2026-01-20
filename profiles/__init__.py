"""Profile management for multi-environment installation."""

from .base import Profile
from .defaults import LAB, WORK, PERSONAL, get_profile, list_profiles

__all__ = ['Profile', 'LAB', 'WORK', 'PERSONAL', 'get_profile', 'list_profiles']
