### Implementing OAuth flow with PKCE (Proof Key for Code Exchange)

#### Creating key pairs - RSA

```commandline
 openssl genrsa -out private.pem 2048
 openssl rsa -in private.pem -pubout -outform PEM -out public.pem
```

#### Instructions

1. Run `auth_server.py`
2. Run `auth_client_application.py`
3. Point the browser to `http://localhost:3000/login`

#### Reference link

https://blog.postman.com/pkce-oauth-how-to/