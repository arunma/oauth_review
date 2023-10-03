import json

import requests
from flask import Flask, request, render_template, make_response, redirect, url_for

auth_codes = {}

app = Flask(__name__)

auth_server_url = "http://localhost:3001"
client_url = "http://localhost:3000"


@app.route("/login")
def login():
    return render_template(
        "client_login.html",
        auth_server_endpoint=f"{auth_server_url}/auth",
        client_id="recon_server",
        redirect_url=f"{client_url}/callback",
    )


@app.route("/callback")
def callback():
    auth_code = request.args.get("authorization_code")

    response = requests.post(
        f"{auth_server_url}/token",
        data={
            "grant_type": "authorization_code",
            "authorization_code": auth_code,
            "client_id": "recon_server",
            "client_secret": "recon_super_secret",
            "redirect_url": "http://localhost:3000/callback",
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


if __name__ == "__main__":
    app.run(port=3000, debug=True)
