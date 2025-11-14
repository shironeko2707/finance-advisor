import React from 'react';
import defaultLogo from "@/assets/logo.png";
import cmcLogo from "@/assets/cmc.svg";

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (menu: string) => void;
  userRole?: string;
}

// Helper function to get logo URL
const getLogoUrl = (): string => {
  const logoUrl = import.meta.env.VITE_APP_LOGO_URL;
  if (logoUrl) {
    // Check for specific known assets
    if (logoUrl === './assets/cmc.svg' || logoUrl === 'assets/cmc.svg') {
      return cmcLogo;
    }
    // If it's a full URL, return as is
    if (logoUrl.startsWith('http')) {
      return logoUrl;
    }
  }
  return defaultLogo;
};

// Helper function to get environment name
const getEnvironmentName = (): string => {
  const env = import.meta.env.VITE_MODE || 'local';
  return env.toUpperCase();
};

export const Sidebar: React.FC<SidebarProps> = ({ activeMenu, onMenuChange, userRole }) => {
  const menuItems = [
    {
      id: 'analyst',
      title: 'Analyst Tools',
      items: [
        { id: 'reports', label: 'Reports', icon: '📊' },
        { id: 'templates', label: 'Templates', icon: '📋' },
        { id: 'files', label: 'Uploaded Files', icon: '📁' }
      ]
    },
    // Only show Admin Panel if user role is not 'User'
    ...(userRole !== 'User' ? [{
      id: 'admin',
      title: 'Admin Panel',
      items: [
        { id: 'users', label: 'Users', icon: '👥' }
      ]
    }] : [])
  ];

  const handleNavigation = (item: { id: string; label: string; icon: string }) => {
    onMenuChange(item.id);
  };

  return (
    <div className="w-[20%] min-w-[250px] text-white">
      {/* Logo with Environment Ribbon */}
      <div className="relative mb-5 overflow-visible">
        <img src={getLogoUrl()} alt="logo" className='w-full' />

        {/* Environment Ribbon */}
        <div className="absolute top-3 -right-3 transform rotate-12 z-10">
          <div className="relative">
            <div className="bg-red-600 text-white text-xs font-bold px-4 py-1.5 shadow-lg relative">
              <span className="relative z-10 tracking-wide">{getEnvironmentName()}</span>
              {/* Ribbon left tail */}
              <div className="absolute -left-2 top-0 border-l-[8px] border-l-transparent border-t-[15px] border-t-red-800 border-b-[15px] border-b-red-800"></div>
              {/* Ribbon right tail */}
              <div className="absolute -right-2 top-0 border-r-[8px] border-r-transparent border-t-[15px] border-t-red-800 border-b-[15px] border-b-red-800"></div>
            </div>
            {/* Shadow effect */}
            <div className="absolute top-1 left-1 bg-red-900 text-transparent text-xs font-bold px-4 py-1.5 -z-10">
              <span className="tracking-wide">{getEnvironmentName()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <div className="p-4 bg-gray-500">
        {menuItems.map((section) => (
          <div key={section.id} className="mb-6">
            <h3 className="text-sm font-medium text-gray-300 mb-3">{section.title}</h3>
            <ul className="space-y-2">
              {section.items.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => handleNavigation(item)}
                    className={`w-full flex items-center px-3 py-2 text-sm rounded-md transition-colors ${activeMenu === item.id
                        ? 'bg-gray-600 text-white'
                        : 'text-gray-300 hover:bg-gray-600 hover:text-white'
                      }`}
                  >
                    <span className="mr-3">{item.icon}</span>
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};
