# Security

As a security I decided to use `djangorestframework-simplejwt` library that provides an easy tool to use JWT tokens.

Here is how we can install it to our project:

```bash
poetry add djangorestframework-simplejwt
```

Then we need to add it to our `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "rest_framework_simplejwt",
    ...
]
```

And add config to REST_FRAMEWORK:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

Also configure JWT settings:
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env.str("SECRET_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}
```

And finally to use it we can configure our urls:

```python
urlpatterns = [
    path("token/", SpectacularTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", SpectacularTokenRefreshView.as_view(), name="token_refresh"),
    path("user/", GetUserInformationView.as_view(), name="user_information"),
    path("register/", RegisterUserView.as_view(), name="register"),
]
```

As a login I use `token/` endpoint, to refresh token `token/refresh/` and to get user information `user/` endpoint.
And to register new user I use `register/` endpoint.

And that's it for usage:)

Also I decided to use `django-environ` to store my secret keys in `.env` file.

Here is how we can install it:

```bash
poetry add django-environ
```

And then we can use it in our `settings.py`:

```python
import environ

env = environ.Env()
environ.Env.read_env(str(BASE_DIR / ".env"))

# And obtain secret from env
SECRET_KEY = env.str("SECRET_KEY")
```

As for other security measures I decided to use `django-cors-headers` to allow only specific origins to access our API.

Here is how we can install it:

```bash
poetry add django-cors-headers
```

And then we need to add it to our `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "corsheaders",
    ...
]
```

And then we need to add it to our `MIDDLEWARE` in `settings.py`:

```python
MIDDLEWARE = [
    ...
    "corsheaders.middleware.CorsMiddleware",
    ...
]
```

And then we need to configure it in `settings.py`:

```python
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:80"])
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)
```

And that's it for security measures:)
