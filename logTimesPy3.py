import os
import ctypes, ctypes.wintypes
import csv
import pickle
from datetime import datetime
from time import sleep

LOG_FILE = 'time_log'
SUFFIX = '.csv'


class LastInfo(ctypes.Structure):
    _fields_ = [
      ('cbSize', ctypes.wintypes.UINT),
      ('dwTime', ctypes.wintypes.DWORD),
      ]
    
GetLastInputInfo = ctypes.windll.user32.GetLastInputInfo
GetLastInputInfo.restype = ctypes.wintypes.BOOL
GetLastInputInfo.argtypes = [ctypes.POINTER(LastInfo)]
Sleep = ctypes.windll.kernel32.Sleep


def wait_until_active(tol=0.5):

    last_info = LastInfo()
    last_info.cbSize = ctypes.sizeof(last_info)
    last_time = None
    delay = 1  # ms
    max_delay = int(tol*1000)
    while True:
        GetLastInputInfo(ctypes.byref(last_info))
        if last_time is None:
            last_time = last_info.dwTime
        if last_time != last_info.dwTime:
            break
        delay = min(2*delay, max_delay)
    Sleep(delay)


def unpickle():
    try:
        morning = pickle.load(open("morning.p", "rb"))
    except IOError:
        morning = datetime.now()
        pickle.dump(morning, open("morning.p", "wb"))
    try:
        evening = pickle.load(open("evening.p", "rb"))
    except IOError:
        evening = morning
        pickle.dump(evening, open("evening.p", "wb"))

    return morning, evening


def log_to_csv(morning, evening):
    if morning != evening:
        delta = evening - morning
        morning_str = str(morning.hour)+":"+str(morning.minute)
        evening_str = str(evening.hour)+":"+str(evening.minute)
        if delta.days == 0:
            row = [str(morning.date()), morning_str, evening_str, str(delta.seconds/3600.0)]
        else:
            row = [str(morning.date()), morning_str, evening_str, '!' + str(delta.days)+'Days, ' + str(delta.seconds/3600.0)]
        log_file_name = LOG_FILE + morning.month + '.' + morning.year + SUFFIX
        is_first = not os.path.isfile(log_file_name)
        with open(log_file_name, 'a+', newline='') as log_file:
            time_logger = csv.writer(log_file)
            if is_first:
                time_logger.writerow(['Date', 'Beginning time', 'End time', 'Total hours this day'])
            time_logger.writerow(row)


def main():
    while True:
        morning, evening = unpickle()
        if morning.date() != datetime.now().date():
            log_to_csv(morning, evening)
            morning = evening = datetime.now()
            pickle.dump(morning, open("morning.p", "wb"))
            pickle.dump(evening, open("evening.p", "wb"))

        while morning.day == evening.day:
            wait_until_active(0.5)
            now = datetime.now()
            if morning.day != now.day:
                break
            sleep(1)
            evening = datetime.now()
            pickle.dump(evening, open("evening.p", "wb"))


if __name__ == "__main__":
    main()
