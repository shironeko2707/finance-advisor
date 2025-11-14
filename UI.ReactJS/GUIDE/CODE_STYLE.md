

## Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # Shadcn UI components
│   ├── LoginPage.tsx   # Login form component
│   ├── Dashboard.tsx   # Dashboard component
│   └── ProtectedRoute.tsx # Route protection wrapper
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── lib/               # Utility functions
│   └── utils.ts       # Shadcn utils
├── App.tsx            # Main app component
└── main.tsx           # App entry point
```

## Authentication Flow

1. User visits the application
2. If not authenticated, redirected to `/login`
3. User enters credentials and submits form
4. On successful login, user is redirected to `/dashboard`
5. Protected routes check authentication status
6. User can logout from the dashboard

## Customization

### Adding New Components

Use Shadcn CLI to add new components:
```bash
npx shadcn@latest add [component-name]
```

### Styling

The app uses Tailwind CSS for styling. You can customize the theme in `tailwind.config.js`.

### Authentication

Currently uses mock authentication. To integrate with a real backend:
1. Update the `login` function in `AuthContext.tsx`
2. Replace localStorage with secure token storage
3. Add API integration for user management

## License

This project is licensed under the MIT License.
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```