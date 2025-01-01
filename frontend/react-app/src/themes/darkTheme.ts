import { createTheme } from '@mui/material/styles';

export const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#1976d2', // Darker blue for primary
      },
      secondary: {
        main: '#64b5f6', // Softer blue highlight
      },
      background: {
        default: '#0f172a', // Deep dark background
        paper: '#1e293b',  // Slightly lighter for containers
      },
      text: {
        primary: '#e5e7eb', // Light gray for text
        secondary: '#94a3b8', // Softer gray for secondary text
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            color: '#ffffff',
            backgroundColor: '#1976d2', // Button matches primary
            '&:hover': {
              backgroundColor: '#1565c0', // Slightly darker on hover
            },
          },
        },
      },
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: '#0f172a', // Background outside the card
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: '#1e293b', // Matches the container design
            borderRadius: '8px',
            padding: '16px',
          },
        },
      },
    },
  });
