# BYN Frontend

A modern React TypeScript frontend for the BYN (Build Your Network) application.

## Features

- 🔐 **Authentication**: Login and registration with JWT tokens
- 📱 **Responsive Design**: Mobile-first design with Tailwind CSS
- 🎨 **Modern UI**: BYN-inspired interface with custom components
- ⚡ **Fast**: Built with React 18 and TypeScript for optimal performance
- 🔄 **Real-time**: Auto-refreshing authentication and data
- 🛡️ **Type Safe**: Full TypeScript implementation

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **React Hook Form** - Form handling
- **Axios** - API communication
- **React Hot Toast** - Notifications
- **Heroicons** - Icons
- **Date-fns** - Date formatting

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Django backend running on http://127.0.0.1:8000

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Demo Credentials

- **Email**: john.doe@example.com
- **Password**: testpass123

Alternative accounts:
- jane.smith@example.com / testpass123
- mike.wilson@example.com / testpass123

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── LoadingSpinner.tsx
│   ├── Navbar.tsx
│   └── ProtectedRoute.tsx
├── contexts/           # React contexts
│   └── AuthContext.tsx
├── pages/              # Page components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── DashboardPage.tsx
│   └── ...
├── types/              # TypeScript type definitions
│   └── index.ts
├── utils/              # Utility functions
│   └── api.ts
├── App.tsx             # Main app component
├── index.tsx           # Entry point
└── index.css           # Global styles
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## API Integration

The frontend communicates with the Django backend through a comprehensive API layer:

- **Authentication**: JWT-based login/logout/registration
- **Jobs**: Browse, search, apply for jobs
- **Profiles**: View and update user profiles
- **Companies**: Explore company profiles
- **Applications**: Track job applications

## Styling

This project uses Tailwind CSS with custom BYN-inspired colors and components:

- **Primary**: LinkedIn blue (#0a66c2)
- **Gray**: Warm gray palette for text and backgrounds
- **Responsive**: Mobile-first breakpoints
- **Dark Mode**: Ready for future implementation

## Development Notes

- The app includes proxy configuration to communicate with Django backend
- All API calls include automatic token refresh
- Form validation uses React Hook Form
- Toast notifications for user feedback
- Protected routes for authenticated content

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - see LICENSE file for details. 