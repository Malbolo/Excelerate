export type DataValue = string | number | boolean | null | Date;

export type DataFrameRow = {
  [key: string]: DataValue;
};

export type DataFrame = DataFrameRow[];
