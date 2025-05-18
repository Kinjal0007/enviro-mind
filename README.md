# EnviroMind: Your Personal Environmental Wellness Guide

EnviroMind is a mobile application designed to provide users with real-time environmental insights and help them manage their health goals. It integrates data from various sources to offer a comprehensive overview of air quality, UV exposure, and sunlight patterns, tailored to the user's location.

## 🌎 What It Does

- ✅ **Real-time Environmental Insights:** Provides up-to-date Air Quality Index (AQI) with detailed pollutant breakdowns (PM2.5, PM10, O3, NO2, SO2, CO), UV Index with actionable advice, and daily sunlight patterns (sunrise, sunset, daylight hours) based on your location.
- ✅ **Personalized Actionable Suggestions:** (Coming Soon) Will offer tailored recommendations for safe activities and wellness tips based on current environmental conditions and your health profile.
- ✅ **Goal Tracking for Healthy Habits:** Integrates with your health goals for sleep, walking, and calorie intake, helping you maintain a balanced lifestyle.
- ✅ **Resilience Score & Streak Tracking:** (Future Feature) Designed to help you build smart, healthy habits in response to environmental factors.
- ✅ **User-Friendly Interface:** Features a clean, intuitive UI for easy access to vital information, aiming to inform without causing alert fatigue.
- ✅ **Interactive Location Settings:** Allows you to use your live location or manually set a location via map or address search for personalized data.

## 💡 Why It's Unique

- **Comprehensive Environmental Overview:** Combines various environmental factors (air quality, UV, sunlight) into one dashboard.
- **Focus on Action and Wellness:** Aims to not just present data, but to integrate with health goals and (in the future) provide guidance to help users act on the information.
- **User-Controlled Location:** Provides flexibility in how location data is sourced, enhancing user privacy and control.
- **(Future) Tailored to Your Health Profile:** Will offer more personalized insights by considering individual health sensitivities.

## 🔧 Tech Stack

- **Data Sources:** Copernicus Climate Data Store (CDS) for atmospheric data (via backend).
- **Frontend:** Flutter with Dart for cross-platform mobile app development.
- **Backend:** FastAPI (Python) with MongoDB.
- **Key Frontend Libraries & Tools:**
  - `provider` for state management.
  - `http` for network requests.
  - `google_maps_flutter` for interactive map features.
  - `geolocator` & `geocoding` for location services.
  - `flutter_secure_storage` for secure token storage.
  - `intl`, `google_fonts`.
- **Development Tools:** VS Code, Android Studio (recommended for full Android build capabilities), Git & GitHub.

## 🚀 Getting Started

### Prerequisites

- Flutter SDK (latest stable version recommended)
- Dart SDK (comes with Flutter)
- For Android: Android Studio with Android SDK and emulator/device set up.
- For iOS: Xcode with iOS simulator/device set up, CocoaPods.
- Python 3.8+ (for backend)
- MongoDB instance (local or cloud).
- Copernicus CDS API key (set up in `.cdsapirc` and backend `.env`).

### Installation & Setup

1.  **Clone the Repository:**

    ```bash
    git clone <your-repository-url>
    cd Enviro%20Mind
    ```

2.  **Backend Setup:**

    - Navigate to the `backend` directory.
    - Create a Python virtual environment: `python -m venv venv`
    - Activate it: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows).
    - Install dependencies: `pip install -r requirements.txt`.
    - Set up your `.env` file with `MONGO_DETAILS`, `CDS_API_URL`, `CDS_API_KEY`, and `SECRET_KEY`.
    - Ensure your `.cdsapirc` file is configured in your home directory or accessible by the backend for Copernicus data.
    - Run the backend: `uvicorn app.main:app --reload --port 8000` (or your configured port).

3.  **Frontend Setup:**
    - Navigate to the `frontend` directory.
    - Get Flutter packages: `flutter pub get`.
    - **API Keys for Google Maps:**
      - **Android:** Add your Google Maps API key to `frontend/android/app/src/main/AndroidManifest.xml`.
      - **iOS:** Add your API key to `frontend/ios/Runner/AppDelegate.swift`.
      - (Refer to the `google_maps_flutter` package documentation for detailed instructions).
    - Ensure the `apiUrl` in `frontend/lib/main.dart` points to your running backend (e.g., `http://10.0.2.2:8000/api/v1` for Android emulator, `http://127.0.0.1:8000/api/v1` for iOS simulator).
    - Run the app: `flutter run`.

## 🏗️ Project Structure (Simplified)

```
EnviroMind/
├── backend/              # FastAPI backend server
│   ├── app/
│   │   ├── api/          # API endpoint routers
│   │   ├── core/         # Configuration, security
│   │   ├── crud/         # Database interaction logic
│   │   ├── models/       # Pydantic models
│   │   ├── schemas/      # Database schemas (if separate)
│   │   └── services/     # Business logic, external API interaction (e.g., Copernicus)
│   ├── requirements.txt
│   └── main.py           # Backend entry point
├── frontend/             # Flutter mobile application
│   ├── lib/
│   │   ├── main.dart     # Main app entry point & routing
│   │   ├── models/       # Dart data models
│   │   ├── providers/    # State management (e.g., LocationProvider, ThemeProvider)
│   │   ├── screens/      # UI screens for different app sections
│   │   ├── services/     # API communication (AuthService, EnvironmentService)
│   │   └── widgets/      # Reusable UI components
│   ├── pubspec.yaml      # Flutter dependencies
│   ├── assets/           # Static assets (images, .env)
│   └── ...               # Platform-specific folders (android/, ios/)
└── README.md             # This file
```

## 🔮 Future Enhancements

- Full implementation of personalized actionable suggestions based on health profiles.
- Development of the Resilience Score and streak tracking features.
- Integration of more environmental data points (e.g., pollen, water quality if APIs available).
- Enhanced UI/UX refinements and animations.
- Notifications for critical alerts.

## 🤝 Contributing

(If you plan to accept contributions, add guidelines here or link to a CONTRIBUTING.md file.)

## 📜 License

(Specify your project's license, e.g., MIT License. If you don't have one, consider adding one.)

---

Built by EnviroMind

