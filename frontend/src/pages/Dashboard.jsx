import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { BookOpen, Users, Bell, ClipboardList } from 'lucide-react';

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({ courses: 0, notices: 0, pending: 0 });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                // Simplified dynamic stats fetching based on roles
                const reqs = [];

                if (user.role === 'STUDENT') {
                    reqs.push(api.get('/courses/').then(res => res.data.length));
                    reqs.push(api.get('/notices/').then(res => res.data.length));
                    reqs.push(api.get('/results/').then(res => res.data.filter(r => r.status === 'PUBLISHED').length));
                } else if (user.role === 'FACULTY') {
                    reqs.push(api.get('/courses/').then(res => res.data.length));
                    reqs.push(api.get('/notices/').then(res => res.data.length));
                    reqs.push(api.get('/results/').then(res => res.data.filter(r => r.status === 'DRAFT').length));
                } else {
                    reqs.push(api.get('/courses/').then(res => res.data.length));
                    reqs.push(api.get('/notices/').then(res => res.data.length));
                    reqs.push(api.get('/users/').then(res => res.data.length));
                }

                const [v1, v2, v3] = await Promise.all(reqs);

                if (user.role === 'STUDENT') {
                    setStats({ courses: v1, notices: v2, results: v3 });
                } else if (user.role === 'FACULTY') {
                    setStats({ courses: v1, notices: v2, drafts: v3 });
                } else {
                    setStats({ courses: v1, notices: v2, users: v3 });
                }
            } catch (err) {
                console.error("Failed to fetch dash stats", err);
            }
        };
        fetchStats();
    }, [user]);

    return (
        <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Welcome back, {user?.first_name}!</h1>
            <p className="text-sm font-medium text-gray-500 mb-8 uppercase tracking-wide">
                Role: <span className="text-indigo-600 font-bold">{user?.role}</span>
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500 truncate">Total Courses</p>
                            <p className="mt-1 text-3xl font-semibold text-gray-900">{stats.courses}</p>
                        </div>
                        <div className="p-3 bg-indigo-50 rounded-full">
                            <BookOpen className="h-6 w-6 text-indigo-600" />
                        </div>
                    </div>
                    <p className="mt-4 text-sm text-indigo-600 font-medium hover:text-indigo-500 cursor-pointer">View all courses →</p>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500 truncate">Recent Notices</p>
                            <p className="mt-1 text-3xl font-semibold text-gray-900">{stats.notices}</p>
                        </div>
                        <div className="p-3 bg-indigo-50 rounded-full">
                            <Bell className="h-6 w-6 text-indigo-600" />
                        </div>
                    </div>
                    <p className="mt-4 text-sm text-indigo-600 font-medium hover:text-indigo-500 cursor-pointer">View notice board →</p>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500 truncate">
                                {user?.role === 'STUDENT' ? 'Published Results' : user?.role === 'FACULTY' ? 'Draft Results' : 'System Users'}
                            </p>
                            <p className="mt-1 text-3xl font-semibold text-gray-900">
                                {user?.role === 'STUDENT' ? stats.results : user?.role === 'FACULTY' ? stats.drafts : stats.users}
                            </p>
                        </div>
                        <div className="p-3 bg-indigo-50 rounded-full">
                            {user?.role === 'STUDENT' || user?.role === 'FACULTY' ? <ClipboardList className="h-6 w-6 text-indigo-600" /> : <Users className="h-6 w-6 text-indigo-600" />}
                        </div>
                    </div>
                    <p className="mt-4 text-sm text-indigo-600 font-medium hover:text-indigo-500 cursor-pointer">Manage items →</p>
                </div>
            </div>

            <div className="bg-white px-4 py-5 border-b border-gray-200 sm:px-6 rounded-lg shadow">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Quick Actions
                </h3>
                <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                    {/* Dynamic action buttons based on roles. Placeholders for now. */}
                    <button className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-left hover:bg-gray-100 transition-colors">
                        <span className="block font-medium text-gray-900">Profile Settings</span>
                        <span className="block text-sm text-gray-500 mt-1">Update personal information</span>
                    </button>
                    {user?.role === 'FACULTY' && (
                        <button className="bg-indigo-50 border border-indigo-200 p-4 rounded-lg text-left hover:bg-indigo-100 transition-colors">
                            <span className="block font-medium text-indigo-900">Mark Attendance</span>
                            <span className="block text-sm text-indigo-700 mt-1">Enter daily records</span>
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
