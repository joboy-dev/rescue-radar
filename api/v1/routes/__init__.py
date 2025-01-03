from fastapi import APIRouter

from api.v1.routes.external import external_router
from api.v1.routes.auth import auth_router
from api.v1.routes.user import user_router
from api.v1.routes.emergency import emergency_router
from api.v1.routes.location import location_router
from api.v1.routes.agency import agency_router
from api.v1.routes.responder import responder_router
from api.v1.routes.notification import notification_router
from api.v1.routes.report import report_router


v1_router = APIRouter()

v1_router.include_router(external_router)
v1_router.include_router(auth_router)
v1_router.include_router(user_router)
v1_router.include_router(emergency_router)
v1_router.include_router(location_router)
v1_router.include_router(agency_router)
v1_router.include_router(responder_router)
v1_router.include_router(notification_router)
v1_router.include_router(report_router)
