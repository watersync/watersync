import plotly.express as px
import plotly.io as pio


def create_sensor_graph(data, deployment):
    plotly_data = {
        "timestamp": [d["timestamp"] for d in data],
        "value": [d["value"] for d in data],
        "type": [d["type"] for d in data],
        "unit": [d["unit"] for d in data],
    }

    fig = px.line(
        data_frame=plotly_data,
        x="timestamp",
        y="value",
        color="type",
        title=f"Sensor Data for {deployment.sensor.identifier}",
        labels={"value": "Measurement value", "timestamp": "timestamp"},
    )
    return pio.to_json(fig)
