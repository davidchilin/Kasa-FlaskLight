#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_from_directory
from pyHS100 import SmartBulb

BULB_IP = "KASA_BULB_IP"
bulb = None

try:
    bulb = SmartBulb(BULB_IP)
    bulb.get_sysinfo()
except Exception as e:
    bulb = None

app = Flask(__name__)


@app.route("/")
def index():
    if bulb is None:
        return (
            "Error: SmartBulb not connected or failed to initialize. Check IP address and server logs.",
            500,
        )

    html_content = """<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> Kasa Light Control </title>
    <link rel="stylesheet" type="text/css" href="/static/css/themes.css" />
    <script type="text/javascript" src="/static/js/colorpicker.js"></script>

  <style type="text/css">
  body{
          background:#000;
          color:#FFFFFF;
          font-family: Arial, sans-serif;
          display: flex;
          flex-direction: column;
          align-items: center;
          margin: 0;
          padding: 5px 0;
      }
  .container {
          margin: 10px 0;
          width: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
      }
  .controls-container, .state-container {
        background: #111;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        width: 350px;
        max-width: 95%;
        box-sizing: border-box;
      }
  h1 { font-size: 1.5em; text-align: center; margin-bottom: 10px; }
  h2 { font-size: 1.3em; text-align: center; margin-bottom: 10px; }

  button {
        padding: 10px;
        border-radius: 5px;
        border: 2px solid #007700;
        background: #000;
        color: #00FF00;
        cursor: pointer;
        font-size: 1em;
      }
  button:hover { background: #333; }

  .button-row-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin: 10px 0;
      }
  .power-btn
        width: 35%;
        min-width: 80px;
        margin: 0 1%;
        padding: 10px 0;
        box-sizing: border-box;
        text-align: center;
      }
  .brightness-btn
        width: 18%;
        min-width: 50px;
        margin: 0 1%;
        padding: 10px 0;
        box-sizing: border-box;
        text-align: center;
      }

  label {
        display: block;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 8px;
      }
  input[type="range"] {
        display: block;
        width: calc(100% - 20px);
        margin: 10px auto 25px auto;
        -webkit-appearance: none;
        appearance: none;
        height: 8px;
        background: #333;
        border-radius: 5px;
        outline: none;
      }
    input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 20px;
        height: 20px;
        background: #00FF00;
        cursor: pointer;
        border-radius: 50%;
      }
    input[type="range"]::-moz-range-thumb {
        width: 20px;
        height: 20px;
        background: #00FF00;
        cursor: pointer;
        border-radius: 50%;
        border: none;
      }

  #colorPickerContainer {
        width: 100%;
        max-width: 260px;
        height: 0;
        padding-bottom: 60%;

        position: relative; /* Usually good for JS components placing elements inside */
        margin: 10px auto 10px auto;
        border: 4px solid #444; /* Border to see container bounds and background */
        box-sizing: border-box;

        /* Attempt to move hue slider to the left */
        display: flex;
        flex-direction: row-reverse; /* This tries to put the second main child (often hue) first */
      }

  #lightstate {
        margin-top:10px;
        font-size: 1.1em;
        word-wrap: break-word;
      }

  @media (max-width: 480px) {
        body { font-size: 15px; }
        .controls-container, .state-container { padding: 15px; width: 95%; }
        h1 { font-size: 1.6em; }
        h2 { font-size: 1.2em; }
        .brightness-btn { padding: 8px 0px; font-size: 0.9em; min-width: 45px; }
        .power-btn { font-size: 0.95em; min-width: 70px; width: 30%;} /* Adjust power button width for mobile */
        #colorPickerContainer {
            max-width: 220px;
        }
        label { margin-top: 20px; }
  }
  @media (max-width: 360px) {
        .button-row-container { flex-wrap: wrap; } /* Allow button rows to wrap */
        .brightness-btn { width: 30%; margin-bottom:10px; font-size: 0.85em; min-width: 40px; }
        .power-btn { width: 40%; margin-bottom:10px; }
        #colorPickerContainer {
            max-width: 180px;
        }
  }
  </style>
  </head>

  <body>
  <div class="container">
    <h1> Kasa Light Control </h1>
    <div class="controls-container">
    <form id="controls" style="text-align:center;">
      <div class="button-row-container">
          <button name="on" type="button" class="power-btn">On</button>
          <button name="off" type="button" class="power-btn">Off</button>
      </div>

      <div class="button-row-container">
          <button name="bright1" type="button" class="brightness-btn">1%</button>
          <button name="bright25" type="button" class="brightness-btn">25%</button>
          <button name="bright50" type="button" class="brightness-btn">50%</button>
          <button name="bright75" type="button" class="brightness-btn">75%</button>
          <button name="bright100" type="button" class="brightness-btn">100%</button>
      </div>

      <label for="brightnessValue">Brightness</label>
      <input type="range" id="brightnessValue" name="brightnessValue" min="1" max="100" step="5" />

      <label for="temperatureValue">Temperature</label>
      <input type="range" id="temperatureValue" name="temperature" min="2500" max="9000" step="500" />

      <label for="colorPickerContainer"></label>
      <div id="colorPickerContainer"></div>
    </form>
    </div>
    <div id="state" class="state-container" style="text-align:center;">
        <h2>Light is currently</h2>
        <div id="lightstate">Loading...</div>
    </div>
  </div>

  <script>
     var form = document.getElementById('controls');
     var lightstate = document.getElementById('lightstate');
     var cp;
     var isUpdatingPickerViaCode = false;
     const colorPickerContainerElement = document.getElementById('colorPickerContainer'); // Get reference once

     function updateLightState(){
      fetch('/lightState')
        .then(r => r.json())
        .then(o => {
          if (o.error) {
              lightstate.innerHTML = `<b style='color:red;'>Error: ${o.error}</b>`;
              return;
          }
          let statusText = `<b style='color:${o.state === 'ON' ? 'lime' : 'red'};'>${o.state}</b>`;
          statusText += ` at Brightness: ${o.brightness}%`;

          document.getElementById('brightnessValue').value = o.brightness;

          if (o.temperature !== null && o.temperature > 0) {
            statusText += ` | Temp: ${o.temperature}K`;
            const tempSlider = document.getElementById('temperatureValue');
            if (o.temperature >= parseInt(tempSlider.min) && o.temperature <= parseInt(tempSlider.max)) {
                 tempSlider.value = o.temperature;
            }
          }

          if (o.hsv && o.hsv.length === 3) {
            statusText += ` | (HSV): ${o.hsv[0]}&deg;, ${o.hsv[1]}%, ${o.hsv[2]}%`;
            if (cp) {
                isUpdatingPickerViaCode = true;
                cp.setHsv({ h: o.hsv[0], s: o.hsv[1] / 100, v: o.hsv[2] / 100 });
                // The setHsv might trigger the callback with the new hex, updating background
                isUpdatingPickerViaCode = false;
            }
          }
          lightstate.innerHTML = statusText;
        })
        .catch(error => {
            lightstate.innerHTML = "<b style='color:red;'>Error fetching state. Check connection.</b>";
        });
      }

      function setLightBright(brightness){
        fetch(`/brightness?brightness=${brightness}`).then(updateLightState);
      }

      function setLightTemp(temperature){
        fetch(`/temperature?temperature=${temperature}`).then(updateLightState);
      }

      function setLightColor(h, s, v){
        const url = `/color?h=${Math.round(h)}&s=${Math.round(s)}&v=${Math.round(v)}`;
        fetch(url)
          .then(response => response.json())
          .then(data => {
            updateLightState();
          })
          .catch(error => {
            updateLightState();
          });
      }

      form.on.onclick = e => { fetch('/lightOn').then(r => r.json()).finally(updateLightState); };
      form.off.onclick = e => { fetch('/lightOff').then(r => r.json()).finally(updateLightState); };

      [1, 25, 50, 75, 100].forEach(val => {
        form[`bright${val}`].onclick = e => { setLightBright(val); };
      });

      form.brightnessValue.onchange = e => { setLightBright(e.target.value); };
      form.temperatureValue.onchange = e => { setLightTemp(e.target.value); };

      document.addEventListener('DOMContentLoaded', (event) => {
          // colorPickerContainerElement is already defined globally in this script block scope
          if (colorPickerContainerElement) {
            if (typeof ColorPicker === 'function') {
                try {
                    cp = ColorPicker(
                        colorPickerContainerElement, // Use the stored reference
                        function(hex, hsv, rgb, pickerCoordinate, sliderCoordinate) {
                            if (colorPickerContainerElement && hex) { // Update background on interaction
                                colorPickerContainerElement.style.backgroundColor = hex;
                            }
                            if (isUpdatingPickerViaCode) { return; }
                            setLightColor(hsv.h, hsv.s * 100, hsv.v * 100);
                        }
                    );
                    // After init, if we have an initial HSV from first updateLightState,
                    // we might want to set the initial background.
                    // This requires updateLightState to run first or to pass initial state.
                    // For now, background updates on first interaction or first programmatic setHsv
                    // if the callback's hex argument gets populated correctly.
                } catch (e) {
                    console.error('Error initializing ColorPicker:', e);
                }
            } else {
                console.error('ColorPicker function IS NOT defined! Check flexiColorPicker.js.');
            }
          } else {
            console.error("colorPickerContainer element NOT found!");
          }
          updateLightState();
      });
    </script>
  </body>
</html>
"""
    return html_content


# --- Python Flask Routes (Remain Unchanged from the last working version) ---
@app.route("/lightOn")
def lightOn():
    if not bulb:
        return jsonify(error="Bulb not initialized"), 500
    try:
        bulb.turn_on()
        return jsonify(state="ON" if bulb.is_on else "OFF", brightness=bulb.brightness)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/lightOff")
def lightOff():
    if not bulb:
        return jsonify(error="Bulb not initialized"), 500
    try:
        bulb.turn_off()
        return jsonify(
            state="OFF" if not bulb.is_on else "ON", brightness=bulb.brightness
        )
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/lightState")
def lightState():
    if not bulb:
        return (
            jsonify(
                error="Bulb not initialized",
                state="ERROR",
                brightness=0,
                temperature=None,
                hsv=None,
            ),
            500,
        )
    try:
        state_info = {
            "state": "ON" if bulb.is_on else "OFF",
            "brightness": bulb.brightness,
            "temperature": None,
            "hsv": None,
        }
        active_color_temp = None
        if bulb.is_variable_color_temp:
            current_temp_val = bulb.color_temp
            if current_temp_val and current_temp_val > 0:
                active_color_temp = current_temp_val
                state_info["temperature"] = active_color_temp
                state_info["hsv"] = (0, 0, state_info["brightness"])

        if active_color_temp is None and bulb.is_color:
            state_info["hsv"] = bulb.hsv
        elif not bulb.is_color and active_color_temp is None:
            state_info["hsv"] = (0, 0, state_info["brightness"])

        return jsonify(state_info)
    except Exception as e:
        return (
            jsonify(
                error=str(e), state="ERROR", brightness=0, temperature=None, hsv=None
            ),
            500,
        )


@app.route("/brightness")
def lightSetBright():
    if not bulb:
        return jsonify(error="Bulb not initialized"), 500
    try:
        brightness = request.args.get("brightness", default=100, type=int)
        bulb.brightness = brightness
        return jsonify(brightness=bulb.brightness)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/temperature")
def lightSetTemp():
    if not bulb:
        return jsonify(error="Bulb not initialized"), 500
    try:
        temperature = request.args.get("temperature", default=5000, type=int)
        if bulb.is_variable_color_temp:
            bulb.color_temp = temperature
            return jsonify(temperature=bulb.color_temp)
        else:
            return (
                jsonify(
                    temperature=None,
                    message="Bulb does not support variable temperature.",
                ),
                400,
            )
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/color")
def lightSetColor():
    if not bulb:
        return jsonify(error="Bulb not initialized"), 500
    try:
        h = request.args.get("h", type=int)
        s = request.args.get("s", type=int)
        v = request.args.get("v", type=int)

        if not bulb.is_color:
            return jsonify(hsv=None, message="Bulb does not support color."), 400

        if h is not None and s is not None and v is not None:
            h = max(0, min(360, h))
            s = max(0, min(100, s))
            v = max(0, min(100, v))

            if not bulb.is_on:
                bulb.turn_on()
            bulb.hsv = (h, s, v)
            return jsonify(hsv=bulb.hsv, brightness=bulb.brightness)
        else:
            return (
                jsonify(
                    hsv=None,
                    message="One or more HSV parameters are missing or invalid.",
                ),
                400,
            )
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.root_path,
        "free-icon-light-bulb.png",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
