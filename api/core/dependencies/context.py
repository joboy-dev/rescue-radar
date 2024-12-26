import datetime as dt
from functools import wraps
from typing import Callable
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from geoalchemy2.functions import ST_GeogFromWKB

from api.db.database import get_db
from api.utils.location import get_ip_info
from api.v1.models.location import EmergencyLocation


def inject_context(request: Request):
    return {
        'request': request,
        "app_name": "Rescue Radar",
        "app_version": "1.0.0",
        "footer_message": "Emergency Response System",
        'year': dt.datetime.now().year
    }
  
  
def add_template_context(template_name: str):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Response:
            from main import frontend
                        
            # Get additional context from the injected dependency
            context_data = inject_context(request)
            
            # Get location information
            location_info = get_ip_info(request)
            
            # Run the route function to get extra context data from the function itself
            result = await func(request, *args, **kwargs)
            
            # Check if the function returned a RedirectResponse (usually for POST redirection)
            if isinstance(result, RedirectResponse):
                return result
            
            # Merge function data with context_data
            context = {
                'page': template_name.split('/')[-1].replace('.html', ''),
                'location': {**location_info},
                **context_data, 
                **result
            }
            
            return frontend.TemplateResponse(template_name, context)
        return wrapper
    return decorator  
