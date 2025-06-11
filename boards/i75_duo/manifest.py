require("bundle-networking")
require("urllib.urequest")
require("umqtt.simple")

# Bluetooth
require("aioble")

include("../manifest-common.py")

freeze("../../modules/wireless/")
freeze("../../modules/duo75/", "interstate75.py")