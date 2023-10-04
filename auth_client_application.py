import base64
import hashlib
import json

import requests
from flask import Flask, request, render_template, make_response, redirect, url_for

auth_codes = {}

app = Flask(__name__)

AUTH_SERVER_URL = "http://localhost:3001"
CLIENT_URL = "http://localhost:3000"
CODE_VERIFIER = "strange_times"


@app.route("/login")
def login():
    code_challenge = generate_code_challenge(CODE_VERIFIER)
    print("Codddeeee", code_challenge)
    return render_template(
        "client_login.html",
        auth_server_endpoint=f"{AUTH_SERVER_URL}/auth",
        client_id="recon_server",
        redirect_url=f"{CLIENT_URL}/callback",
        code_challenge=code_challenge,
    )


@app.route("/callback")
def callback():
    auth_code = request.args.get("authorization_code")

    response = requests.post(
        f"{AUTH_SERVER_URL}/token",
        data={
            "grant_type": "authorization_code",
            "authorization_code": auth_code,
            "client_id": "recon_server",
            "client_secret": "recon_super_secret",
            "redirect_url": "http://localhost:3000/callback",
            "code_verifier": CODE_VERIFIER,
        },
    )

    print("Response: ", response.text)
    access_token = json.loads(response.text).get("access_token")

    print("Access token: ", access_token)
    response = make_response(redirect(url_for("success")))
    response.set_cookie("access_token", auth_code)
    return response


@app.route("/success")
def success():
    return "Success"


def generate_code_challenge(code_verifier):
    h = hashlib.sha256()
    h.update(code_verifier.encode())
    code_challenge = (
        base64.b64encode(h.digest()).decode("utf-8").replace("=", "").replace("+", "")
    )
    print("Code challenge ", code_challenge)
    return code_challenge


if __name__ == "__main__":
    app.run(port=3000, debug=True)
