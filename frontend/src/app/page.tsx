'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import TelegramLoginWidget from '@/components/TelegramLoginWidget';
import { authAPI } from '@/lib/api';
import { TelegramAuthData } from '@/types';

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTelegramAuth = async (authData: TelegramAuthData) => {
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(authData);
      
      // Simpan token di cookie
      Cookies.set('access_token', response.access_token, { expires: 7 });
      
      // Redirect ke dashboard
      router.push('/dashboard');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login gagal. Silakan coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  const botUsername = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || 'pocketwiner_Bot';

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ZipHostBot
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Platform Hosting Bot Telegram Berbasis Upload ZIP
          </p>
          
          <div className="bg-white rounded-lg shadow-md p-8 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Cara Kerja Platform
            </h2>
            <div className="text-left space-y-3 text-sm text-gray-600">
              <div className="flex items-start">
                <span className="bg-telegram-blue text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3 mt-0.5">1</span>
                <p>Login menggunakan akun Telegram Anda</p>
              </div>
              <div className="flex items-start">
                <span className="bg-telegram-blue text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3 mt-0.5">2</span>
                <p>Upload file .zip berisi kode bot Telegram Anda</p>
              </div>
              <div className="flex items-start">
                <span className="bg-telegram-blue text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3 mt-0.5">3</span>
                <p>Masukkan token bot yang akan dijalankan</p>
              </div>
              <div className="flex items-start">
                <span className="bg-telegram-blue text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3 mt-0.5">4</span>
                <p>Platform akan otomatis menjalankan bot Anda 24/7</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Login & Kelola Bot Anda
            </h2>
            
            {loading && (
              <div className="mb-4">
                <p className="text-telegram-blue">Sedang memproses login...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <TelegramLoginWidget
              botUsername={botUsername}
              onAuth={handleTelegramAuth}
            />

            <p className="text-xs text-gray-500 mt-4">
              Dengan login, Anda menyetujui penggunaan platform ini untuk menjalankan bot Telegram Anda.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}