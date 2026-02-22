import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { AlertTriangle } from 'lucide-react';

const Unauthorized = () => {
    const { user } = useAuth();
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md bg-white p-8 border border-gray-200 shadow rounded-lg text-center">
                <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
                <p className="text-sm text-gray-600 mb-6">
                    You do not have the required permissions to view this page.
                </p>
                <p className="text-xs text-gray-400 mb-4">
                    Logged in as {user?.role}
                </p>
                <a href="/" className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
                    Return to Dashboard
                </a>
            </div>
        </div>
    );
};

export default Unauthorized;
