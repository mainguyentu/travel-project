from app.app_factory import create_app
from app.routers import admin

app = create_app([admin.router])
