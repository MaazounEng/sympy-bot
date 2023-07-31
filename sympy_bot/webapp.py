import textwrap
import datetime
import os
import base64
from subprocess import CalledProcessError
from collections import defaultdict

from aiohttp import web, ClientSession

from gidgethub import routing, sansio, BadRequest
from gidgethub.aiohttp import GitHubAPI

from .changelog import (get_changelog, update_release_notes, VERSION_RE,
                        get_release_notes_filename, BEGIN_RELEASE_NOTES,
                        END_RELEASE_NOTES)
from .update_wiki import update_wiki

router = routing.Router()

USER = 'sympy-bot'
RELEASE_FILE = 'sympy/release.py'

async def main_post(request):
    # read the GitHub webhook payload
    body = await request.read()

    # our authentication token and secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # a representation of GitHub webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    print(f"Received {event.event} event with delivery_id={event.delivery_id}")
    async with ClientSession() as session:
        gh = GitHubAPI(session, USER, oauth_token=oauth_token, cache={})

        # call the appropriate callback for the event
        result = await router.dispatch(event, gh)

    return web.Response(status=200, text=str(result))
