import { useEffect } from 'react';

import { useWebSocketStore } from '../../store/useWebSocket';

interface LayoutProps {
  children: React.ReactNode;
}

export default function SocketLayout({ children }: LayoutProps) {
  const { connectWebSocket, disconnectWebSocket, isConnected } =
    useWebSocketStore();

  useEffect(() => {
    if (!isConnected) {
      connectWebSocket();
    }

    // cleanup 함수
    return () => {
      disconnectWebSocket();
    };
  }, [connectWebSocket, disconnectWebSocket]);

  return <>{children}</>;
}
