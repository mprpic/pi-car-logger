import os
import gps
import signal
from pprint import pprint
from peewee import Model, SqliteDatabase, FloatField, DateTimeField
from playhouse.shortcuts import model_to_dict

# If we want to print received data rather than store them in the database,
# define a GPS_DEBUG_MODE environment variable.
DEBUG_MODE = 'GPS_DEBUG_MODE' in os.environ

# Initialize database where we store GPS data.
DB_NAME = 'gps_data.sqlite'
db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
db = SqliteDatabase(db_path)


class GPSRecord(Model):
    """GPS record model to store data received from GPS module"""

    latitude = FloatField(null=True)     # Latitude in degrees: +/- signifies North/South
    longitude = FloatField(null=True)    # Longitude in degrees: +/- signifies East/West
    altitude = FloatField(null=True)     # In meters
    climb_speed = FloatField(null=True)  # Climb (positive) or sink (negative) rate in m/s
    speed = FloatField(null=True)        # Speed over ground in m/s
    timestamp = DateTimeField(null=True)      # In UTC

    class Meta:
        database = db


def init_db():
    db.connect()

    # Create tables if needed
    db.create_tables([GPSRecord], safe=True)


def init_gps():
    # Start a GPS streaming session that outputs data in JSON format
    # (represented as a dict in Python). The session itself is an iterator that
    # yields values as it gets them from the GPS module.
    session = gps.gps()
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    return session


def quit_logger(*args):
    print('Exiting GPS logger...')
    db.close()
    exit(0)


def record_data(session):
    while True:
        try:
            report = session.next()

            # Only watch for TPV-type records (Time-Position-Velocity).
            if report['class'] != 'TPV':
                continue

            # Create a record with the passed data. If any of the attributes
            # are missing, KeyError will be caught and record skipped.
            record = GPSRecord(
                latitude=report['lat'],
                longitude=report['lon'],
                altitude=report['alt'],
                climb_speed=report['climb'],
                speed=report['speed'],
                timestamp=report['time'],
            )

            if DEBUG_MODE:
                # If in debug mode, pretty print the dictionary of all data
                # excluding the records non-existent (since it's not
                # saved) ID.
                pprint(model_to_dict(record, exclude=[GPSRecord.id]))
            else:
                # Save the record to the database.
                record.save()

        except KeyError:
            pass
        except (KeyboardInterrupt, StopIteration):
            quit_logger()


def main():
    init_db()
    session = init_gps()
    signal.signal(signal.SIGTERM, quit_logger)

    record_data(session)


if __name__ == '__main__':
    main()
