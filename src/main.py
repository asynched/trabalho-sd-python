from flask import Flask, render_template, request, make_response
from dotenv import load_dotenv
from os import getenv
from github import GithubAuthService
from database import Database, UserRepository, SessionRepository

load_dotenv()

app = Flask(__name__)
app.template_folder = "../static"

database = Database()
user_repository = UserRepository(database)
session_repository = SessionRepository(database)
github_service = GithubAuthService()


@app.get("/")
def index():
    ctx = {
        "client_id": getenv("GITHUB_OAUTH_CLIENT_ID"),
    }

    return render_template("index.jinja", **ctx)


@app.get("/auth/github")
def github_auth_callback():
    args = request.args

    if "code" not in args:
        return "Missing code parameter", 400

    code = args["code"]

    profile = github_service.get_profile(code)

    if profile is None:
        return "Failed to get profile", 500

    user = user_repository.find_user_by_username(profile.login)

    if user is None:
        user_repository.create_user(profile)
        user = user_repository.find_user_by_username(profile.login)

    session = session_repository.create_session(user.id, code)

    if session is None:
        return "Failed to create session", 500

    response = make_response(render_template("auth.jinja"))
    response.set_cookie("session", session)

    return response


@app.get("/home")
def home():
    session = request.cookies.get("session")

    if session is None:
        return "Missing session cookie", 400

    if not session_repository.find_session_by_token(session):
        return "Invalid session", 400

    user = user_repository.find_user_by_session(session)

    if user is None:
        return "Invalid session", 400

    ctx = {"user": user}

    if user.role == "teacher":
        ctx["students"] = user_repository.get_users()

    return render_template("home.jinja", **ctx)


@app.post("/home")
def update_grade():
    form = request.form

    session = request.cookies.get("session")

    if session is None:
        return "Missing session cookie", 400

    if not session_repository.find_session_by_token(session):
        return "Invalid session", 400

    user = user_repository.find_user_by_session(session)

    if user is None:
        return "Invalid session", 400

    grade = int(form["grade"])

    if grade < 0 or grade > 4:
        return "Invalid grade", 400

    user_repository.update_grade(user.id, grade)

    ctx = {
        "user": user_repository.find_user_by_session(session),
    }

    return render_template("home.jinja", **ctx)


@app.get("/sign-out")
def sign_out():
    session = request.cookies.get("session")

    if session is None:
        return "Missing session cookie", 400

    session_repository.delete_session(session)

    response = make_response(render_template("sign-out.jinja"))
    response.set_cookie("session", "", expires=0)

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
