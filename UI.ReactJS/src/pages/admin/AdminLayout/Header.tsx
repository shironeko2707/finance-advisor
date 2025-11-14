import React from 'react';
import { useAuth } from '@/contexts/AuthContext.tsx';
import downIcon from "@/assets/down-arrow.png";
import logoutIcon from "@/assets/logout-icon.png";
import { DropdownMenu } from "@/components/atomic/dropdown-menu";

export const Header: React.FC = () => {
  const { user, logout } = useAuth();

  const dropdownItems = [
    {
      label: 'Log out',
      onClick: logout,
      icon: <img src={logoutIcon} alt="logoutIcon" className='w-4' />,
      className: 'text-sm font-[700] text-[#5C5C5C] hover:bg-[#F5F5F5]'
    }
  ];

  const customTrigger = (
    <div className='flex gap-2 items-center cursor-pointer p-2'>
      <span className="font-[500] text-base text-[#5D5D5D]">
        {user?.name || ''}
      </span>
      <img src={downIcon} alt="downIcon" className='w-4 h-4' />
    </div>
  );

  return (
    <header className="bg-[#E9E9E4] flex justify-end mb-4">
      <DropdownMenu
        items={dropdownItems}
        trigger={customTrigger}
        triggerClassName="hover:bg-transparent"
        align="center"
      />
    </header>
  );
};
