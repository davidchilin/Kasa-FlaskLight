# Kasa FlaskLight

FlaskLight updated with color picker from FlexiColorPicker https://github.com/DavidDurman/FlexiColorPicker. get some practice with llm.
Used older Kasa Smartbulb library pyHS100, but you can also update to python-kasa which uses asyncio.

 ![Screenshot](https://github.com/davidchilin/Kasa-FlaskLight/blob/master/lamp_control.jpg?raw=true)

## Q&A
- Doesn't  KASA already have a mobile app and cloud site to do this with?
	 - Avoid using some of the vendor lock in software.
     This allows me to access it from any device without installing anything

- How do I use this dang thing?
	- Connect the KASA bulb to your wifi using their pesky mobile app
	-  Change the `bulb = SmartBulb("192.168.1.253")` in app.py to the IP of your bulb
	-  Run `pip3 install -r requirements.txt`
	-  Run ./run.sh
	-  Connect to localhost:8123, or whatever you want to set, at the very end of app.py
- How do I find the IP of my bulb?
  - Run `pyhs100` with no arguments in a shell after installing the requirements with pip
- Help, I can't access the interface!
	- By default Flask runs the dev server bound to 127.0.0.1 (localhost) only, if you're running the app on a different machine locally, you'll need to run `FLASK_APP=app.py flask run -h 0.0.0.0` to bind to all IPs
