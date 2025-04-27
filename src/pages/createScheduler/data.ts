import { Job, Status } from '@/types/scheduler';

// Job 타입 임포트 가정

const generateDummyJobs = (count: number): Job[] => {
  const jobs: Job[] = [];
  for (let i = 1; i <= count; i++) {
    const statusOptions = ['pending', 'success', 'error'];
    const randomStatus = statusOptions[Math.floor(Math.random() * 3)];
    jobs.push({
      jobId: `job-${String(i).padStart(3, '0')}`,
      title: `자동 보고서 생성 작업 ${i}`,
      description: `매일 ${i}시 실행되는 데이터 분석 및 보고서 자동 생성 스케줄 ${i}`,
      createdAt: new Date(
        Date.now() - Math.random() * 1000000000,
      ).toISOString(), // 무작위 생성 시간
      commandList: [
        {
          commandId: `cmd-${i}-1`,
          commandTitle: `데이터 수집 ${i}`,
          commandStatus: randomStatus as Status,
        },
        {
          commandId: `cmd-${i}-2`,
          commandTitle: `데이터 처리 ${i}`,
          commandStatus: 'pending',
        },
        {
          commandId: `cmd-${i}-3`,
          commandTitle: `보고서 생성 ${i}`,
          commandStatus: 'pending',
        },
      ],
    });
  }
  // 검색 테스트를 위한 데이터 추가
  jobs.push({
    jobId: 'job-kpi',
    title: 'KPI 데이터 집계',
    description: '월간 KPI 데이터 집계 작업',
    createdAt: new Date().toISOString(),
    commandList: [],
  });
  jobs.push({
    jobId: 'job-sync',
    title: '사용자 데이터 동기화',
    description: '외부 시스템과 사용자 데이터 동기화',
    createdAt: new Date().toISOString(),
    commandList: [],
  });
  return jobs;
};

export const allDummyJobs = generateDummyJobs(20); // 총 22개 생성
