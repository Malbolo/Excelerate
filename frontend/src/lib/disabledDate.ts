export const disabledDate = (date: Date, endDate: Date | undefined, startDate: Date | undefined) => {
  if (endDate && date > endDate) return true;
  if (startDate && date < startDate) return true;
  if (date > new Date(new Date().setHours(0, 0, 0, 0))) return true;
  return false;
};
