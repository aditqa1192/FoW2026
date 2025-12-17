# React Frontend Setup Instructions

This document provides step-by-step instructions to set up and run the React frontend.

## Installation Steps

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Create production build
- `npm run preview` - Preview production build

## Dependencies

The frontend uses the following key packages:
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Axios** - HTTP client for API requests
- **React Markdown** - Render markdown content

## Configuration

### API Proxy

The Vite configuration includes a proxy to forward API requests from `/api/*` to `http://localhost:5000`. This is configured in `vite.config.js`.

### Environment Variables

You can create a `.env` file in the frontend directory to customize settings:
```
VITE_API_URL=http://localhost:5000
```

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, Vite will automatically try the next available port. You'll see the actual port in the terminal output.

### Backend Connection Issues

Make sure the Flask backend is running on `http://localhost:5000` before starting the frontend.

### Module Not Found Errors

If you encounter module not found errors, try:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Production Build

To create a production build:

```bash
npm run build
```

The optimized files will be in the `dist` directory. You can preview the production build:

```bash
npm run preview
```

## Deployment

For deployment, you can use services like:
- **Vercel** - `npm run build` and deploy the `dist` folder
- **Netlify** - `npm run build` and deploy the `dist` folder
- **GitHub Pages** - Use `gh-pages` package
- **Any static hosting** - Upload the contents of `dist` folder

Remember to update the API endpoint in production to point to your backend server.
