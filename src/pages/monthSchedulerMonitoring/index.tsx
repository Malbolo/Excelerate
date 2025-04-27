import React, { useState } from 'react';

import DateNavigator from '@/components/DateNavigator';

import CalendarGrid from './components/CalendarGrid';

const SchedulerMonitoringPage: React.FC = () => {
  const [year] = useState(2025);
  const [month] = useState(4);
  const today = new Date();

  return (
    <div className='mx-auto mt-8 w-full rounded-lg bg-white p-2 shadow'>
      <DateNavigator />
      <CalendarGrid year={year} month={month} today={today} />
    </div>
  );
};

export default SchedulerMonitoringPage;
