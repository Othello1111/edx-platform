"""
Views that implement a RESTful API for interacting with XBlocks.

Note that these views are only for interacting with existing blocks. Other
Studio APIs cover use cases like adding/deleting/editing blocks.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.response import Response
from xblock.django.request import DjangoWebobRequest, webob_to_django_response

from opaque_keys.edx.keys import UsageKey
from openedx.core.lib.api.view_utils import view_auth_classes
from ..api import (
    get_block_metadata,
    get_handler_url as _get_handler_url,
    load_block,
    render_block_view as _render_block_view,
)
from ..utils import validate_secure_token_for_xblock_handler

User = get_user_model()


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))  # Permissions are handled at a lower level, by the learning context
def block_metadata(request, usage_key_str):
    """
    Get metadata about the specified block.
    """
    usage_key = UsageKey.from_string(usage_key_str)
    block = load_block(usage_key, request.user)
    metadata_dict = get_block_metadata(block)
    return Response(metadata_dict)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))  # Permissions are handled at a lower level, by the learning context
def render_block_view(request, usage_key_str, view_name):
    """
    Get the HTML, JS, and CSS needed to render the given XBlock.
    """
    usage_key = UsageKey.from_string(usage_key_str)
    block = load_block(usage_key, request.user)
    fragment = _render_block_view(block, view_name, request.user)
    response_data = get_block_metadata(block)
    response_data.update(fragment.to_dict())
    return Response(response_data)


@api_view(['GET'])
@view_auth_classes(is_authenticated=True)
def get_handler_url(request, usage_key_str, handler_name):
    """
    Get an absolute URL which can be used (without any authentication) to call
    the given XBlock handler.

    The URL will expire but is guaranteed to be valid for a minimum of 2 days.
    """
    usage_key = UsageKey.from_string(usage_key_str)
    handler_url = _get_handler_url(usage_key, handler_name, request.user.id)
    return Response({"handler_url": handler_url})


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([])  # Disable session authentication; we don't need it and don't want CSRF checks
@permission_classes((permissions.AllowAny, ))
def xblock_handler(request, user_id, secure_token, usage_key_str, handler_name, suffix):
    """
    Run an XBlock's handler and return the result
    """
    user_id = int(user_id)  # User ID comes from the URL, not session auth
    usage_key = UsageKey.from_string(usage_key_str)

    # To support sandboxed XBlocks, custom frontends, and other use cases, we
    # authenticate requests using a secure token in the URL. see
    # openedx.core.djangoapps.xblock.utils.get_secure_hash_for_xblock_handler
    # for details and rationale.
    if not validate_secure_token_for_xblock_handler(user_id, usage_key_str, secure_token):
        raise PermissionDenied("Invalid/expired auth token.")
    if request.user.is_authenticated:
        # The user authenticated twice, e.g. with session auth and the token
        # So just make sure the session auth matches the token
        if request.user.id != user_id:
            raise AuthenticationFailed("Authentication conflict.")
        user = request.user
    else:
        user = User.objects.get(pk=user_id)

    request_webob = DjangoWebobRequest(request)  # Convert from django request to the webob format that XBlocks expect
    block = load_block(usage_key, user)
    # Run the handler, and save any resulting XBlock field value changes:
    response_webob = block.handle(handler_name, request_webob, suffix)
    response = webob_to_django_response(response_webob)
    # We need to set Access-Control-Allow-Origin: * to allow sandboxed XBlocks
    # to call these handlers:
    response['Access-Control-Allow-Origin'] = '*'
    return response
