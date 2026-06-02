from sanic import Sanic
from sanic.response import json

from app.config import APP_NAME


def create_app(name: str = APP_NAME) -> Sanic:
    app = Sanic(name)

    @app.get("/health")
    async def health(request):
        return json({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, dev=True)
