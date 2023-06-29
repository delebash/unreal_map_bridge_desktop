# Import the image, math and os libraries
import os
import requests  # The requests package allows use to call URLS
from PIL import Image
import mercantile
import PIL
from requests_cache import NEVER_EXPIRE, CachedSession
import json
from io import BytesIO

session = CachedSession()
session.settings.expire_after = NEVER_EXPIRE


def stitch_tiles(bbox, z, filename, access_token, api_url, base_dir, composite_dir, publisher):
    # access_token = 'pk.eyJ1IjoiZGVsZWJhc2giLCJhIjoiY2t1YWxkODF0MGh2NjJxcXA4czBpdXlmdyJ9.D_ngzR7j4vU1CILtpNLg4Q'
    # terrain_url = 'https://api.mapbox.com/v4/mapbox.terrain-rgb/'
    # api_url = 'https://api.mapbox.com/v4/mapbox.satellite/'
    # elevation_dir = 'elevation_images/'
    # satellite_dir = 'satellite_images/'
    # composite_dir = 'satellite_composite_images/'
    # base_dir = 'F:/3DProjects/github/DansProjects/map_bridge_backend_flask/'
    # os.makedirs(os.path.dirname(base_dir + satellite_dir), exist_ok=True)
    # os.makedirs(os.path.dirname(base_dir + elevation_dir), exist_ok=True)
    os.makedirs(os.path.dirname(base_dir + composite_dir), exist_ok=True)

    top_left_lng = bbox[0]
    top_left_lat = bbox[1]
    bottom_right_lng = bbox[2]
    bottom_right_lat = bbox[3]

    print(top_left_lat)
    tl = [top_left_lat, top_left_lng]
    br = [bottom_right_lat, bottom_right_lng]

    tl_tiles = mercantile.tile(tl[1], tl[0], z)
    br_tiles = mercantile.tile(br[1], br[0], z)
    x_tile_range = [tl_tiles.x, br_tiles.x]
    y_tile_range = [tl_tiles.y, br_tiles.y]
    urls_array = {}
    images_array = {}
    sorted_urls = {}
    # Loop over the tile ranges
    for i, x in enumerate(range(x_tile_range[0], x_tile_range[1] + 1)):
        for j, y in enumerate(range(y_tile_range[0], y_tile_range[1] + 1)):
            url = api_url + str(z) + '/' + str(x) + '/' + str(y) + '@2x.pngraw?access_token=' + access_token
            key = str(i) + '.' + str(j)
            urls_array[key] = url
    sorted_urls = dict(sorted(urls_array.items()))
    total_count = len(sorted_urls)
    count = 0
    for x in sorted_urls:
        response = session.get(sorted_urls[x])
        images_array[x] = response.content
        count = count + 1
        msg = {"event": "stitch_tiles", "process": "downloading_tiles", "count": count, "total_count": total_count,
               "cached": response.from_cache}
        publisher.publish(json.dumps(msg))

    # Open the image set using pillow
    msg = {"event": "stitch_tiles", "process": "opening_images"}
    publisher.publish(json.dumps(msg))
    images = [PIL.Image.open(BytesIO(images_array[x])) for x in images_array]

    # # Calculate the number of image tiles in each direction
    edge_length_x = x_tile_range[1] - x_tile_range[0]
    edge_length_y = y_tile_range[1] - y_tile_range[0]
    edge_length_x = max(1, edge_length_x)
    edge_length_y = max(1, edge_length_y)
    # Find the final composed image dimensions
    width, height = images[0].size
    images.clear()
    total_width = width * edge_length_x
    total_height = height * edge_length_y
    # # Create a new blank image we will fill in
    composite = PIL.Image.new('RGB', (total_width, total_height))
    # # Loop over the x and y ranges
    y_offset = 0
    count = 0
    for i in range(0, edge_length_x):
        x_offset = 0
        for j in range(0, edge_length_y):
            # Open up the image file and paste it into the composed image at the given offset position
            key = str(i) + '.' + str(j)
            tmp_img = PIL.Image.open(BytesIO(images_array[key]))
            composite.paste(tmp_img, (y_offset, x_offset))
            msg = {"event": "stitch_tiles", "process": "combining_images", "count": count, "total_count": total_count}
            publisher.publish(json.dumps(msg))
            x_offset += width  # Update the width
            count = count + 1
        y_offset += height  # Update the height
    # # Save the final image
    msg = {"event": "stitch_tiles", "process": "saving_file"}
    publisher.publish(json.dumps(msg))
    composite.save(base_dir + composite_dir + filename)

# # Testing uncomment
# bbox = [-122.33875557099599, 46.23192217548484, -121.69074845551023, 45.78185052337425]
# zoom = 11
# filename = 'test.png'
# stitch_tiles(bbox, zoom, filename)
