from datetime import datetime, timedelta

def DurationAsString(duration):
    # a utility function to convert a duration in microseconds into a string of hours and minutes
    microsecondsInAMinute = 1000 * 60
    microsecondsInAnHour = microsecondsInAMinute * 60
    hours = int(math.floor(duration / microsecondsInAnHour))
    minutes = int(math.floor((duration - (hours * microsecondsInAnHour)) / microsecondsInAMinute))
    if hours == 0 and minutes == 1:
        return str(minutes) + " minute"
    elif hours == 0 and minutes > 0:
        return str(minutes) + " minutes"
    elif hours == 1 and minutes == 0:
        return str(hours) + " hour"
    elif hours == 1 and minutes > 0:
        return str(hours) + " hour " + str(minutes) + " minutes"
    elif hours > 1 and minutes == 0:
        return str(hours) + " hours"
    else:
        return str(hours) + " hours " + str(minutes) + " minutes"

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
