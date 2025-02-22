// lightTheme.ts
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

export const lightTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'light',
    primary: { main: '#007bff' },
    background: { default: '#f9f9f9', paper: '#ffffff' },
  },
  custom: {
    appBarBg: '#007bff', // Bright blue AppBar for light theme
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: ({ theme }) => ({
          backgroundColor: theme.custom.appBarBg,
        }),
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#ffffff', // Keep Drawer background light
        },
      },
    },
  },
});
