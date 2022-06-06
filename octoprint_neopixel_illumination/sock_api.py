import getopt
import json
import logging
import os
import sys
from socketserver import UnixStreamServer, StreamRequestHandler

SOCKET_SERVER_ADDRESS = "/tmp/neopixel_socket"

logger: logging.Logger = None


def setup_logger(log_path):
    global logger
    file_handler = logging.FileHandler(log_path, "a")
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
except:
    import mocks.microcontroller as microcontroller
    import mocks.neopixel as neopixel

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
                    pixels.brightness = float(value)
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
    log_path = "/tmp/plugin_neopixel_illumination_api.log"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:")
    except getopt.GetoptError:
        print(f"{sys.argv[0]} -l <log path>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-l":
            log_path = arg

    setup_logger(log_path)

    logger.info("Starting server".format(SOCKET_SERVER_ADDRESS))
    try:
        os.unlink(SOCKET_SERVER_ADDRESS)
    except OSError:
        if os.path.exists(SOCKET_SERVER_ADDRESS):
            raise

    with ThreadedUnixStreamServer(SOCKET_SERVER_ADDRESS, Handler) as server:
        server.serve_forever()
