from sanic import Sanic
from sanic.response import json

from app.config import settings
from app.routes.admins import admins_bp
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.webhooks import webhooks_bp


def create_app(name: str | None = None) -> Sanic:
    app = Sanic(name or settings.app_name)
    app.blueprint(auth_bp)
    app.blueprint(users_bp)
    app.blueprint(admins_bp)
    app.blueprint(webhooks_bp)

    @app.get("/health")
    async def health(request):
        return json({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, dev=settings.debug)
