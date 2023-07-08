# Import the image, math and os libraries
# import os
# import requests  # The requests package allows use to call URLS
import mercantile
from PIL import Image, ImageFilter
from requests_cache import NEVER_EXPIRE, CachedSession
import json
from io import BytesIO
from osgeo import gdal
from osgeo import gdal_array
import numpy as np
from scipy.ndimage.filters import gaussian_filter

# BASE_DIR = os.curdir
# os.environ['PATH'] = os.path.join(BASE_DIR, r'venv\Lib\site-packages\osgeo') + ';' + os.environ['PATH']
# os.environ['PROJ_LIB'] = os.path.join(BASE_DIR, r'env3\Lib\site-packages\osgeo\data\proj') + ';' + os.environ['PATH']
# GDAL_LIBRARY_PATH = os.path.join(BASE_DIR, r'venv\lib\site-packages\osgeo\gdal300.dll')
session = CachedSession()
session.settings.expire_after = NEVER_EXPIRE


# global_publisher = None


def stitch_tiles(bbox, z, filename, access_token, api_url, base_dir, sub_dir, publisher, is_heightmap,
                 landscape_size, is_sealevel, flipx, flipy, heightmapblurradius):
    # os.makedirs(os.path.dirname(base_dir), exist_ok=True)
    # global_publisher = publisher
    save_path = base_dir + '/' + sub_dir + '/' + filename
    top_left_lng = bbox[0]
    top_left_lat = bbox[1]
    bottom_right_lng = bbox[2]
    bottom_right_lat = bbox[3]

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
            url = api_url + str(z) + '/' + str(x) + '/' + str(y) + access_token
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
    images = [Image.open(BytesIO(images_array[x])) for x in images_array]

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
    composite = Image.new('RGB', (total_width, total_height))
    # # Loop over the x and y ranges
    y_offset = 0
    count = 0
    for i in range(0, edge_length_x):
        x_offset = 0
        for j in range(0, edge_length_y):
            # Open up the image file and paste it into the composed image at the given offset position
            key = str(i) + '.' + str(j)
            tmp_img = Image.open(BytesIO(images_array[key]))
            composite.paste(tmp_img, (y_offset, x_offset))
            msg = {"event": "stitch_tiles", "process": "combining_images", "count": count, "total_count": total_count}
            publisher.publish(json.dumps(msg))
            x_offset += width  # Update the width
            count = count + 1
        y_offset += height  # Update the height
    images_array.clear()

    if is_heightmap:
        rgb_elevation = composite.convert('RGB')
        rgb_data = np.array(rgb_elevation)
        composite = None
        r = rgb_data[..., 0].astype(np.float32)
        g = rgb_data[..., 1].astype(np.float32)
        b = rgb_data[..., 2].astype(np.float32)
        decoded_data = -10000 + ((r * 256 * 256 + g * 256 + b) * 0.1)
        im = np.array(decoded_data)
        decoded_data = None
        # im2 = (65535 * (im - im.min()) / im.ptp()).astype(np.uint16)
        im2 = ((im - im.min()) / (im.max() - im.min()) * 32767).astype(np.uint16)
        im = None
        if heightmapblurradius:
            im2 = gaussian_filter(im2, sigma=int(heightmapblurradius))
        if flipx:
            im2 = np.fliplr(im2)
        if flipy:
            im2 = np.flipud(im2)

        # composite = Image.fromarray(im2)
        # composite.save(save_path)

        ds = gdal_array.OpenArray(im2)

        sealevel = '32767'
        imax = '65535'
        imin = '0'
        resize = 'bilinear'

        kwargs = {'format': 'PNG', 'outputType': gdal.GDT_UInt16}
        if is_sealevel:
            kwargs['scaleParams'] = [[imin, imax, sealevel, imax]]

        if int(landscape_size) > 0:
            kwargs['width'] = landscape_size
            kwargs['height'] = landscape_size
            kwargs['resampleAlg'] = resize

        gdal.Translate(save_path, ds, **kwargs, callback=progress_cb, callback_data=publisher)
        ds = None
    else:
        # Save the final image
        msg = {"event": "stitch_tiles", "process": "saving_file"}
        publisher.publish(json.dumps(msg))
        composite.save(save_path)
        composite.close()


def progress_cb(complete, message, cb_data):
    msg = {"event": "stitch_tiles", "process": "gdal_resampling", "count": int(complete * 100), "total_count": 100}
    cb_data.publish(json.dumps(msg))
    # if int(complete * 100) % 10 == 0:
    #     print(f'{complete * 100:.0f}', end='', flush=True)
    # elif int(complete * 100) % 3 == 0:
    #     print(f'{cb_data}', end='', flush=True)

# # Testing uncomment
# bbox = [-122.33875557099599, 46.23192217548484, -121.69074845551023, 45.78185052337425]
# zoom = 11
# filename = 'test.png'
# stitch_tiles(bbox, zoom, filename)
