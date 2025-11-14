import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { LoginPage } from '@/pages/LoginPage.tsx';
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage.tsx';
import NotFoundPage from '@/pages/NotFoundPage';
import ForbiddenPage from '@/pages/ForbiddenPage';
import { AdminLayout } from '@/pages/admin/AdminLayout/AdminLayout.tsx';
import { routes } from '@/routes.ts';
import { ProtectedRoute } from '@/pages/admin/AdminLayout/ProtectedRoute.tsx';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/forbidden" element={<ForbiddenPage />} />

          {/* Admin Routes */}
          <Route
            path="/*"
            element={
              <ProtectedRoute requiredRole="User">
                <AdminLayout />
              </ProtectedRoute>
            }
          >
            {/* Nested routes will be rendered inside AdminLayout's Outlet */}
            <Route index element={<Navigate to="reports" replace />} />
            {routes.map((route) => (
              <Route
                key={route.path}
                path={route.path.startsWith('/') ? route.path.substring(1) : route.path}
                element={<route.component />}
              />
            ))}
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
