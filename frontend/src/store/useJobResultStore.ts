import { ColumnDef } from '@tanstack/react-table';
import { create } from 'zustand';

import { DataFrame, DataFrameRow } from '@/types/dataframe';
import { ErrorMessage } from '@/types/job';

interface JobResultState {
  columns: ColumnDef<DataFrameRow>[];
  dataframe: DataFrame | null;
  code: string;
  downloadToken: string;
  errorMsg: ErrorMessage | null;

  setColumns: (columns: ColumnDef<DataFrameRow>[]) => void;
  setDataframe: (data: DataFrame | null) => void;
  setCode: (code: string) => void;
  setDownloadToken: (token: string) => void;
  setErrorMsg: (msg: ErrorMessage | null) => void;
  resetResult: () => void;
}

export const useJobResultStore = create<JobResultState>(set => ({
  columns: [],
  dataframe: null,
  code: '',
  downloadToken: '',
  errorMsg: null,

  setColumns: columns => set({ columns }),
  setDataframe: dataframe => set({ dataframe }),
  setCode: code => set({ code }),
  setDownloadToken: token => set({ downloadToken: token }),
  setErrorMsg: errorMsg => set({ errorMsg }),
  resetResult: () =>
    set({
      columns: [],
      dataframe: null,
      code: '',
      downloadToken: '',
      errorMsg: null,
    }),
}));
