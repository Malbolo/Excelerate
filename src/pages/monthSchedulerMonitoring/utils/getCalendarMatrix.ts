export function getCalendarMatrix(year: number, month: number) {
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
}
