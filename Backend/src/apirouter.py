from flask import Blueprint, jsonify
from flask_socketio import emit, join_room, leave_room
from flask import request
from flask import Response
from . import socketio
from .arduinoController import ArduinoController
import time
import logging
import os
import json
import io
from .camera_pi import Camera
from threading import Condition

apirouter = Blueprint("router", __name__)
arduinoController = ArduinoController()
portList = []

# I don't know where to put the creation of the port list
configFile = open(os.path.join("static", "config.json"), "r")
json_data = json.load(configFile)
print(json_data)
portList = json_data['portlist']


@apirouter.route('/startArduino',methods=['POST'])
def startArduino():
  message = 'Nothing happened'
  try:
    params = request.get_json(force=True)
    arduinoController.openSerial(params['selectedPort'])
    message = 'Serial reading started'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred starting the arduino'
  return jsonify({"message": message})

@apirouter.route('/stopArduino',methods=['GET'])
def stopArduino():
  message = 'Nothing happened'
  try:
    arduinoController.stopSerial()
    message = 'Stop message sent'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred stopping the arduino'
  return jsonify({"message": message})

@apirouter.route('/sendCommandToArduino', methods=['POST'])
def sendCommandToArduino():
  message = 'Nothing happened'
  try:
    params = request.get_json(force=True)
    arduinoController.sendCommand(params['command'])
    message = 'Command sent'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred sending command to the arduino'
  return jsonify({"message": message})

@apirouter.route('/releaseCommandToArduino', methods=['POST'])
def releaseCommandToArduino():
  message = 'Nothing happened'
  try:
    params = request.get_json(force=True)
    releaseCommand = '-' + params['command']
    arduinoController.sendCommand(releaseCommand)
    message = 'Command sent'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred sending command to the arduino'
  return jsonify({"message": message})


@apirouter.route('/getPageUpdate',methods=['GET'])
def getPageUpdate():
  answer = {
    "selectedPort": arduinoController.port, 
    "portlist": portList, 
  }
  return jsonify(answer)


def gen(camera): 
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@apirouter.route('/video_feed') 
def video_feed(): 
    """Video streaming route. Put this in the src attribute of an img tag.""" 
    return Response(gen(Camera()),mimetype='multipart/x-mixed-replace; boundary=frame')
