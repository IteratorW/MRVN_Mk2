import logging
import os
import subprocess
import typing
from io import BytesIO
from typing import Optional

import numpy as np
from PIL import Image

# ATTENTION: all the code stolen from https://github.com/LinesGuy/img_sussifier :3

FFMPEG_CMD = "ffmpeg " \
             "-f image2 " \
             "-i sussified_{0}_%d.png " \
             "-filter_complex \"[0:v] " \
             "scale=sws_dither=none:,split [a][b];[a] " \
             "palettegen=max_colors=255:stats_mode=single [p];[b][p] paletteuse=dither=none\" " \
             "-r 20 " \
             "-y -hide_banner " \
             "-loglevel error " \
             "sussified_{0}.gif"

logger = logging.getLogger("fun stuff sussifier")

twerk_frames = []
twerk_frames_data = []  # Image as numpy array, pre-calculated for performance


def prepare_sus_twerk():
    path = os.path.dirname(os.path.realpath(__file__))

    for i in range(6):
        try:
            img = Image.open(f"{path}/twerk_imgs/{i}.png").convert("RGBA")
        except Exception:
            logger.error(f"Error loading sus twerk frame {i}")

            return

        twerk_frames.append(img)
        # noinspection PyTypeChecker
        twerk_frames_data.append(np.array(img))


def sussify(image: typing.IO, filename: str, output_width: int = 21) -> Optional[bytes]:
    if len(twerk_frames) + len(twerk_frames_data) != 12:
        return None

    twerk_width, twerk_height = twerk_frames[0].size

    input_image = Image.open(image).convert("RGB")

    input_width, input_height = input_image.size

    # Height of output gif (in crewmates)
    output_height = int(output_width * (input_height / input_width) * (twerk_width / twerk_height))

    # Width, height of output in pixels
    output_px = (int(output_width * twerk_width), int(output_height * twerk_height))

    # Scale image to number of crewmates, so each crewmate gets one color
    input_image_scaled = input_image.resize((output_width, output_height), Image.NEAREST)

    for frame_number in range(6):
        # Create blank canvas
        background = Image.new(mode="RGBA", size=output_px)
        for y in range(output_height):
            for x in range(output_width):
                r, g, b = input_image_scaled.getpixel((x, y))

                # Grab the twerk data we calculated earlier
                # (x - y + frame_number) is the animation frame index,
                # we use the position and frame number as offsets to produce the wave-like effect
                sussified_frame_data = np.copy(twerk_frames_data[(x - y + frame_number) % len(twerk_frames)])
                red, green, blue, alpha = sussified_frame_data.T
                # Replace all pixels with colour (214,224,240) with the input image colour at that location
                color_1 = (red == 214) & (green == 224) & (blue == 240)
                sussified_frame_data[..., :-1][color_1.T] = (r, g, b)  # thx stackoverflow
                # Repeat with colour (131,148,191) but use two thirds of the input image colour to get a darker colour
                color_2 = (red == 131) & (green == 148) & (blue == 191)
                sussified_frame_data[..., :-1][color_2.T] = (int(r * 2 / 3), int(g * 2 / 3), int(b * 2 / 3))

                # Convert sussy frame data back to sussy frame
                sussified_frame = Image.fromarray(sussified_frame_data)

                # Slap said frame onto the background
                background.paste(sussified_frame, (x * twerk_width, y * twerk_height))
        background.save(f"sussified_{filename}_{frame_number}.png")

    # Convert sussied frames to gif. PIL has a built-in method to save gifs but
    # it has dithering which looks sus, so we use ffmpeg with dither=none

    try:
        subprocess.check_output(
            FFMPEG_CMD.format(filename),
            shell=True)
    except subprocess.SubprocessError:
        return None

    with open(f"./sussified_{filename}.gif", "rb") as f:
        result = f.read()

    # Remove temp files
    for frame_number in range(6):
        os.remove(f"sussified_{filename}_{frame_number}.png")

    os.remove(f"./sussified_{filename}.gif")

    return result


try:
    subprocess.check_output("ffmpeg -version", shell=True, stderr=subprocess.DEVNULL)
except subprocess.SubprocessError:
    logger.error("ffmpeg is not installed :(")

prepare_sus_twerk()
