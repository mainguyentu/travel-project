from app.app_factory import create_app
from app.routers import analytics

app = create_app([analytics.router])
