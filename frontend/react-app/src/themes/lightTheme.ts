import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
    palette: {
      mode: 'light',
      primary: {
        main: '#007bff', // Bright blue for primary
      },
      secondary: {
        main: '#6c757d', // Subtle gray for secondary
      },
      background: {
        default: '#f8f9fa', // Light background
        paper: '#ffffff', // White for containers
      },
      text: {
        primary: '#212529', // Dark gray for primary text
        secondary: '#6c757d', // Softer gray for secondary text
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            color: '#ffffff',
            backgroundColor: '#007bff', // Matches primary
            '&:hover': {
              backgroundColor: '#0056b3', // Darker blue on hover
            },
          },
        },
      },
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: '#f8f9fa', // Light background outside the card
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: '#ffffff', // White for cards
            borderRadius: '8px',
            padding: '16px',
          },
        },
      },
    },
  });
