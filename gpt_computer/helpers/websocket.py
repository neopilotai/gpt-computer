from __future__ import annotations

import re
import threading

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, Optional
from urllib.parse import urlparse

import socketio

from gpt_computer.systems.communication.websocket import (
    WebSocketHandler,
    WebSocketResult,
    validate_ws_origin,
    normalize_origin,
    ConnectionNotFoundError,
    SingletonInstantiationError,
)

if TYPE_CHECKING:  # pragma: no cover - hints only
    from gpt_computer.helpers.websocket_manager import WebSocketManager
