from sanic import Sanic
from sanic.response import json

from app.config import APP_NAME


def create_app() -> Sanic:
    app = Sanic(APP_NAME)

    @app.get("/health")
    async def health(request):
        return json({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8000, dev=True)
