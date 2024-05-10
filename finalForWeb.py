import network
import socket
from time import sleep
from machine import Pin, ADC
from dht import DHT11

SENSOR_COEFFICIENTS = {
    'CO': 0.8,
    'NH4': 0.7,
    'Alcohol': 1.2,
    'CH4': 1.0,
    'Butane': 0.9,
}

# Define your network credentials
ssid = 'RVU'
password = 'RVU@guru'

data_pin = 15
data_pin_object = Pin(data_pin, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(data_pin_object)

MQ135_PIN = ADC(Pin(26))

def read_dht11():
    sensor.measure()  # Perform measurement
    temperature_celsius = sensor.temperature  # Read temperature
    humidity_percentage = sensor.humidity  # Read humidity
    return temperature_celsius, humidity_percentage

# Connect to WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
    print('Connecting...')
    sleep(1)
ip = wlan.ifconfig()[0]
print('Connection successful')
print(f'Connected on {ip}')

def generate_html(gas_ppm, temperature, humidity):
    temperature_str = f"{temperature:.2f} °C" 
    humidity_str = f"{humidity:.2f} %" 

    html_template = f"""
    <html>
    <head>
        <title>Raspberry Pico W - Gas Sensor</title>

        <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        h1 {{
            text-align: center;
        }}
        .grid-container {{
            display: grid;
            grid-template-columns: auto auto auto;
            gap: 20px; /* Add space between the boxes */
            padding: 10px;
        }}
        .grid-item {{
            border: 1px solid rgba(0, 0, 0, 0.8);
            border-radius: 15px; /* Increase border radius */
            padding: 20px;
            font-size: 30px;
            text-align: center;
        }}
        .inner-box {{
            width: 50px;
            height: 50px;
            margin: auto;
            border: 1px solid black;
        }}
        .inner-box img {{
            max-width: 100%; /* Limit the image size */
            height: auto;
        }}
        .btn {{
            margin-top: 10px;
            color: white;
        }}
        /* Style for the table */
        table {{
            width: 100%;
            margin-top: 20px;
        }}
        th, td {{
            border: 1px solid black;
            padding: 10px;
            text-align: center;
            background-color: #f2f2f2; /* Add a background color to the headings */
        }}
        </style>
    </head>
    <body>
        <h1>Environment Monitoring:</h1>
        <table>
        <tr>
            <th>NH4</th>
            <th>CO</th>
            <th>Alcohol</th>
            <th>CH4</th>
            <th>CO2</th>
            <th>Butane</th>
            <th>Humidity</th>
            <th>Temperature</th>
        </tr>
        <tr>
            {''.join(gas_data)}
            <td>{humidity:.2f} %</td>
            <td>{temperature:.2f} °C</td>
        </tr>
        </table>

        <div class="grid-container">
            <div class="grid-item">
                <div class="inner-box">
                    <img src="https://shorturl.at/wBFP6" alt="Image">
                </div>
                <button class="btn" onclick="changeColor(this)">Good</button>
            </div>
            <div class="grid-item">
                <div class="inner-box">
                    <img src="RedSaucePasta1.jpg" alt="Image">
                </div>
                <button class="btn" onclick="changeColor(this)">Good</button>
            </div>
            <div class="grid-item">
                <div class="inner-box">
                    <img src="RedSaucePasta1.jpg" alt="Image">
                </div>
                <button class="btn" onclick="changeColor(this)">Good</button>
            </div>
            <div class="grid-item">
                <div class="inner-box">
                    <img src="RedSaucePasta1.jpg" alt="Image">
                </div>
                <button class="btn" onclick="changeColor(this)">Good</button>
            </div>
            <div class="grid-item">
                <div class="inner-box">
                    <img src="RedSaucePasta1.jpg" alt="Image">
                </div>
            <button class="btn" onclick="changeColor(this)">Good</button>
            </div>
            <div class="grid-item">
                <div class="inner-box">
                    <img src="RedSaucePasta1.jpg" alt="Image">
                </div>
            <button class="btn" onclick="changeColor(this)">Good</button>
            </div>
        </div>

        <script>
        function changeColor(element) {{
            if (element.innerHTML === "Good") {{
                element.style.backgroundColor = "orange";
                element.innerHTML = "Moderate";
            }} 
            else if (element.innerHTML === "Moderate") {{
                element.style.backgroundColor = "red";
                element.innerHTML = "Danger";
            }} 
            else {{
                element.style.backgroundColor = "green";
                element.innerHTML = "Good";
            }}
        }}
        </script>
    </body>
    </html>
    """
    return html_template

def generate_gas_data_html(data):
    html = ""
    for value in data:
        html += f"<td>{value:.2f} ppm</td>"
    return html

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, 80))
    server.listen(1)
    selected_gas = 'CO'  # Default selected gas

    while True:
        client, addr = server.accept()
        request = client.recv(1024).decode()
        # Parse the request to handle gas selection (if submitted)
        if request.startswith('POST'):
            # Extract selected gas from form data (assuming basic parsing)
            try:
                selected_gas = request.split('=')[-1].split('&')[0]
            except IndexError:
                pass

        # Read MQ135 sensor data
        analog_value = MQ135_PIN.read_u16()
        gas_ppm = 100 * (1 - analog_value / 65535) * SENSOR_COEFFICIENTS.get(selected_gas, 1.0)

        # Read DHT11 sensor data
        temperature, humidity = read_dht11()

        # Generate gas data HTML
        gas_data_html = generate_gas_data_html([gas_ppm] * 6)

        # Generate complete HTML page
        html_page = generate_html(gas_data_html, temperature, humidity)
        
        client.send(html_page)
        client.close()
                 
if __name__ == '__main__':
    main()