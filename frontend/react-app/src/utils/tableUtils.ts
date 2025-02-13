import { Table } from 'types/schema/schemaType';

export const convertTablesToArray = (tables: Record<string, Table>): Array<{ key: string } & Table> => {
  return Object.entries(tables).map(([key, tableData]) => ({
    ...tableData,
    key
  }));
};
