from src.users.accessor import userAccessor
from src.core.auth import remove_authenticated_user, authenticate
from src.users.errors import InvalidPasswordError, UserNotFoundError
from src.users.users import User


class UserManager:
    async def create_user(self, args):
        try:
            print(args)
            user_in = User(username=args.username, password=args.password)
            user = await userAccessor.create(user_in)
            print(f"User created successfully: {user}")
        except Exception as e:
            print("Error creating user:", e)

    def logout(self, args):
        remove_authenticated_user()
        print("User logged out")

    async def login(self, args):
        try:
            user = await authenticate(args.username, args.password)
            print(f"User logged in: {user}")
        except UserNotFoundError:
            print("User not found")
        except InvalidPasswordError:
            print("Invalid password")
        except Exception as e:
            print("Login failed:", e)


userManager = UserManager()
