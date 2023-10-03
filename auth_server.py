import base64
import json
import time

import jwt
from cryptography.fernet import Fernet
from flask import render_template, redirect, Flask, request

auth_codes = {}

app = Flask(__name__)

fernet = Fernet(Fernet.generate_key())

with open("private.pem", "rb") as f:
    private_key = f.read()


# Request from client - Render the login page
@app.route("/auth")
def auth():
    client_id = request.args.get("client_id")
    redirect_url = request.args.get("redirect_url")

    # TODO - For now, ignore handling empty client id, redirect url and Verifying client info
    return render_template(
        "auth_server_login.html",
        client_id=client_id,
        redirect_url=redirect_url,
    )


@app.route("/login", methods=["POST"])
def login():
    # Verify user credentials
    username = request.form.get("username")
    password = request.form.get("password")
    client_id = request.form.get("client_id")
    redirect_url = request.form.get("redirect_url")

    # Assume that the client is authentcated

    # TODO - Generate authorization code
    auth_code = generate_authorization_code(client_id, redirect_url)
    url = redirect_url + "?authorization_code=" + auth_code
    return redirect(url, code=303)


def generate_authorization_code(client_id, redirect_url):
    # Stupid way of generating auth code
    enc_auth_code = fernet.encrypt(f"{client_id}_123456789".encode())
    auth_code = base64.b64encode(enc_auth_code, b"-_").decode().replace("=", "")

    # TODO - Store the auth code for exchange of token later
    auth_codes[auth_code] = {
        "client_id": client_id,
        "redirect_url": redirect_url,
    }
    return auth_code


@app.route("/token", methods=["POST"])
def exchange_for_token():
    auth_code = request.form.get("authorization_code")
    client_id = request.form.get("client_id")
    # code_verifier = request.form.get("code_verifier")

    # TODO - Verify code challenge against code verifier
    # sha256 = hashlib.sha256()
    # sha256.update(code_verifier.encode("utf-8"))
    # code_challenge = base64.b64encode(sha256.digest()).decode("utf-8").replace("=", "")

    # if auth_codes[auth_code]["code_challenge"] != code_challenge:
    #     return "Invalid code verifier", 400
    # else:
    #     del auth_codes[auth_code]

    access_token = generate_access_token()
    return json.dumps(
        {
            "access_token": access_token,
            "token_type": "JWT",
            "expires_in": 3600,
        }
    )


def generate_access_token():
    payload = {
        "iss": "http://my-auth-server.com",
        "exp": time.time() + 3600,
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


if __name__ == "__main__":
    app.run(port=3001, debug=True)
