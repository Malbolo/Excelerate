import { TLog } from '@/types/agent';

export const MGraph: TLog[] = Array.from({ length: 10 }, (_, index) => ({
  name: `log name ${index + 1}`,
  input: '당신은 pandas dataframe 형식의 데이터를 처리하는 전문가입니다.',
  output: '4월 5일 이후의 데이터만 필터링해 주세요.',
  timestamp: '2025-04-22T09:44:58Z',
  metadata: {
    model: 'gpt-4o',
    version: '1.0.0',
  },
  subEvents: [],
}));

export const MGraphWithSubEvents: TLog[] = Array.from(
  { length: 10 },
  (_, index) => {
    const baseLog: TLog = {
      name: `log name ${index + 1}`,
      input: '당신은 pandas dataframe 형식의 데이터를 처리하는 전문가입니다.',
      output: '4월 5일 이후의 데이터만 필터링해 주세요.',
      timestamp: '2025-04-22T09:44:58Z',
      metadata: {
        model: 'gpt-4o',
        version: '1.0.0',
      },
      subEvents: [],
    };

    // 두 번째 노드에만 subEvents 추가
    if (index === 1) {
      baseLog.subEvents = [
        {
          name: 'sub event 1',
          input: 'sub input 1',
          output: 'sub output 1',
          timestamp: '2025-04-22T09:45:00Z',
          metadata: {
            model: 'gpt-4o',
            version: '1.0.0',
          },
          subEvents: [
            {
              name: 'sub event 3',
              input: 'sub input 1',
              output: 'sub output 1',
              timestamp: '2025-04-22T09:45:00Z',
              metadata: {
                model: 'gpt-4o',
                version: '1.0.0',
              },
              subEvents: [],
            },
            {
              name: 'sub event 4',
              input: 'sub input 1',
              output: 'sub output 1',
              timestamp: '2025-04-22T09:45:00Z',
              metadata: {
                model: 'gpt-4o',
                version: '1.0.0',
              },
              subEvents: [],
            },
          ],
        },
        {
          name: 'sub event 2',
          input: 'sub input 2',
          output: 'sub output 2',
          timestamp: '2025-04-22T09:45:10Z',
          metadata: {
            model: 'gpt-4o',
            version: '1.0.0',
          },
          subEvents: [],
        },
      ];
    }

    return baseLog;
  },
);
