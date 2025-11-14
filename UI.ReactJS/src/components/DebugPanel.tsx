import React, { useState } from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { config } from '@/config/config.ts';

export const DebugPanel: React.FC = () => {
  const [useFixtures, setUseFixtures] = useState(() => {
    // Check if any feature flag is enabled for fixtures
    return config.USER_MANAGEMENT_USE_FIXTURE || 
           config.TEMPLATE_MANAGEMENT_USE_FIXTURE || 
           config.REPORTS_MANAGEMENT_USE_FIXTURE || 
           config.FILES_MANAGEMENT_USE_FIXTURE;
  });

  if (!config.ENABLE_DEBUG_PANEL) {
    return null;
  }

  const toggleFixtureMode = () => {
    // Note: This is for display only since config is const
    // In a real implementation, you'd want to update environment variables
    setUseFixtures(!useFixtures);
    console.log('Debug: Toggle fixture mode (reload app to see changes)');
  };

  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-50">
      <div className="text-sm font-medium mb-2">Debug Panel</div>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs">Data Source:</span>
          <span className={`text-xs px-2 py-1 rounded ${
            useFixtures 
              ? 'bg-orange-500 text-white' 
              : 'bg-green-500 text-white'
          }`}>
            {useFixtures ? 'Mock Data' : 'Real API'}
          </span>
        </div>
        <Button
          onClick={toggleFixtureMode}
          size="sm"
          variant="outline"
          className="w-full text-white border-white hover:bg-white hover:text-gray-800"
        >
          Switch to {useFixtures ? 'API' : 'Mock'}
        </Button>
      </div>
    </div>
  );
};
