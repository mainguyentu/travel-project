from app.app_factory import create_app
from app.routers import interaction

app = create_app([interaction.router])
