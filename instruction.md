# MASTER PROMPT — FLOWSIGHT AI

Build a complete, intermediate-level, portfolio-quality BTech CSE project named **FlowSight AI – Intelligent Traffic Monitoring and Analytics System**.

## 1. Project objective
Develop an AI-powered web application that analyses traffic videos, detects and tracks vehicles, counts traffic, estimates density, and identifies congestion.

## 2. Technology stack
- Frontend: React.js with Vite and Tailwind CSS.
- Backend: Python FastAPI.
- AI: Ultralytics YOLO pretrained model.
- Computer vision: OpenCV.
- Vehicle tracking: ByteTrack where supported.
- Data processing: NumPy and Pandas.
- Charts: Recharts.
- Database: SQLite.
- API communication: REST API.

## 3. Required features
1. Upload traffic videos.
2. Detect cars, motorcycles, buses, and trucks.
3. Draw bounding boxes and class labels.
4. Track individual vehicles across video frames.
5. Count vehicles without repeatedly counting the same tracked vehicle.
6. Calculate traffic density.
7. Classify traffic as Low, Medium, or High.
8. Display congestion information.
9. Show vehicle counts by category.
10. Display traffic analytics using charts.
11. Provide a video monitoring interface.
12. Store traffic analysis history in SQLite.
13. Provide a clean and responsive dashboard.

## 4. Dashboard design
Create a modern professional dashboard with:
- FlowSight AI branding.
- Sidebar navigation.
- Overview page.
- Video upload section.
- Traffic monitoring page.
- Analytics page.
- History page.
- Vehicle count cards.
- Traffic density indicator.
- Congestion status.
- Bar and line charts.

Use a professional dark-blue and white theme.

## 5. Backend requirements
- Create FastAPI application.
- Create API routes for video upload and analysis.
- Implement YOLO vehicle detection.
- Implement vehicle tracking and counting.
- Calculate traffic density and congestion.
- Save analysis results in SQLite.
- Provide API endpoints for dashboard statistics.
- Include error handling and input validation.

## 6. Project structure
Automatically create all necessary folders and files, including:
- backend
- frontend
- models
- traffic_videos
- database
- documentation

Do not ask me to create folders manually.

## 7. Important development instructions
- Reuse the existing Python 3.12 virtual environment named venv.
- Reuse already installed Python libraries where possible.
- Do not unnecessarily reinstall dependencies.
- Create requirements.txt.
- Create .gitignore.
- Create a complete README.md.
- Never put passwords, API keys, or secrets in source code.
- Do not use fake traffic analytics in the real dashboard.
- If no video is uploaded, show a helpful empty state.
- Make the application functional, not just a static UI.
- Include clear instructions for running the backend and frontend separately.
- Use a sample video only if a properly licensed sample is available; otherwise provide instructions for uploading a user's own video.

## 8. Testing
- Test backend imports and startup.
- Test API endpoints.
- Check frontend build.
- Check backend/frontend API integration.
- Fix errors before declaring completion.

## 9. Final instructions
Build the project step by step, create the actual source files, and explain what has been implemented.

Do not stop after generating a plan or displaying sample code. Implement the complete working project inside the currently opened FlowSight-AI folder.

Start by inspecting the existing folder and virtual environment.