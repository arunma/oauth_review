import base64
import hashlib
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
    code_challenge = request.args.get("code_challenge")

    # TODO - For now, ignore handling empty client id, redirect url and Verifying client info
    return render_template(
        "auth_server_login.html",
        client_id=client_id,
        redirect_url=redirect_url,
        code_challenge=code_challenge,
    )


@app.route("/login", methods=["POST"])
def login():
    # Verify user credentials
    username = request.form.get("username")
    password = request.form.get("password")
    client_id = request.form.get("client_id")
    redirect_url = request.form.get("redirect_url")
    code_challenge = request.form.get("code_challenge")

    # Assume that the client is authenticated using the username and password

    # TODO - Generate authorization code
    auth_code = generate_authorization_code(client_id, redirect_url, code_challenge)
    url = redirect_url + "?authorization_code=" + auth_code
    return redirect(url, code=303)


def generate_authorization_code(client_id, redirect_url, code_challenge):
    # Stupid way of generating auth code
    enc_auth_code = fernet.encrypt(f"{client_id}_123456789".encode())
    auth_code = base64.b64encode(enc_auth_code, b"-_").decode().replace("=", "")

    # TODO - Store the auth code for exchange of token later
    auth_codes[auth_code] = {
        "client_id": client_id,
        "redirect_url": redirect_url,
        "code_challenge": code_challenge,
    }
    return auth_code


@app.route("/token", methods=["POST"])
def exchange_for_token():
    auth_code = request.form.get("authorization_code")
    client_id = request.form.get("client_id")
    code_verifier = request.form.get("code_verifier")

    print("Code verifier value on /token", code_verifier)
    print("incoming auth code", auth_code)
    print("Auth codes: ", auth_codes)

    # Verify code challenge against code verifier
    h = hashlib.sha256()
    h.update(code_verifier.encode())
    code_challenge = (
        base64.b64encode(h.digest()).decode("utf-8").replace("=", "").replace("+", "")
    )

    print(
        f"Verifying code_challenge. In server: {auth_codes[auth_code]['code_challenge']}, Incoming: {code_challenge} "
    )

    if auth_codes[auth_code]["code_challenge"] != code_challenge:
        return "Invalid code verifier", 400
    else:
        del auth_codes[auth_code]

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
