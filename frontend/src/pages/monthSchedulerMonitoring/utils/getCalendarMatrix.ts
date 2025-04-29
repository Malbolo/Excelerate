// Info : 캘린더 그리드를 그리는 함수
// 캘린더 그리드는 7x6 행렬로 이루어져 있음

export const getCalendarMatrix = (year: number, month: number) => {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const prevMonthLastDay = new Date(year, month - 1, 0);

  const startDayOfWeek = firstDay.getDay();
  const daysInMonth = lastDay.getDate();
  const daysInPrevMonth = prevMonthLastDay.getDate();

  const matrix: { day: number; isCurrentMonth: boolean }[] = [];

  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    matrix.push({ day: daysInPrevMonth - i, isCurrentMonth: false });
  }

  for (let i = 1; i <= daysInMonth; i++) {
    matrix.push({ day: i, isCurrentMonth: true });
  }

  while (matrix.length < 42) {
    matrix.push({
      day: matrix.length - (startDayOfWeek + daysInMonth) + 1,
      isCurrentMonth: false,
    });
  }
  return matrix;
};

export const isSameDate = (date1: Date, date2: Date): boolean => {
  if (!date1 || !date2) return false;
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
};

// Delete : 오늘날짜를 기준으로, 이전날짜이면 Pending 상태를 포함하지 않는 UI를 위한 함수 추후 삭제 예정
export const isBeforeDate = (date1: Date, date2: Date): boolean => {
  if (!date1 || !date2) return false;
  const d1 = new Date(date1.getFullYear(), date1.getMonth(), date1.getDate());
  const d2 = new Date(date2.getFullYear(), date2.getMonth(), date2.getDate());
  return d1 < d2;
};
