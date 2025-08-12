from __future__ import annotations

from typing import Optional, Any


class PlausibleError(Exception):
    pass


class PlausibleAuthError(PlausibleError):
    def __init__(self, message: str, *, status_code: Optional[int] = None, response_text: Optional[str] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class PlausibleRateLimitError(PlausibleError):
    def __init__(self, message: str, *, status_code: Optional[int] = None, response_text: Optional[str] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class PlausibleAPIError(PlausibleError):
    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
        payload: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text
        self.payload = payload
