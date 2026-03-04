"""
Identity routes for Flask API.

Provides endpoints for Identity domain:
- GET /api/identity - Get all identity documents
- GET /api/identity/<id> - Get a specific identity document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.identity_service import IdentityService

import logging
logger = logging.getLogger(__name__)


def create_identity_routes():
    """
    Create a Flask Blueprint exposing identity endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with identity routes
    """
    identity_routes = Blueprint('identity_routes', __name__)
    
    @identity_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_identitys():
        """
        GET /api/identity - Retrieve infinite scroll batch of sorted, filtered identity documents.
        
        Query Parameters:
            name: Optional name filter
            after_id: Cursor for infinite scroll (ID of last item from previous batch, omit for first request)
            limit: Items per batch (default: 10, max: 100)
            sort_by: Field to sort by (default: 'name')
            order: Sort order 'asc' or 'desc' (default: 'asc')
        
        Returns:
            JSON response with infinite scroll results: {
                'items': [...],
                'limit': int,
                'has_more': bool,
                'next_cursor': str|None
            }
        
        Raises:
            400 Bad Request: If invalid parameters provided
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Get query parameters
        name = request.args.get('name')
        after_id = request.args.get('after_id')
        limit = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'name')
        order = request.args.get('order', 'asc')
        
        # Service layer validates parameters and raises HTTPBadRequest if invalid
        # @handle_route_exceptions decorator will catch and format the exception
        result = IdentityService.get_identitys(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_identitys Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @identity_routes.route('/<identity_id>', methods=['GET'])
    @handle_route_exceptions
    def get_identity(identity_id):
        """
        GET /api/identity/<id> - Retrieve a specific identity document by ID.
        
        Args:
            identity_id: The identity ID to retrieve
            
        Returns:
            JSON response with the identity document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        identity = IdentityService.get_identity(identity_id, token, breadcrumb)
        logger.info(f"get_identity Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(identity), 200
    
    logger.info("Identity Flask Routes Registered")
    return identity_routes