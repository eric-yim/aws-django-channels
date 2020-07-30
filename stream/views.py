from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
#import asyncio
import json
def index(request):
    return render(request, 'stream/index.html')
def room(request, room_name):
    return render(request, 'stream/display.html', {
        'room_name': room_name
    })

