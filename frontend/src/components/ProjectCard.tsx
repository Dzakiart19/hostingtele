'use client';

import { useState } from 'react';
import { Project } from '@/types';
import { projectsAPI } from '@/lib/api';

interface ProjectCardProps {
  project: Project;
  onUpdate: () => void;
}

export default function ProjectCard({ project, onUpdate }: ProjectCardProps) {
  const [loading, setLoading] = useState(false);

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'PENDING':
        return 'status-badge status-pending';
      case 'PROCESSING':
        return 'status-badge status-processing';
      case 'RUNNING':
        return 'status-badge status-running';
      case 'STOPPED':
        return 'status-badge status-stopped';
      case 'FAILED':
        return 'status-badge status-failed';
      default:
        return 'status-badge status-pending';
    }
  };

  const handleAction = async (action: 'start' | 'stop' | 'delete') => {
    if (loading) return;
    
    setLoading(true);
    try {
      switch (action) {
        case 'start':
          await projectsAPI.startProject(project.id);
          break;
        case 'stop':
          await projectsAPI.stopProject(project.id);
          break;
        case 'delete':
          if (confirm('Apakah Anda yakin ingin menghapus proyek ini?')) {
            await projectsAPI.deleteProject(project.id);
          }
          break;
      }
      onUpdate();
    } catch (error) {
      console.error(`Error ${action} project:`, error);
      alert(`Gagal ${action} proyek. Silakan coba lagi.`);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('id-ID');
  };

  return (
    <div className="card">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
        <span className={getStatusClass(project.status)}>
          {project.status}
        </span>
      </div>

      <div className="space-y-2 text-sm text-gray-600 mb-4">
        <p>Dibuat: {formatDate(project.created_at)}</p>
        <p>Diperbarui: {formatDate(project.updated_at)}</p>
        {project.container_id && (
          <p className="font-mono text-xs">Container: {project.container_id.substring(0, 12)}</p>
        )}
      </div>

      {project.last_error_log && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
          <p className="text-sm text-red-700 font-medium">Error Log:</p>
          <p className="text-xs text-red-600 mt-1 font-mono break-all">
            {project.last_error_log}
          </p>
        </div>
      )}

      <div className="flex gap-2">
        {project.status === 'RUNNING' && (
          <button
            onClick={() => handleAction('stop')}
            disabled={loading}
            className="btn-secondary text-sm"
          >
            {loading ? 'Loading...' : 'Stop'}
          </button>
        )}
        
        {(project.status === 'STOPPED' || project.status === 'FAILED') && (
          <button
            onClick={() => handleAction('start')}
            disabled={loading}
            className="btn-primary text-sm"
          >
            {loading ? 'Loading...' : 'Start'}
          </button>
        )}

        <button
          onClick={() => handleAction('delete')}
          disabled={loading}
          className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 text-sm"
        >
          {loading ? 'Loading...' : 'Delete'}
        </button>
      </div>
    </div>
  );
}