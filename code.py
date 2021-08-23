import time
from board import NEOPIXEL
import displayio
import adafruit_display_text.label
from adafruit_datetime import datetime
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network

STOP_ID = 'b994'
DATA_SOURCE = 'https://api.wheresthefuckingtrain.com/by-id/%s' % (STOP_ID,)
DATA_LOCATION = ["data"]
UPDATE_DELAY = 15
MINIMUM_MINUTES_DISPLAY = 9

def get_arrival_in_minutes_from_now(now, date_str):
    train_date = datetime.fromisoformat(date_str).replace(tzinfo=None)
    return round((train_date-now).total_seconds()/60.0)

def get_arrival_times():
    stop_trains =  network.fetch_data(DATA_SOURCE, json_path=(DATA_LOCATION,))
    stop_data = stop_trains[0]
    nortbound_trains = [x['time'] for x in stop_data['N']]
    southbound_trains = [x['time'] for x in stop_data['S']]

    now = datetime.now()
    nortbound_arrivals = [get_arrival_in_minutes_from_now(now, x) for x in nortbound_trains]
    southound_arrivals = [get_arrival_in_minutes_from_now(now, x) for x in southbound_trains]

    n = [str(x) for x in nortbound_arrivals if x>= MINIMUM_MINUTES_DISPLAY]
    s = [str(x) for x in southound_arrivals if x>= MINIMUM_MINUTES_DISPLAY]

    n0 = n[0]
    n1 = n[1] if len(n) > 1 else '-'
    s0 = s[0]
    s1 = s[1] if len(s) > 1 else '-'

    return n0,n1,s0,s1

def update_text(n0, n1, s0, s1):
    text_line2.text = "%s,%s m" % (n0,n1)
    text_line4.text = "%s,%s m" % (s0,s1)
    display.show(group)

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()
bitmap = displayio.OnDiskBitmap(open('example9.bmp', 'rb'))
tile_grid = displayio.TileGrid(bitmap, pixel_shader=getattr(bitmap, 'pixel_shader', displayio.ColorConverter()))
group.append(tile_grid)
color = displayio.Palette(2)
color[0] = 0x444444  # dim white
color[1] = 0xDD8000  # gold

font1 = bitmap_font.load_font("fonts/6x10.bdf")
text_line1 = adafruit_display_text.label.Label(font1, color=color[0], x=20, y=3, text="Queens")
text_line2 = adafruit_display_text.label.Label(font1, color=color[1], x=20, y=11, text="- mins")
text_line3 = adafruit_display_text.label.Label(font1, color=color[0], x=20, y=20, text="Church")
text_line4 = adafruit_display_text.label.Label(font1, color=color[1], x=20, y=28, text="- mins")
group.append(text_line1)
group.append(text_line2)
group.append(text_line3)
group.append(text_line4)

display.show(group)
network.get_local_time()

while True:
    try:
        print("Getting arrival times...")
        arrivals = get_arrival_times()
        update_text(*arrivals)
    except (ValueError, RuntimeError) as e:
        print("Some error occured, retrying! -", e)

    time.sleep(UPDATE_DELAY)
