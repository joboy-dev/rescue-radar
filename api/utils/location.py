import os, ipinfo
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Request

from api.utils.settings import settings


def get_client_ip(request: Request):
    '''Returns the IP address of current client'''
    
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]
    else:
        client_ip = request.client.host
        
    return client_ip


def get_ip_info(request: Request):
    '''Returns the location of the client'''

    api_key = settings.IPINFO_API_KEY
    
    # Get an ipinfo handler with the API key
    ipinfo_handler = ipinfo.getHandler(api_key)

    # Get the client ip address
    client_ip = get_client_ip(request)

    # Get the location details of the client
    details = ipinfo_handler.getDetails(client_ip)
    
    print(details.all)

    # return the details as a dictionary
    return details.all
    