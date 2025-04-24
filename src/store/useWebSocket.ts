import { create } from 'zustand';

interface BareWebSocketState {
  isConnected: boolean;
  client: WebSocket | null;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  updateSubscription: (subscriptionType: string, channelId: string) => void;
  sendMessage: (payload: unknown) => void;
}

export const useWebSocketStore = create<BareWebSocketState>((set, get) => ({
  isConnected: false,
  client: null,

  connectWebSocket: () => {
    const currentClient = get().client;

    if (
      currentClient !== null &&
      currentClient.readyState < WebSocket.CLOSING
    ) {
      return;
    }

    const client = new WebSocket('ws://localhost:8080/ws');

    client.onopen = () => {
      set({ isConnected: true, client });
    };

    client.onmessage = event => {
      const messageData = JSON.parse(event.data);
      const { type, response } = messageData;

      // 채널 메시지 처리
      if (type === 'channel' && response) {
        console.log('channel', response);
      }
    };

    client.onerror = error => {
      console.error('WebSocket error:', error);
    };

    client.onclose = () => {
      set({ isConnected: false, client: null });
    };

    set({ client });
  },

  disconnectWebSocket: () => {
    const { client } = get();
    if (client) {
      client.close(1000, 'User disconnected');
    }
  },

  updateSubscription: (subscriptionType: string, channelId: string) => {
    const { client, isConnected } = get();
    if (!client || !isConnected) return;

    const messagePayload = {
      type: 'subscribe',
      context: subscriptionType,
      channelId,
      authorization: 'ho',
    };

    get().sendMessage(messagePayload);
  },

  sendMessage: (payload: unknown) => {
    const { client } = get();
    if (!client || client.readyState !== WebSocket.OPEN) return;

    try {
      const messageString = JSON.stringify(payload);
      client.send(messageString);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  },
}));
