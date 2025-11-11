import json
from pathlib import Path
from src.users.accessor import userAccessor
from src.users.errors import UserNotFoundError, InvalidPasswordError
from src.users.users import User

# Файл для хранения сессии
AUTH_FILE = Path.home() / ".cli_file_manager_auth.json"


async def authenticate(username: str, password: str) -> int:
    user = await userAccessor.fetch_by_username(username)
    if not user:
        raise UserNotFoundError

    if not User.check_password(password, user.password):
        raise InvalidPasswordError

    AUTH_FILE.write_text(json.dumps({"user_id": user.id}))
    return user.id


def is_authenticated() -> int | None:
    if AUTH_FILE.exists():
        try:
            data = json.loads(AUTH_FILE.read_text())
            return data.get("user_id")
        except Exception:
            return None
    return None


def remove_authenticated_user():
    if AUTH_FILE.exists():
        AUTH_FILE.unlink()
