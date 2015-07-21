"""
This module is used to send the led data to hyperion's json server
Created on 27.11.2014, last updated on 02.02.2015
@author: Fabian Hertwig
@author: Juha Rantanen
"""

import socket

client = None

class JsonClient(object):

    def __init__(self, host, port, timeout=10):

        self.host = host
        self.port = port
        self.timeout = timeout
        self.connected = False
        self.socket = None

    def connect(self):

        """
        Open a socket connection to the server
        :param host: Hostname oder ip address of the server
        :param port: Port of the server
        :param timeout: timeout in seconds
        """

        if self.connected:
            return

        self.socket = socket.socket()
        self.socket.settimeout(self.timeout)
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
        except socket.error, exc:
            print "Error on connection to ", self.host, ":", self.port, "\nMessage: ", exc

    def disconnect(self):
        if self.connected:
            try:
                self.socket.send('{"command":"clearall"}\n')
                self.socket.close()
                self.connected = False
            except socket.error, exc:
                print "Could not close socket connection\nMessage: ", exc

    def send_led_data(self, led_data):
        """
        Send the led data in a message format the hyperion json server understands
        :param led_data: bytearray of the led data (r,g,b) * hyperion.ledcount
        """

        if not self.connected:
            return
        # create a message to send
        message = '{"color":['
        # add all the color values to the message
        for i in range(len(led_data)):
            message += repr(led_data[i])
            # separate the color values with ",", but do not add a "," at the end
            if not i == len(led_data) - 1:
                message += ','
        # complete message
        message += '],"command":"color","priority":100}\n'
        try:
            self.socket.send(message)
        except socket.error, exc:
            print "Error while sending the led data\nMessage: ", exc
            # Recreate the socket
            self.connected = False
            print "Reconnecting..."
            self.connect()
            if self.connected:
                print "Connected."


def open_connection(host, port, timeout=10):
    global client
    client = JsonClient(host, port, timeout)
    client.connect()


def close_connection():
    global client
    client.disconnect()


def send_led_data(led_data):
    global client
    if client != None:
        client.send_led_data(led_data)