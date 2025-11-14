import React from 'react';
import { User, Shield, Clock, Activity, BarChart3, Settings, HelpCircle } from 'lucide-react';
import { Button } from '@/components/atomic/button.tsx';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/atomic/card.tsx';
import { useAuth } from '@/contexts/AuthContext.tsx';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="p-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Admin Dashboard</h1>
        <p className="text-gray-600">Manage your application from this central hub.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="border-0 shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-2 text-lg">
              <User className="w-5 h-5 text-blue-600" />
              <span>Profile Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Name</span>
                <span className="font-semibold">{user?.name || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Email</span>
                <span className="font-semibold">{user?.email || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">User ID</span>
                <span className="font-semibold">{user?.id || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Status</span>
                <span className="text-green-600 font-semibold flex items-center space-x-1">
                  <Activity className="w-3 h-3" />
                  <span>Active</span>
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-2 text-lg">
              <BarChart3 className="w-5 h-5 text-green-600" />
              <span>System Statistics</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Users</span>
                <span className="font-semibold">24</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Sessions</span>
                <span className="font-semibold">8</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Templates</span>
                <span className="font-semibold">12</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Storage Used</span>
                <span className="font-semibold">2.4 GB</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-2 text-lg">
              <Clock className="w-5 h-5 text-orange-600" />
              <span>Recent Activity</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="text-sm">
                <div className="font-medium">User login</div>
                <div className="text-gray-500">2 minutes ago</div>
              </div>
              <div className="text-sm">
                <div className="font-medium">Template created</div>
                <div className="text-gray-500">1 hour ago</div>
              </div>
              <div className="text-sm">
                <div className="font-medium">User updated</div>
                <div className="text-gray-500">3 hours ago</div>
              </div>
              <div className="text-sm">
                <div className="font-medium">System backup</div>
                <div className="text-gray-500">1 day ago</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-2 text-lg">
              <Shield className="w-5 h-5 text-red-600" />
              <span>Security Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Security Level</span>
                <span className="text-green-600 font-semibold">High</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Last Scan</span>
                <span className="text-gray-900 font-semibold">Today</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Threats Detected</span>
                <span className="text-gray-900 font-semibold">0</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-2 text-lg">
              <Settings className="w-5 h-5 text-purple-600" />
              <span>Quick Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button className="w-full justify-start" variant="outline">
                <User className="w-4 h-4 mr-2" />
                View All Users
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Settings className="w-4 h-4 mr-2" />
                System Settings
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <BarChart3 className="w-4 h-4 mr-2" />
                View Reports
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <HelpCircle className="w-4 h-4 mr-2" />
                Help Center
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
