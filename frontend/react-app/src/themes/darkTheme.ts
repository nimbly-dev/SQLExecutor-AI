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
      error: {
        main: '#f44336', // Add error color
      },
      warning: {
        main: '#ffb74d', // Add warning color
      },
      background: {
        default: '#2b2b2b', // Deep dark background
        paper: '#3b3b3b',  // Slightly lighter for containers
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
            borderRadius: 'var(--border-radius-sm)',
            transition: 'var(--transition-default)',
            '&:hover': {
              boxShadow: 'var(--shadow-dark-sm)',
            },
            '&.MuiButton-contained': {
              boxShadow: 'var(--shadow-dark-md)',
            },
            '&.MuiButton-containedPrimary': {
              color: '#ffffff',
              backgroundColor: '#1976d2',
              '&:hover': {
                backgroundColor: '#1565c0',
              },
              '&.Mui-disabled': {
                backgroundColor: 'rgba(255, 255, 255, 0.12)',
                color: 'rgba(255, 255, 255, 0.3)',
              }
            },
            '&.MuiButton-containedError': {
              color: '#ffffff',
              backgroundColor: '#f44336',
              '&:hover': {
                backgroundColor: '#d32f2f',
              },
            },
            '&.MuiButton-outlinedWarning': {
              color: '#ffb74d',
              borderColor: '#ffb74d',
              '&:hover': {
                backgroundColor: 'rgba(255, 183, 77, 0.08)',
              },
            },
            '&.Mui-disabled': {
              backgroundColor: '#1a1f2b',
              color: 'rgba(255, 255, 255, 0.3)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
            },
          },
        },
      },
      MuiCssBaseline: {
        styleOverrides: {
          html: {
            height: '100%',
          },
          body: {
            margin: 0,
            padding: 0,
            height: '100%',
            width: '100%',
            backgroundColor: '#0f172a',
            overflow: 'hidden',
            boxSizing: 'border-box',
          },
          '#root': {
            height: '100%',
            width: '100%',
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
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 'var(--border-radius-lg)',
            transition: 'var(--transition-box-shadow)',
            boxShadow: 'none',
            backgroundColor: '#2b2b2b',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            },
            '&.Mui-disabled': {
              backgroundColor: '#1a1f2b',
              color: 'rgba(255, 255, 255, 0.3)',
              cursor: 'not-allowed',
            },
            '& .MuiCardHeader-root': {
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            },
            '& .MuiCardContent-root': {
              backgroundColor: '#3b3b3b',
            }
          },
        },
      },
      MuiCardContent: {
        styleOverrides: {
          root: {
            padding: '20px',
            '&:last-child': {
              paddingBottom: '20px',
            },
          },
        },
      },
      MuiSwitch: {
        styleOverrides: {
          root: {
            '&.Mui-disabled': {
              '& .MuiSwitch-track': {
                backgroundColor: '#2d3748 !important',
                opacity: 0.3,
              },
              '& .MuiSwitch-thumb': {
                backgroundColor: '#4a5568',
              },
            },
            '& .MuiSwitch-switchBase': {
              '&.Mui-checked': {
                '& + .MuiSwitch-track': {
                  backgroundColor: '#1976d2',
                  opacity: 0.5,
                },
              },
            },
            '& .MuiSwitch-track': {
              backgroundColor: '#666666',
              opacity: 0.3,
            },
            '& .MuiSwitch-thumb': {
              backgroundColor: '#ffffff',
            },
          },
        },
      },
      MuiDivider: {
        styleOverrides: {
          root: {
            borderColor: 'rgba(255, 255, 255, 0.1)',
          },
        },
      },
    },
});
