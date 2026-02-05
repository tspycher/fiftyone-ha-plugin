# FiftyOne Home Assistant Integration

Custom Home Assistant integration for the FiftyOne API.

## Features

### Stock Information
- Track stock prices, quantities, and total values
- Sensors for each stock symbol showing:
  - Current price
  - Total value (price × quantity)
  - Quantity held

### Aviation Data (LSZI)
- Weather sensors:
  - Temperature (OAT)
  - Humidity
  - Pressure (QNH)
  - Wind speed and direction
  - Cloud base
  - Density altitude
  - Pressure altitude
- Runway status sensor

### Webcams
- Live camera images from Swiss city webcams:
  - Basel
  - Bern
  - Lucerne
  - Zurich

### Image Sources
- Configure multiple image sources using unique codes
- Each source provides:
  - Latest image entity
  - Random image entity
- Manage sources via integration options

## Installation

### Manual Installation

1. Copy the `custom_components/fiftyone` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "FiftyOne" and follow the setup wizard

### HACS Installation

1. Add this repository as a custom repository in HACS
2. Search for "FiftyOne" and install
3. Restart Home Assistant
4. Configure via the integrations page

## Configuration

The integration is configured through the Home Assistant UI:

1. **API URL**: The URL of your FiftyOne API (default: `https://api.fiftyone.dev`)
2. **Image Sources**: Add one or more image sources by providing:
   - **Code**: The unique source code for the image API
   - **Name**: A friendly display name (optional, defaults to code)

### Managing Image Sources

After initial setup, you can add or remove image sources via:
**Settings** → **Devices & Services** → **FiftyOne** → **Configure**

## Entities Created

### Sensors

| Entity | Description |
|--------|-------------|
| `sensor.{symbol}_price` | Current stock price |
| `sensor.{symbol}_value` | Total value of stock holdings |
| `sensor.{symbol}_quantity` | Number of shares held |
| `sensor.lszi_temperature` | Outside air temperature |
| `sensor.lszi_humidity` | Relative humidity |
| `sensor.lszi_pressure` | Atmospheric pressure (QNH) |
| `sensor.lszi_wind_speed` | Wind speed in knots |
| `sensor.lszi_wind_direction` | Wind direction in degrees |
| `sensor.lszi_cloud_base` | Cloud base in feet |
| `sensor.lszi_density_altitude` | Density altitude in feet |
| `sensor.lszi_pressure_altitude` | Pressure altitude in feet |
| `sensor.lszi_runway_status` | Current runway status |

### Cameras (Webcams)

| Entity | Description |
|--------|-------------|
| `camera.webcam_basel` | Basel city webcam |
| `camera.webcam_bern` | Bern city webcam |
| `camera.webcam_lucerne` | Lucerne city webcam |
| `camera.webcam_zurich` | Zurich city webcam |

### Images (per configured source)

| Entity | Description |
|--------|-------------|
| `image.{source_name}_latest` | Most recent image from source |
| `image.{source_name}_random` | Random image from source |

## API Endpoints Used

- `GET /` - Health check (returns movie quote)
- `GET /stocks` - Stock portfolio data
- `GET /webcams` - Webcam image URLs
- `GET /aviation/lszi` - Aviation weather and runway data
- `GET /image/latest?code={code}` - Latest image for source
- `GET /image/random?code={code}` - Random image for source

## Development

```bash
# Clone the repository
git clone <your-gitlab-url>

# Link to your Home Assistant dev environment
ln -s /path/to/fiftyone-ha-plugin/custom_components/fiftyone /path/to/ha-config/custom_components/fiftyone
```

## License

MIT License
