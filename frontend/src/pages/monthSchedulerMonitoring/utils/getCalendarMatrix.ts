interface DailySummary {
  day: number;
  pending: number;
  success: number;
  fail: number;
}

export interface CalendarMatrixElement {
  day: number;
  isCurrentMonth: boolean;
  pending: number;
  success: number;
  fail: number;
}

export const getCalendarMatrix = (
  year: number,
  month: number,
  monthSchedules: DailySummary[] = [],
): CalendarMatrixElement[] => {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const prevMonthLastDay = new Date(year, month - 1, 0);

  const startDayOfWeek = firstDay.getDay();
  const daysInMonth = lastDay.getDate();
  const daysInPrevMonth = prevMonthLastDay.getDate();

  const scheduleMap = new Map<number, DailySummary>();
  monthSchedules.forEach(summary => {
    scheduleMap.set(summary.day, summary);
  });

  const matrix: CalendarMatrixElement[] = [];

  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    matrix.push({
      day: daysInPrevMonth - i,
      isCurrentMonth: false,
      pending: 0,
      success: 0,
      fail: 0,
    });
  }

  for (let i = 1; i <= daysInMonth; i++) {
    const summary = scheduleMap.get(i);
    matrix.push({
      day: i,
      isCurrentMonth: true,
      pending: summary?.pending ?? 0,
      success: summary?.success ?? 0,
      fail: summary?.fail ?? 0,
    });
  }

  let nextMonthDay = 1;
  while (matrix.length < 42) {
    matrix.push({
      day: nextMonthDay++,
      isCurrentMonth: false,
      pending: 0,
      success: 0,
      fail: 0,
    });
  }
  return matrix;
};
