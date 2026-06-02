from sanic import Sanic
from sanic.response import json

from app.config import settings


def create_app(name: str | None = None) -> Sanic:
    app = Sanic(name or settings.app_name)

    @app.get("/health")
    async def health(request):
        return json({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, dev=settings.debug)
