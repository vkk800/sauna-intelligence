import os
import datetime
import csv

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ruuvitag_sensor.ruuvitag import RuuviTag


_fields = ('time', 'temperature', 'pressure', 'humidity')


def maybe_create_log(logfile):
    """Creates a .csv file with the correct column names if it doesn't exist.

    # Arguments
        logfile: str. Path to the logfile
    """
    if os.path.isfile(logfile):
        return
    with open(logfile, 'w') as f:
        f.write(",".join(_fields) + "\n")


def log_reading(mac, logfile=None):
    """Reads the state of a Ruubitag and writes it into a logfile if provided.
    The logfile is created if it doesn't already exist.

    # Arguments
        mac: str. MAC-address of the ruuvitag
        logfile: str or None (default None). Path to the logfile. If `None`,
            the reading is just returned and nothing gets logged.
    """
    sensor = RuuviTag(mac)
    sensor.update()
    reading = sensor.state
    reading['time'] = str(datetime.datetime.now())
    if logfile:
        maybe_create_log(logfile)
        with open(logfile, 'a', newline='\n') as f:
            dw = csv.DictWriter(f, fieldnames=_fields, extrasaction='ignore')
            dw.writerow(reading)
    return reading


def create_figures(logfile, picfile):
    """Creates figures from `logfile`. The output is one picture
    which is saved into `picfile`.
    """
    now = datetime.datetime.now()

    plt.style.use("seaborn")

    fig, ax = plt.subplots(3, 2, figsize=(14, 21))
    df = pd.read_csv(logfile, index_col='time', parse_dates=True)

    lw = np.datetime64(now) - np.timedelta64(1, 'W')
    df[df.index > lw]['temperature'].plot(ax=ax[0, 0])
    ax[0, 0].set_title("Temp: last week")
    lw = np.datetime64(now) - np.timedelta64(1, 'W')
    df[df.index > lw]['humidity'].plot(ax=ax[0, 1])
    ax[0, 1].set_title("Humidity: last week")

    ld = np.datetime64(now) - np.timedelta64(1, 'D')
    df[df.index > ld]['temperature'].plot(ax=ax[1, 0])
    ax[1, 0].set_title("Temp: today")
    ld = np.datetime64(now) - np.timedelta64(1, 'D')
    df[df.index > ld]['humidity'].plot(ax=ax[1, 1])
    ax[1, 1].set_title("Humidity: today")

    l2h = np.datetime64(now) - np.timedelta64(2, 'h')
    df[df.index > l2h]['temperature'].plot(ax=ax[2, 0])
    ax[2, 0].set_title("Temp: last two hours")
    l2h = np.datetime64(now) - np.timedelta64(2, 'h')
    df[df.index > l2h]['humidity'].plot(ax=ax[2, 1])
    ax[2, 1].set_title("Humidity: last two hours")

    plt.tight_layout()
    plt.savefig(picfile)
    plt.close(fig)


def create_html(html_file, logfile, picpath):
    """Creates a report of the log as html file and saves it to path
    `html_file`. `logfile` is the path to the log used as data for the
    file. `picpath` is the desired path for storing the figures included
    in the html.
    """
    create_figures(logfile, picpath+"temps.png")
    df = pd.read_csv(logfile, index_col='time', parse_dates=True)
    contents = """<!DOCTYPE html>
    <html>
    <p>
    Last reading: {time}\n |

    Temp: {temp}\n |

    Pressure: {press}\n |

    Humidity: {humid}\n\n

    </p>
    <p>
    <img src="{pic}">
    </p>
    </html>
    """.format(time=df.tail(1).index[0].strftime("%Y-%m-%d %H:%M:%S"),
               temp=df.tail(1)['temperature'][0],
               press=df.tail(1)['pressure'][0],
               humid=df.tail(1)['humidity'][0],
               pic="temps.png")
    with open(html_file, 'w') as f:
        f.write(contents)
