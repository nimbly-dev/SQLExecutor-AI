// darkTheme.ts
import { createTheme } from '@mui/material/styles';
import { baseTheme } from 'themes/base/baseTheme';

declare module '@mui/material/styles' {
  interface Theme {
    custom: {
      appBarBg: string;
    };
  }
  interface ThemeOptions {
    custom?: {
      appBarBg?: string;
    };
  }
}

export const darkTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'dark',
    primary: { main: '#1976d2' },
    background: { default: '#2b2b2b', paper: '#3b3b3b' },
    text: { primary: '#e5e7eb', secondary: '#94a3b8' },
    error: { main: '#f44336' },
    warning: { main: '#ffb74d' },
  },
  custom: {
    appBarBg: '#1e293b',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          '&:hover': { boxShadow: 'var(--shadow-dark-sm)' },
          '&.MuiButton-contained': { boxShadow: 'var(--shadow-dark-md)' },
          '&.MuiButton-containedPrimary': {
            color: '#ffffff',
            backgroundColor: '#1976d2',
            '&:hover': { backgroundColor: '#1565c0' },
            '&.Mui-disabled': {
              backgroundColor: 'rgba(255, 255, 255, 0.12)',
              color: 'rgba(255, 255, 255, 0.3)',
            },
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: ({ theme }) => ({
          backgroundColor: theme.custom.appBarBg,
        }),
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: ({ theme }) => ({
          backgroundColor: theme.custom.appBarBg,
        }),
      },
    },
  },
});
