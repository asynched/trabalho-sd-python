import requests
from os import getenv
from dataclasses import dataclass


@dataclass
class GithubProfile:
    id: int
    login: str
    name: str
    avatar_url: str


class GithubAuthService:
    client_id = getenv("GITHUB_OAUTH_CLIENT_ID")
    client_secret = getenv("GITHUB_OAUTH_CLIENT_SECRET")

    def get_access_token(self, code: str):
        try:
            response = requests.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
                headers={
                    "Accept": "application/json",
                },
            )

            data = response.json()

            return data["access_token"]
        except Exception as err:
            print("Failed to get access token, error:", err)
            return None

    def get_profile(self, code: str):
        access_token = self.get_access_token(code)

        if access_token is None:
            return None

        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                },
            )

            data = response.json()

            return GithubProfile(
                id=data["id"],
                login=data["login"],
                name=data["name"],
                avatar_url=data["avatar_url"],
            )
        except Exception as err:
            print("Failed to get profile, error:", err)
            return None
