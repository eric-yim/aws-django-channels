import json
from channels.generic.websocket import WebsocketConsumer
import asyncio
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
#from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import pandas.io.sql as sqlio
import pickle
import numpy as np
import base64
import psycopg2
import os      
import cv2  

from psycopg2_pgevents.trigger import install_trigger, \
    install_trigger_function, uninstall_trigger, uninstall_trigger_function
from psycopg2_pgevents.event import poll, register_event_channel, \
    unregister_event_channel
class MyConsumer(WebsocketConsumer):
    def connect(self):
        # Called on connection.
        # To accept the connection call:
        self.accept()

        #DATABASE LOOKUP
        self.scaleup=2.0
        self.img = None
        self.data = None
        self.row_id = None
        self.conn = psycopg2.connect(host=os.environ['db_uri'],
                                dbname=os.environ['db_database'],
                                user=os.environ['db_username'],
                                password=os.environ['db_password'],
                                port = os.environ['db_port'])
        self.table_name = 'crowd_heatmaps'
        
        self.query_db()
        
        


    def receive(self, text_data=None, bytes_data=None):
        pass
    def disconnect(self, close_code):
        pass
    ##### Handlers for messages sent over the channel layer    

    def query_db(self):
        if self.conn is not None:
            self.conn.autocommit=True
            install_trigger_function(self.conn)
            install_trigger(self.conn, self.table_name)
            register_event_channel(self.conn)
            try:
                print("LIStening for event...")
                while True:
                    row_ids = []
                    for evt in poll(self.conn):
                        print('New Event: {}'.format(evt))
                        row_id = vars(evt)['row_id']
                        row_ids.append(row_id)

                    if len(row_ids)>0:
                        self.row_id=max(row_ids)
                        
                        self.query_db_basic()
                        self.transform_and_scale()
                        if self.img is not None:
                            self.send(text_data=self.img.decode('utf-8'))
            except KeyboardInterrupt:
                print('User exit via Ctrl-C; Shutting down...')
                unregister_event_channel(connection)
                uninstall_trigger(connection, table_name)
                uninstall_trigger_function(connection)
                print('Shutdown complete.')

                #await asyncio.sleep(2)
                #await self.query_db_basic()
                #await self.transform_and_scale()
                #if self.img is not None:
                #    await self.send(text_data=self.img.decode('utf-8'))
            #print(self.data)

    #@database_sync_to_async
    def query_db_basic(self):
        
        if self.row_id is not None:
            try:
                #cursor = self.conn.cursor()
                query = "select * from {} natural join video_sensors where id={};".format(self.table_name,self.row_id)
                data =  sqlio.read_sql_query(query, self.conn)
                self.data= data['heatmap'][0]
            except psycopg2.DatabaseError as error:
                print(error)
                self.data = None

    def transform_and_scale(self):
        q = self.data
        if q is not None:
            q = pickle.loads(q)
            q = np.array(q[...,0])
            q = np.clip(q*self.scaleup,0,255).astype(np.uint8)
            q=cv2.applyColorMap(q, cv2.COLORMAP_JET)
            self.img = base64.b64encode(cv2.imencode('.png',q)[1].tobytes())
            
        
    
