import React, { useState } from 'react';
import { Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar.tsx';
import { Header } from './Header.tsx';
import { useAuth } from '@/contexts/AuthContext.tsx';
import { menuRouteMap } from '@/routes.ts';

const AdminContent: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  // Determine active menu based on current path
  const getActiveMenuFromPath = (pathname: string): string => {
    if (pathname.startsWith('/templates')) return 'templates';
    if (pathname.startsWith('/users')) return 'users';
    if (pathname.startsWith('/reports')) return 'reports';
    if (pathname.startsWith('/files')) return 'files';
    if (pathname.startsWith('/dashboard')) return 'dashboard';
    return 'dashboard'; // default to dashboard
  };

  const [activeMenu, setActiveMenu] = useState<string>(getActiveMenuFromPath(location.pathname));

  React.useEffect(() => {
    setActiveMenu(getActiveMenuFromPath(location.pathname));
  }, [location.pathname]);

  // If user is not logged in, redirect to login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleMenuChange = (menu: string) => {
    setActiveMenu(menu);

    // Navigate to appropriate route using menuRouteMap
    const targetRoute = menuRouteMap[menu];
    if (targetRoute) {
      navigate(targetRoute);
    }
  };

  return (
    <div className="bg-[#E9E9E4] px-[60px] py-[18px]">
      <div className="flex gap-8 h-[calc(100vh-36px)] max-w-[1440px] mx-auto">
        <Sidebar
          activeMenu={activeMenu}
          onMenuChange={handleMenuChange}
          userRole={user?.role}
        />
        <div className='w-full'>
          <Header />
          <main className="bg-white h-[calc(100vh-100px)] overflow-y-auto custom-scrollbar">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export const AdminLayout: React.FC = () => {
  return (
    <AdminContent />
  );
};
