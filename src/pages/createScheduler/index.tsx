import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';

const CreateSchedulerPage = () => {
  const year = new Date().getFullYear();
  const month = new Date().getMonth() + 1;

  return (
    <SchedulerMonitoringLayout
      title={`${year}년 ${month}월 스케줄 생성`}
      backPath={`/scheduler-monitoring/month/${year}-${month}`}
    >
      <div>CreateSchedulerPage</div>
    </SchedulerMonitoringLayout>
  );
};

export default CreateSchedulerPage;
