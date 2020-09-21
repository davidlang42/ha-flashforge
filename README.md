FlashForge API
=======================

This is an unofficial interpretation of the FlashForge API by 01F0 using a Flashforge Finder 3d printer.
The api has been written into a simple HomeAssistant integration by davidlang42.

Warning
=======================
Use at your own risk. It only does reading operations but it is unofficial and may of course have bugs etc.
This API is done solely by reverse engineering.

Installation instructions
=======================
* Open HACS (https://hacs.xyz/) in HomeAssistant UI
* Add a custom repository: https://github.com/davidlang42/ha-flashforge
* Install "Flashforge API"
* Configure in YAML as below

```
sensor:
  - platform: flashforge
    name: Flashforge 3d printer
    host: X.X.X.X # IP address of your printer
    port: 8899 # Optional, default 8899
    include_info: True # Optional, default True, includes general device details (model, serial, firmware version, etc)
    include_head: True # Optional, default True, includes head position
    include_temp: True # Optional, default True, includes temperature current/target
    include_progress: True # Optional, default True, includes printing progress
    debug: False # Optional, default False, if true it will include debug information in the state attributes
```

Does it support other FlashForge models?
=======================
So far it has been tested on:
* Finder (by 01F0)
* Adventurer (by davidlang42)

If you have another flashforge model, try enabling debug mode in YAML config (as above) and send the state attributes to us to update the value parsing.
