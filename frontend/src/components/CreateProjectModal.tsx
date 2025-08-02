'use client';

import { useState } from 'react';
import { projectsAPI } from '@/lib/api';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateProjectModal({ isOpen, onClose, onSuccess }: CreateProjectModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    bot_token: '',
    zip_file: null as File | null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.bot_token || !formData.zip_file) {
      setError('Semua field harus diisi');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('bot_token', formData.bot_token);
      formDataToSend.append('zip_file', formData.zip_file);

      await projectsAPI.createProject(formDataToSend);
      
      // Reset form
      setFormData({
        name: '',
        bot_token: '',
        zip_file: null,
      });
      
      onSuccess();
      onClose();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Gagal membuat proyek');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.zip')) {
        setError('File harus berformat .zip');
        return;
      }
      if (file.size > 50 * 1024 * 1024) { // 50MB
        setError('Ukuran file maksimal 50MB');
        return;
      }
      setFormData({ ...formData, zip_file: file });
      setError('');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Deploy Bot Baru dari .zip</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nama Proyek
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="contoh: Bot Notifikasi Saya"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-telegram-blue"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Token Bot Telegram
            </label>
            <input
              type="text"
              value={formData.bot_token}
              onChange={(e) => setFormData({ ...formData, bot_token: e.target.value })}
              placeholder="1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-telegram-blue font-mono text-sm"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Token bot yang akan dijalankan (bukan token platform)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              File .zip
            </label>
            <input
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-telegram-blue"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Maksimal 50MB. Harus berisi requirements.txt (Python) atau package.json (Node.js)
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
              disabled={loading}
            >
              Batal
            </button>
            <button
              type="submit"
              className="btn-primary flex-1"
              disabled={loading}
            >
              {loading ? 'Sedang memproses...' : 'Deploy Bot'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}