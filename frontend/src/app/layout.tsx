import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ZipHostBot - Platform Hosting Bot Telegram',
  description: 'Deploy dan kelola Bot Telegram Anda dengan mudah melalui upload file ZIP',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="bg-gray-50 min-h-screen">
        {children}
      </body>
    </html>
  );
}