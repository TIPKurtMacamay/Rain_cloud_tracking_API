import os
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import engine, Base, Session, CONNECTION_STR, Devices, WeatherLogs, CloudImages
from flask_cors import CORS
from datetime import timedelta, datetime
import argparse
import json

app = Flask(__name__)
CORS(app)  
app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION_STR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)

app.config['UPLOAD_FOLDER_A'] = 'cloud_images/device_A'
app.config['UPLOAD_FOLDER_B'] = 'cloud_images/device_B'

jwt = JWTManager(app)
session = Session()

def response_template(method, code, message=None, data=None):
    if code==200:
        if method=='GET':
            message = "Resource retrieved successfully"
        elif method=='PUT':
            message = "Resource updated successfully"
        elif method=='DELETE':
            message = "Resource deleted successfully"
            
        return jsonify({
            "success": True,
            "message": message,
            "data": data
        }), code
    
    if code==404:
        return jsonify({
            "success": False,
            "message": "Resource not found"
        }), code
        
    if code==201:
        return jsonify({
            "success": True,
            "message": "Resources created successfully",
            "data": data
        }), code
    
    if code==400:
        return jsonify({
            "success": False,
            "message": f"Invalid request data: {message}"
        }), code
        
    if code==500:
        return jsonify({
            "success": False,
            "message": f"Internal server error: {message}"
        }), code

@app.route('/update-device/<int:id>',  methods=['POST'])
def updateDevice(id):
    data = request.get_json()
    device = session.query(Devices).filter(Devices.id==id).first()
    if not device:
        return response_template(request.method, 404)
    
    device.location = data.get('location')
    device.orientation = data.get('orientation')
    
    try:
        session.commit()
        return response_template(request.method, 200, data=device.as_json())
    except Exception as e:
        session.rollback()
        return response_template(request.method, 400, message=e)
        

@app.route('/register-device', methods=['POST'])
def registerDevice():
    data = request.get_json()
    
    new_device = Devices(
        location = data.get('location'),
        orientation = data.get('orientation'),
        is_online = False
    )
    
    try:
        session.add(new_device)
        session.commit()
        return response_template(request.method, 201, data=new_device.as_json())
    except Exception as e:
        session.rollback()
        return response_template(request.method, 400, message=e)
    
        

@app.route('/log-info', methods=['POST'])
def logInfo():
    pass

@app.route('/log-weather-data', methods=['POST'])
def logWeatherData():
    data = request.get_json()
    
    new_weatherLogs = WeatherLogs(
        device_id = data.get("device_id"),
        rainfall_amount = data.get("rainfall_amount"),
        air_temperature = data.get("air_temperature"),
        humidity = data.get("humidity"),
        pressure = data.get("pressure")
    )
    
    try:
        session.add(new_weatherLogs)
        session.commit()
        return response_template(request.method, 201, data=new_weatherLogs.as_json())
    except Exception as e:
        session.rollback()
        return response_template(request.method, 400, message=e)


@app.route('/fetch-last-data/<int:id>', methods=['GET'])
def fetchData(id):
    try:
        latest_record = session.query(WeatherLogs).filter(WeatherLogs.device_id == id).order_by(WeatherLogs.timestamp.desc()).first()
        device_info =  session.query(Devices).filter(Devices.id == id).first()
        
        response_dict = json.dumps({**latest_record.as_json(), **device_info.as_json()})
        
        return response_template(request.method, 200, data=response_dict)
    except Exception as e:
        return response_template(request.method, 400, message=e)
    
    
@app.route('/fetch-logs', methods=['GET'])
def fetchLogs():
    pass


@app.route('/devices', methods=['GET'])
def fetchDevices():
    try:
        devices = session.query(Devices).all()
        return response_template(request.method, 200, data=[i.as_json() for i in devices])
    except Exception as e:
        return response_template(request.method, 400, message=e)
    
    
@app.route('/weather-logs/<int:count>', methods=['GET'])
def fetchWeatherData(count):
    try:
        data = request.get_json()
        
        duration = datetime.now() - timedelta(minutes=data.get("minutes"))
        data = session.query(WeatherLogs).filter(WeatherLogs.timestamp >= duration).order_by(WeatherLogs.timestamp.desc()).limit(count).all()
        return response_template(request.method, 200, data=[i.as_json() for i in data])
    except Exception as e:
        return response_template(request.method, 400, message=e)
    
    
@app.route('/weather-logs/duration', methods=['GET'])
def fetchWeatherDataDuration():
    try:
        data = request.get_json()
        
        duration = datetime.now() - timedelta(minutes=data.get("minutes"))
        data = session.query(WeatherLogs).filter(WeatherLogs.timestamp >= duration).all()
        return response_template(request.method, 200, data=[i.as_json() for i in data])
    except Exception as e:
        return response_template(request.method, 400, message=e)


@app.route('/sky_image', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return response_template(request.method, 400, message="Error: No file part")

    file = request.files['file']
    if file.filename == '':
         return response_template(request.method, 400, message="Error: No file part")

    device_id = request.form.get('device_id')
    

    if file and device_id:
        if device_id==1:
            filename = os.path.join(app.config['UPLOAD_FOLDER_A'], file.filename)
        elif device_id==2:
            filename = os.path.join(app.config['UPLOAD_FOLDER_B'], file.filename)
            
        file.save(filename)
        
        new_cloud_image = CloudImages(
            file_path=filename, 
            device_id=device_id
        )
        try: 
            session.add(new_cloud_image)
            session.commit()
            return response_template(request.method, 201)
        except Exception as e:
            session.rollback()
            return response_template(request.method, 201)
    else:
        return response_template(request.method, 400, message="error: Missing data field")
            
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-ct", "--create", action='store_true', help="Create Tables")
    parser.add_argument("-dt", "--drop", action='store_true', help="Drop Tables")
    parser.add_argument("-s", "--start", action='store_true', help="Start API Endpoints")
    
    args = parser.parse_args()
    if args.create:
        with app.app_context():
            print("Creating Tables")
            Base.metadata.create_all(bind=engine)
            print('Tables created.')
    
    if args.drop:
        with app.app_context():
            print("Dropping Tables")
            Base.metadata.drop_all(bind=engine)  # Specify the engine to bind to
            print('Tables dropped.')

    if args.start:
        app.run(debug=True)