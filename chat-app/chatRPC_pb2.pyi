from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BlockRequest(_message.Message):
    __slots__ = ["access_token", "blocked_user"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    BLOCKED_USER_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    blocked_user: str
    def __init__(self, blocked_user: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...

class ChannelPostRequest(_message.Message):
    __slots__ = ["access_token", "channel_name", "message"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    channel_name: str
    message: str
    def __init__(self, channel_name: _Optional[str] = ..., message: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...

class DirectMessageRequest(_message.Message):
    __slots__ = ["access_token", "message", "recipient"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    message: str
    recipient: str
    def __init__(self, recipient: _Optional[str] = ..., message: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ["password", "username"]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    password: str
    username: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ["access_token"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = ["channel_name", "date", "receiver_id", "sender", "text"]
    CHANNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    channel_name: str
    date: str
    receiver_id: int
    sender: str
    text: str
    def __init__(self, sender: _Optional[str] = ..., text: _Optional[str] = ..., date: _Optional[str] = ..., receiver_id: _Optional[int] = ..., channel_name: _Optional[str] = ...) -> None: ...

class MessageStreamRequest(_message.Message):
    __slots__ = ["access_token"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ["password", "username"]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    password: str
    username: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["status", "text"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    status: bool
    text: str
    def __init__(self, text: _Optional[str] = ..., status: bool = ...) -> None: ...

class UnblockRequest(_message.Message):
    __slots__ = ["access_token", "blocked_user"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    BLOCKED_USER_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    blocked_user: str
    def __init__(self, blocked_user: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...

class UnwatchRequest(_message.Message):
    __slots__ = ["access_token", "channel_name"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    channel_name: str
    def __init__(self, channel_name: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...

class WatchRequest(_message.Message):
    __slots__ = ["access_token", "channel_name"]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    channel_name: str
    def __init__(self, channel_name: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...
