from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref, relationship
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Date, ForeignKey, TIMESTAMP, Float, JSON
import datetime
import json

user = 'postgres'
password = '1234'
host = 'localhost'
port = '5432'
database = 'rain_cloud_db'

CONNECTION_STR = f"postgresql://{user}:{password}@{host}/{database}"

engine = create_engine(CONNECTION_STR)

Base = declarative_base()
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def current_time_without_ms():
    return datetime.datetime.now().replace(microsecond=0)

class Devices(Base):
    """
    Class representing the 'devices' table in the database.
    
    Attributes:
    - id (BigInteger, primary_key): Unique identifier for the device.
    - location (JSON): JSON data representing the device location.
    - orientation (JSON): JSON data representing the device orientation.
    - is_online (Boolean): Flag indicating whether the device is online or not.
    - logs_children (relationship): Relationship to the Logs table.
    - weather_logs_children (relationship): Relationship to the WeatherLogs table.
    - cloud_images (relationship): Relationship to the CloudImages table.
    """
    __tablename__ = 'devices'

    id = Column(BigInteger, primary_key=True)
    location = Column(JSON)
    orientation = Column(JSON)
    
    is_online = Column(Boolean)
    
    logs_children = relationship("Logs", back_populates="parent")
    weather_logs_children = relationship("WeatherLogs", back_populates="parent")
    cloud_images_children = relationship("CloudImages", back_populates="parent")
    
    def as_json(self):
        return {
            "id":self.id,
            "location":self.location,
            "orientation":self.orientation,
            "is_online":self.is_online
        }
    
    
class Logs(Base):
    """
    Class representing the 'logs' table in the database.
    
    Attributes:
    - id (BigInteger, primary_key): Unique identifier for the log entry.
    - device_id (BigInteger, ForeignKey): Foreign key referencing the device ID.
    - timestamp (TIMESTAMP): Timestamp of the log entry creation.
    - type (String): Type of log entry.
    - message (String): Message associated with the log entry.
    - parent (relationship): Relationship to the Devices table.
    """
    __tablename__ = 'logs'
    
    id = Column(BigInteger, primary_key=True)
    device_id = Column(BigInteger, ForeignKey('devices.id'))
    timestamp = Column(TIMESTAMP, default=current_time_without_ms)
    
    type = Column(String)
    message = Column(String)
    
    parent = relationship("Devices", back_populates="logs_children")
    

class WeatherLogs(Base):
    """
    Class representing the 'weather_logs' table in the database.
    
    Attributes:
    - id (BigInteger, primary_key): Unique identifier for the weather log entry.
    - device_id (BigInteger, ForeignKey): Foreign key referencing the device ID.
    - timestamp (TIMESTAMP): Timestamp of the weather log entry creation.
    - rainfall_amount (Float): Amount of rainfall recorded.
    - air_temperature (Float): Air temperature recorded.
    - humidity (Float): Humidity recorded.
    - pressure (Float): Atmospheric pressure recorded.
    - parent (relationship): Relationship to the Devices table.
    """
    __tablename__ = 'weather_logs'
    
    id = Column(BigInteger, primary_key=True)
    device_id = Column(BigInteger, ForeignKey('devices.id'))
    timestamp = Column(TIMESTAMP, default=current_time_without_ms)
    
    rainfall_amount = Column(Float)
    air_temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    
    parent = relationship("Devices", back_populates="weather_logs_children")
    
    def as_json(self):
        return {
            "id":self.id,
            "device_id":self.device_id,
            "timestamp":str(self.timestamp),
            "rainfall_amount":self.rainfall_amount,
            "air_temperature":self.air_temperature,
            "humidity":self.humidity,
            "pressure":self.pressure
        }
    
    
class CloudImages(Base):
    __tablename__ = 'cloud_images'
    
    id = Column(BigInteger, primary_key=True)
    device_id = Column(BigInteger, ForeignKey('devices.id'))
    timestamp = Column(TIMESTAMP, default=current_time_without_ms)
    file_path = Column(String)
    
    parent = relationship("Devices", back_populates="cloud_images_children")
    
    
    
    
