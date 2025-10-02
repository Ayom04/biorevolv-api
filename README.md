# BioRevolv API - IoT Biogas Monitoring System

A FastAPI-based REST API for monitoring and managing sensors in an IoT-enabled biogas production system. This API collects and processes sensor data from various stages of the biogas production process, enabling real-time monitoring, optimization, and predictive maintenance.

## 🌱 Project Overview

BioRevolv is an integrated biogas production monitoring system that leverages IoT sensors and AI analytics to optimize the conversion of organic waste into clean energy. The system monitors critical parameters throughout the biogas production process to maximize efficiency and ensure stable operation.

### Biogas Production Process

The system monitors the following key stages:

#### 1. Feedstock Collection

- **Sources**: Cassava peels, rice husks, maize stalks, cow dung, poultry manure
- **Monitoring**: Waste storage conditions to prevent contamination
- **Sensors**: Weight, moisture, temperature

#### 2. Pre-treatment

- **Process**: Sorting, shredding, moisture adjustment
- **Purpose**: Reduce particle size for faster microbial digestion
- **Sensors**:
  - Moisture sensors for optimal water content
  - Weight sensors for consistency tracking

#### 3. Feedstock Mixing & Buffering

- **Process**: Blend different wastes for optimal Carbon:Nitrogen (C:N) ratio
- **Combination**:
  - Cow dung (Nitrogen-rich)
  - Cassava peels (Carbon-rich)
  - Poultry manure (balanced)
- **Equipment**: Buffer tank for thorough mixing
- **Sensors**: Feed weight, moisture content

#### 4. Anaerobic Digester

- **Environment**: Sealed modular tank, mesophilic conditions (35–40°C)
- **Process**: Hydrolysis → Acidogenesis → Acetogenesis → Methanogenesis
- **Output**: Biogas (CH₄ + CO₂) and digestate
- **Critical Sensors**:
  - Temperature (maintain microbial activity)
  - pH (prevent acidification)
  - ORP (track redox balance)
  - Gas flow & composition (CH₄/CO₂ ratio)
  - Slurry level

#### 5. Biogas Processing

- **Composition**: 55–65% methane, 35–45% CO₂, traces of H₂S, NH₃, moisture
- **Processing Steps**:
  - Gas conditioning (H₂S removal, dehumidification)
  - Optional CO₂ capture for reuse
  - Energy utilization (cooking gas, electricity generation)

#### 6. Digestate Processing

- **Product**: Nutrient-rich slurry (NPK, organic carbon, micronutrients)
- **Processing Routes**:
  - Liquid biofertilizer (filtered, pasteurized)
  - Pelletized/granular fertilizer (dewatered, dried, pelletized)
- **Sensors**: Solids content, moisture, conductivity

### 🤖 IoT/AI Integration

The system provides:

- **Real-time Monitoring**: Continuous sensor data collection
- **Process Optimization**: AI-driven feeding ratio optimization
- **Predictive Analytics**: Methane yield prediction
- **Fault Detection**: Early warning systems (e.g., pH crash detection)
- **Maintenance Scheduling**: Predictive maintenance alerts

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Data Validation**: Pydantic
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bioreolv-api
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
# Start the FastAPI server
uvicorn main:app --reload
```

The API will be available at:

- **API Base URL**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

## 📚 API Endpoints

### Sensor Management

#### Create a Sensor

```http
POST /api/sensors/
Content-Type: application/json

{
  "name": "Temperature Sensor 1",
  "type": "temperature",
  "location": "Anaerobic Digester"
}
```

#### Get Sensor Details

```http
GET /api/sensors/{sensor_id}
```

### Sensor Data Ingestion

#### Submit Sensor Reading

```http
POST /api/sensors/data
Content-Type: application/json

{
  "sensor_id": 1,
  "value": 37.5,
  "unit": "°C"
}
```

#### Get Sensor Readings

```http
GET /api/sensors/{sensor_id}/readings
```

## 📊 Supported Sensor Types

- **Temperature**: Digester temperature monitoring
- **pH**: Acidity level tracking
- **ORP**: Oxidation-reduction potential
- **Moisture**: Feedstock and digestate moisture content
- **Weight**: Feed quantities and inventory
- **Gas Flow**: Biogas production rate
- **Gas Composition**: Methane/CO₂ ratio
- **Conductivity**: Digestate nutrient content
- **Pressure**: System pressure monitoring
- **Level**: Slurry and gas storage levels

## 🗄️ Database Schema

### Sensors Table

- `id`: Primary key
- `name`: Sensor identifier
- `type`: Sensor type (temperature, pH, etc.)
- `location`: Physical location in the system

### Sensor Readings Table

- `id`: Primary key
- `sensor_id`: Foreign key to sensors table
- `value`: Measured value
- `unit`: Unit of measurement
- `timestamp`: Reading timestamp

## 🔧 Development

### Project Structure

```
bioreolv-api/
├── main.py          # FastAPI application and routes
├── models.py        # SQLAlchemy database models
├── schemas.py       # Pydantic data validation schemas
├── database.py      # Database connection configuration
├── requirements.txt # Python dependencies
├── README.md        # Project documentation
└── sensors.db       # SQLite database (auto-generated)
```

### Adding New Sensor Types

1. Update the sensor model if needed
2. Add validation in schemas
3. Create specific endpoints for specialized sensors
4. Update documentation

## 🚀 Deployment

### Production Considerations

1. **Database**: Switch to PostgreSQL for production
2. **Environment Variables**: Use environment variables for sensitive configuration
3. **Security**: Implement authentication and authorization
4. **Monitoring**: Add logging and health checks
5. **Scaling**: Consider containerization with Docker

### Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost/biogas_db
SECRET_KEY=your-secret-key
DEBUG=False
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs` endpoint

## 🔮 Future Enhancements

- [ ] Real-time dashboard interface
- [ ] Machine learning models for yield prediction
- [ ] Mobile app for remote monitoring
- [ ] Integration with external weather APIs
- [ ] Advanced analytics and reporting
- [ ] Multi-site deployment support
- [ ] Automated alert system
- [ ] Data export capabilities
