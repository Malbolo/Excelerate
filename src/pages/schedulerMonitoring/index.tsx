import React, { useState } from 'react';

import CalendarGrid from './components/CalendarGrid';
import CalendarHeader from './components/CalendarHeader';

const SchedulerMonitoringPage: React.FC = () => {
  const [year, setYear] = useState(2025);
  const [month, setMonth] = useState(4);
  const today = new Date();

  const handlePrev = () => {
    if (month === 1) {
      setYear(y => y - 1);
      setMonth(12);
    } else {
      setMonth(m => m - 1);
    }
  };

  const handleNext = () => {
    if (month === 12) {
      setYear(y => y + 1);
      setMonth(1);
    } else {
      setMonth(m => m + 1);
    }
  };

  return (
    <div className='mx-auto mt-8 w-full rounded-lg bg-white p-2 shadow'>
      <CalendarHeader
        year={year}
        month={month}
        onPrev={handlePrev}
        onNext={handleNext}
      />
      <CalendarGrid year={year} month={month} today={today} />
    </div>
  );
};

export default SchedulerMonitoringPage;
