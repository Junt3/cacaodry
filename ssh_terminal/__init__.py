"""
SSH Terminal Module for Cacao Drying System

This module provides SSH terminal functionality through WebSocket connections.
It allows authenticated users to access the server hosting this service via SSH.
"""

from .socketio_events import create_ssh_namespace
from .simple_events import create_simple_ssh_namespace

__all__ = ['create_ssh_namespace', 'create_simple_ssh_namespace']