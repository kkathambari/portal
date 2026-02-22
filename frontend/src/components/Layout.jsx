import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
    Home, BookOpen, Users, ClipboardList, CheckSquare,
    Bell, Settings, LogOut, Menu, X, User as UserIcon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const getNavigationBoxes = (role) => {
    const common = [
        { name: 'Dashboard', href: '/', icon: Home },
        { name: 'Notices', href: '/notices', icon: Bell },
    ];

    switch (role) {
        case 'STUDENT':
            return [
                ...common,
                { name: 'My Courses', href: '/courses', icon: BookOpen },
                { name: 'My Attendance', href: '/attendance', icon: CheckSquare },
                { name: 'My Results', href: '/results', icon: ClipboardList },
            ];
        case 'FACULTY':
            return [
                ...common,
                { name: 'Assigned Courses', href: '/courses', icon: BookOpen },
                { name: 'Mark Attendance', href: '/attendance', icon: CheckSquare },
                { name: 'Assessments', href: '/assessments', icon: ClipboardList },
            ];
        case 'ADMIN':
        case 'HOD':
        case 'EXAM_CELL':
            return [
                ...common,
                { name: 'All Courses', href: '/courses', icon: BookOpen },
                { name: 'Manage Users', href: '/users', icon: Users },
            ]
        default:
            return common;
    }
};

const Layout = () => {
    const { user, logout } = useAuth();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const location = useLocation();

    const navigation = getNavigationBoxes(user?.role);

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar for desktop */}
            <div className="hidden md:flex flex-col w-64 bg-indigo-900 border-r border-indigo-800 text-white">
                <div className="flex items-center justify-center h-16 border-b border-indigo-800">
                    <span className="text-xl font-bold tracking-wider">AcaPortal</span>
                </div>

                <div className="flex-1 overflow-y-auto py-4">
                    <nav className="space-y-1 px-2">
                        {navigation.map((item) => {
                            const isActive = location.pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    className={`group flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors ${isActive ? 'bg-indigo-800 text-white' : 'text-indigo-100 hover:bg-indigo-700 hover:text-white'
                                        }`}
                                >
                                    <item.icon className={`mr-3 flex-shrink-0 h-5 w-5 ${isActive ? 'text-white' : 'text-indigo-300 group-hover:text-white'}`} aria-hidden="true" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="p-4 border-t border-indigo-800">
                    <div className="flex items-center group">
                        <div className="ml-3">
                            <p className="text-sm font-medium text-white group-hover:text-indigo-200">
                                {user?.first_name} {user?.last_name}
                            </p>
                            <p className="text-xs font-medium text-indigo-300 group-hover:text-white">
                                View profile
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="mt-4 w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none"
                    >
                        <LogOut className="mr-2 h-4 w-4" />
                        Sign Out
                    </button>
                </div>
            </div>

            {/* Main Content wrapper */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Mobile top bar */}
                <div className="md:hidden flex items-center justify-between bg-indigo-900 h-16 px-4">
                    <span className="text-xl font-bold tracking-wider text-white">AcaPortal</span>
                    <button
                        type="button"
                        className="text-indigo-200 hover:text-white rounded-md p-2 focus:outline-none"
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    >
                        {isMobileMenuOpen ? (
                            <X className="h-6 w-6" aria-hidden="true" />
                        ) : (
                            <Menu className="h-6 w-6" aria-hidden="true" />
                        )}
                    </button>
                </div>

                {/* Mobile Menu Dropdown */}
                <AnimatePresence>
                    {isMobileMenuOpen && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="md:hidden bg-indigo-800 px-2 pt-2 pb-3 space-y-1 sm:px-3 shadow-lg z-50 absolute w-full top-16"
                        >
                            {navigation.map((item) => {
                                const isActive = location.pathname === item.href;
                                return (
                                    <Link
                                        key={item.name}
                                        to={item.href}
                                        onClick={() => setIsMobileMenuOpen(false)}
                                        className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${isActive ? 'bg-indigo-900 text-white' : 'text-indigo-100 hover:bg-indigo-700 hover:text-white'
                                            }`}
                                    >
                                        <div className="flex items-center">
                                            <item.icon className="mr-3 h-5 w-5" aria-hidden="true" />
                                            {item.name}
                                        </div>
                                    </Link>
                                );
                            })}
                            <button
                                onClick={() => { setIsMobileMenuOpen(false); logout(); }}
                                className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-indigo-100 hover:bg-indigo-700 hover:text-white mt-4 items-center flex"
                            >
                                <LogOut className="mr-3 h-5 w-5" /> Sign Out
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Main page content area */}
                <main className="flex-1 relative overflow-y-auto focus:outline-none bg-gray-50 p-4 md:p-8">
                    <div className="max-w-7xl mx-auto">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Layout;
