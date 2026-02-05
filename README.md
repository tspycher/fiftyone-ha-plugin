# FiftyOne Home Assistant Integration

Custom Home Assistant integration for the FiftyOne API.

## Features

- **Stock Information**: Display stock prices and share data as sensors
- **Weather Data**: Weather information from custom sensor
- **Webcams**: Still images from various webcams as camera entities
- **Family Pictures**: Display family pictures as a camera entity (slideshow)

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

The integration is configured through the Home Assistant UI. You will need to provide:

- **API URL**: The URL of your FiftyOne API (default: `https://api.fiftyone.dev`)

## Entities

### Sensors

- **Weather Temperature**: Current temperature from the weather sensor
- **Stock [ID]**: Stock price/value for each configured stock

### Cameras

- **Webcam [Name]**: Still images from each configured webcam
- **Family Pictures**: Rotating slideshow of family pictures

## API Requirements

The FiftyOne API should provide the following endpoints:

- `GET /health` - Health check endpoint
- `GET /stocks` - Stock information
- `GET /weather` - Weather data
- `GET /webcams` - List of webcams
- `GET /webcams/{id}/image` - Webcam image
- `GET /pictures` - List of family pictures
- `GET /pictures/{id}` - Picture image

## Development

```bash
# Clone the repository
git clone <your-gitlab-url>

# Link to your Home Assistant dev environment
ln -s /path/to/fiftyone-ha-plugin/custom_components/fiftyone /path/to/ha-config/custom_components/fiftyone
```

## License

MIT License
