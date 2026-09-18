import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';

export const AppShell: React.FC = () => {
  return (
    <div className="min-h-screen bg-soc-bg flex flex-col font-sans">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-8 overflow-y-auto max-w-7xl">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

