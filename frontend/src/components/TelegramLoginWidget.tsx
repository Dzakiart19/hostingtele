'use client';

import { useEffect, useRef } from 'react';
import { TelegramAuthData } from '@/types';

interface TelegramLoginWidgetProps {
  botUsername: string;
  onAuth: (authData: TelegramAuthData) => void;
}

declare global {
  interface Window {
    TelegramLoginWidget: {
      dataOnauth: (user: any) => void;
    };
  }
}

export default function TelegramLoginWidget({ botUsername, onAuth }: TelegramLoginWidgetProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Set global callback
    window.TelegramLoginWidget = {
      dataOnauth: (user: any) => {
        onAuth(user);
      }
    };

    // Create script element
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botUsername);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)');
    script.setAttribute('data-request-access', 'write');
    script.async = true;

    // Append to container
    if (ref.current) {
      ref.current.appendChild(script);
    }

    return () => {
      // Cleanup
      if (ref.current && script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [botUsername, onAuth]);

  return (
    <div 
      ref={ref}
      className="flex justify-center items-center"
    />
  );
}