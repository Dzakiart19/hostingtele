'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import ProjectCard from '@/components/ProjectCard';
import CreateProjectModal from '@/components/CreateProjectModal';
import { projectsAPI } from '@/lib/api';
import { Project } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    // Cek apakah user sudah login
    const token = Cookies.get('access_token');
    if (!token) {
      router.push('/');
      return;
    }

    loadProjects();
  }, [router]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await projectsAPI.getProjects();
      setProjects(response.projects);
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Cookies.remove('access_token');
    router.push('/');
  };

  const handleCreateSuccess = () => {
    loadProjects();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">ZipHostBot</h1>
              <span className="ml-3 px-3 py-1 bg-telegram-blue text-white text-sm rounded-full">
                Dashboard
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Bot Anda</h2>
            <p className="text-gray-600 mt-1">
              Kelola dan monitor bot Telegram yang sudah di-deploy
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary"
          >
            Deploy Bot Baru dari .zip
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-telegram-blue"></div>
            <p className="mt-2 text-gray-600">Memuat proyek...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg shadow-md p-8 max-w-md mx-auto">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Belum Ada Bot
              </h3>
              <p className="text-gray-600 mb-6">
                Mulai dengan men-deploy bot Telegram pertama Anda dari file .zip
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary"
              >
                Deploy Bot Pertama
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onUpdate={loadProjects}
              />
            ))}
          </div>
        )}

        {/* Refresh Button */}
        <div className="flex justify-center mt-8">
          <button
            onClick={loadProjects}
            disabled={loading}
            className="btn-secondary"
          >
            {loading ? 'Memuat...' : 'Refresh Status'}
          </button>
        </div>
      </main>

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleCreateSuccess}
      />
    </div>
  );
}