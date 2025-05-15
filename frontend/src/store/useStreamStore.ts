import { toast } from 'sonner';
import { create } from 'zustand';

import { generateStreamId } from '@/lib/generateStreamId';
import { Log } from '@/types/agent';

interface StreamState {
  streamId: string | null;
  isConnected: boolean;
  eventSource: EventSource | null;
  logs: Log[];
  notice: string;

  connectStream: () => void;
  disconnectStream: () => void;
  resetLogs: () => void;
  resetStream: () => void;
}

export const useStreamStore = create<StreamState>((set, get) => ({
  streamId: null,
  isConnected: false,
  eventSource: null,
  logs: [],
  notice: '',

  connectStream: () => {
    const currentEventSource = get().eventSource;
    const currentStreamId = get().streamId;

    if (currentEventSource !== null && currentStreamId !== null) {
      return;
    }

    const newStreamId = generateStreamId();
    const eventSource = new EventSource(
      `${import.meta.env.VITE_BASE_URL}/api/agent/logs/stream/${newStreamId}`,
    );

    eventSource.addEventListener('log', event => {
      try {
        const log = JSON.parse(event.data) as Log;
        set(state => ({
          logs: [...state.logs, log],
          isConnected: true,
        }));
      } catch (error) {
        toast.error(`Failed to parse SSE message: ${error}`);
      }
    });

    eventSource.addEventListener('notice', event => {
      set({ notice: event.data });
    });

    eventSource.addEventListener('stop', () => {
      set({ notice: '' });
    });

    eventSource.onerror = error => {
      set({ isConnected: false });
      toast.error(`Connection error: ${error}`);
    };

    set({
      eventSource,
      streamId: newStreamId,
      isConnected: true,
    });
  },

  disconnectStream: () => {
    const { eventSource } = get();
    if (eventSource) {
      eventSource.close();
      set({
        isConnected: false,
        eventSource: null,
        streamId: null,
        notice: '',
      });
    }
  },

  resetLogs: () => {
    set({ logs: [] });
  },

  resetStream: () => {
    const { eventSource } = get();
    if (eventSource) {
      eventSource.close();
    }
    set({
      isConnected: false,
      eventSource: null,
      logs: [],
      streamId: null,
      notice: '',
    });
  },
}));
