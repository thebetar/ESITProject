# %%
import paho.mqtt.client as mqtt_client
import ssl
import time
import json
from bokeh.plotting import figure, output_file, save

# %%
# Use the same credentials as in Node-RED exercise
broker = ""
port = 0
username = "pi"
password = "raspberry."

# Server certificate PEM file
# TODO fill in the path to your CA certificate
ca_cert = "./isrgrootx1.pem"

# Replace XX by your Raspberry Pi number located on the yellow label
client_id = "EsitApp04"
topic = ""

# Finished_work=True indicates that sufficient data has been collected
mqtt_values = []
finished_work = False


# %%
# The callback for when the client receives a response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(
            "Info: Connected to MQTT Broker as: "
            + client._client_id.decode("UTF-8").lstrip()
        )
        client.subscribe(topic)
    else:
        print("Error: Failed to connect, return code %d\n", rc)


def connect_mqtt():
    # Open connection to MQTT broker
    client = mqtt_client.Client(
        client_id=client_id,
        clean_session=True,
        protocol=mqtt_client.MQTTv311,
        transport="tcp",
    )
    client.username_pw_set(username, password)

    # Set the callbacks for connection and message reception
    client.on_connect = on_connect
    client.on_message = on_message

    # Set TLS parameters for secure connection
    client.tls_set(
        ca_certs=ca_cert,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=mqtt_client.ssl.PROTOCOL_TLS,
    )
    client.tls_insecure_set(False)

    # Connect to the MQTT broker
    client.connect(broker, port)

    return client


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global finished_work

    try:
        payload = msg.payload.decode("utf-8")
        print("Debug: incoming message: topic: " + msg.topic + " payload: " + payload)

        data = json.loads(payload)

        mqtt_values.append(data)

        if len(mqtt_values) >= 10:
            finished_work = True
            print(
                "Info: Finished collecting data, total messages received: ",
                len(mqtt_values),
            )
    except UnicodeDecodeError:
        print("Error: Failed to decode message payload")
        return


# %%
def show_results():
    global mqtt_values

    # Calculate the min, avg, and max values
    min_value = min(mqtt_values, key=lambda x: x["value"])["value"]
    avg_value = sum(d["value"] for d in mqtt_values) / len(mqtt_values)
    max_value = max(mqtt_values, key=lambda x: x["value"])["value"]

    # Print table as shown in figure 2
    print(f"Device: {client_id}")
    print("  light intesity [lux]")
    print("-" * 30)

    for i, data in enumerate(mqtt_values):
        print(f"  {i+1:2d}: {data['value']:5.1f} lux")

    print("-" * 30)
    print(f"min: {min_value:5.1f} lux")
    print(f"avg: {avg_value:5.1f} lux")
    print(f"max: {max_value:5.1f} lux")

    # Print graph as shown in figure 3
    output_file("mqtt_data_plot.html")
    p = figure(
        title="Light measurements",
        x_axis_label="Measurement number",
        y_axis_label="Lux",
    )
    p.line(
        x=range(len(mqtt_values)),
        y=[d["value"] for d in mqtt_values],
        legend_label="Values",
        line_width=2,
    )

    # Save the plot to an HTML file
    save(p)
    print("Info: Plot saved as mqtt_data_plot.html")


# %%
try:
    client = connect_mqtt()
    client.loop_start()

    while True:
        time.sleep(1)

        if finished_work == True:
            print("Info: Finished work, plotting and exiting...")
            show_results()
            break
except KeyboardInterrupt:
    pass
finally:
    client.disconnect()
    print("\nInfo: Client disconnected. Exiting...")
