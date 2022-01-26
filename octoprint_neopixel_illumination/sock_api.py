import json
import logging
import os
import sys
from socketserver import UnixStreamServer, StreamRequestHandler

SOCKET_SERVER_ADDRESS = "/tmp/neopixel_socket"

if os.path.exists(r"/home/pi/.octoprint/logs"):
    log_path = r"/home/pi/.octoprint/logs"
else:
    log_path = "./"
file_handler = logging.FileHandler(os.path.join(log_path, "neopixel_api.log"), "a")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
file_handler.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
stdout_handler.setLevel(logging.DEBUG)

logger = logging.getLogger("octoprint.plugins.neopixel_illumination.api")
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)
logger.setLevel(logging.INFO)

try:
    import microcontroller
    import neopixel

    logger.info("Prod")
except:
    import mocks.microcontroller as microcontroller
    import mocks.neopixel as neopixel

    logger.info("Dev")

PIXEL_CONFIG_DEFAULT = {
    "brightness": 1.0,
    "auto_write": True,
}

pixels: neopixel.NeoPixel = None


class Handler(StreamRequestHandler):
    def process_data(self, data: dict):
        global pixels

        try:
            for key, value in data.items():
                if key == "init":
                    pixel_config = {**PIXEL_CONFIG_DEFAULT, **value}
                    pixel_config["pin"] = microcontroller.Pin(pixel_config["pin"])
                    pixels = neopixel.NeoPixel(**pixel_config)
                elif key == "fill":
                    pixels.fill(value)
                elif key == "pixel":
                    index, color = value
                    pixels[index] = color
                elif key == "brightness":
                    pixels.brightness = value
                elif key == "show":
                    pixels.show()
        except:
            logger.exception("Fail.")

    def handle(self):
        while True:
            message = self.rfile.readline().strip()
            message = message.decode()
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("message `{}`".format(message))
            if message and message.startswith("{"):
                self.process_data(json.loads(message))
            else:
                return


class ThreadedUnixStreamServer(UnixStreamServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        os.chmod(server_address, 0o777)
        logger.info("Server is running on {}".format(server_address))


if __name__ == '__main__':
    logger.info("Starting server".format(SOCKET_SERVER_ADDRESS))
    try:
        os.unlink(SOCKET_SERVER_ADDRESS)
    except OSError:
        if os.path.exists(SOCKET_SERVER_ADDRESS):
            raise

    with ThreadedUnixStreamServer(SOCKET_SERVER_ADDRESS, Handler) as server:
        server.serve_forever()
