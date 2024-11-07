from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from api.v1.models.user import User
from api.v1.services.auth import AuthService
from api.core.dependencies.flash_messages import flash, MessageCategory


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # Define route access logic
        unauthenticated_only_routes = ["/", "/signup", "/login"]
        protected_routes = [
            "/dashboard", 
            "/profile", 
            "/settings", 
            '/logout',
            '/select-role',
            '/profile',
            '/profile/edit',
            '/profile/change-password',
        ]  # Define more as needed

        # Check access token in cookies
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        
        # If route is protected, ensure user is authenticated
        if request.url.path in protected_routes:
            if not access_token:
                flash(request, 'Please login to access this page.', MessageCategory.ERROR)
                return RedirectResponse(url="/login", status_code=303)

            # Verify token
            try:
                token = AuthService.verify_access_token(access_token, credentials_exception)
                user = User.fetch_by_id(token.user_id)
                
                if not user:
                    flash(request, 'Session expired. Please login again.', MessageCategory.ERROR)
                    return RedirectResponse(url="/login", status_code=303)
                
            except HTTPException as e:
                # Try to refresh access token with refresh token
                try:
                    access, refresh = AuthService.refresh_access_token(refresh_token)
    
                    # Update access token in cookies
                    response = RedirectResponse(url=request.url.path, status_code=303)
                    response.set_cookie("access_token", access)
                    response.set_cookie("refresh_token", refresh)
                    
                    return response
                
                except HTTPException as e:
                    # If refresh token is expired, redirect to login page
                    flash(request, e.detail, MessageCategory.ERROR)
                    return RedirectResponse(url="/login", status_code=303)
            
            # Attach user to request state for access in route
            request.state.current_user = user

        # If route is for unauthenticated users only, redirect authenticated users
        elif request.url.path in unauthenticated_only_routes:
            try:
                if access_token and AuthService.verify_access_token(access_token, credentials_exception):
                    return RedirectResponse(url="/dashboard", status_code=303)
            except HTTPException as e:
                flash(request, e.detail, MessageCategory.ERROR)
                return RedirectResponse(url="/login", status_code=303)
            
        # Proceed with request if no redirection is needed
        response = await call_next(request)
        return response
