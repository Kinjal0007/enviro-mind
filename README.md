# EnviroMind

EnviroMind is a personalized environmental health alert application that leverages Copernicus, Galileo, and IRIS² data to provide users with actionable health insights based on their environment.

## Features

- Personalized environmental health alerts
- Real-time air quality monitoring
- Heat stress warnings
- Mental well-being insights
- Location-based recommendations

## Tech Stack

- React Native with TypeScript
- Expo
- FastAPI (Backend)
- PostgreSQL with PostGIS
- Copernicus APIs
- Galileo HAS

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Expo CLI
- Python 3.8+ (for backend)
- PostgreSQL with PostGIS extension

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/enviromind.git
cd enviromind
```

2. Install frontend dependencies:

```bash
cd mobile
npm install
```

3. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Start the development server:

```bash
# Frontend
cd mobile
npm start

# Backend
cd backend
uvicorn main:app --reload
```

## Project Structure

```
enviromind/
├── mobile/                 # React Native frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── screens/       # App screens
│   │   ├── services/      # API services
│   │   ├── utils/         # Utility functions
│   │   └── types/         # TypeScript type definitions
│   └── App.tsx           # Main app component
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   └── services/     # Business logic
│   └── main.py           # Backend entry point
└── README.md             # Project documentation
```

## Development Roadmap

1. MVP Phase

   - Basic user authentication
   - Location-based environmental data fetching
   - Simple alert system
   - Basic UI implementation

2. Enhancement Phase

   - Advanced personalization
   - Machine learning integration
   - Wearable device integration
   - Enhanced UI/UX

3. Production Phase
   - Security hardening
   - Performance optimization
   - Scale infrastructure
   - Production deployment

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
