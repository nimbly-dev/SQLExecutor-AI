import { CSSObject } from '@mui/system';

export const baseTheme = {
  zIndex: {
    modal: 1300,
    modalContent: 1301,
    drawer: 1200,
    appBar: 1300,
    select: 1250,
    tooltip: 1800,
    snackbar: 1900,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 'var(--border-radius-sm)',
          transition: 'var(--transition-default)',
          '&:hover': {
            boxShadow: 'var(--shadow-sm)',
          },
          '&.MuiButton-contained': {
            boxShadow: 'var(--shadow-md)',
          },
        },
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        html: { height: '100%' },
        body: {
          margin: 0,
          padding: 0,
          height: '100%',
          width: '100%',
          overflow: 'auto',
          boxSizing: 'border-box',
        },
        '#root': { height: '100%', width: '100%' },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 'var(--border-radius-lg)',
          transition: 'var(--transition-box-shadow)',
          boxShadow: 'var(--shadow-sm)',
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: '20px',
          '&:last-child': { paddingBottom: '20px' },
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        root: {
          '& .MuiSwitch-track': { opacity: 0.2 },
          '& .MuiSwitch-thumb': { backgroundColor: '#ffffff' },
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: { borderColor: 'rgba(0, 0, 0, 0.12)' },
      },
    },
    MuiSelect: {
      defaultProps: {
        MenuProps: {
          sx: { zIndex: 1250 },
          PaperProps: { sx: { zIndex: 1250 } },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          zIndex: 1300,
          borderRadius: 0,
          border: 'none',
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
          // Do not force inner Toolbar width here.
        },
      },
    },
    MuiSnackbar: {
      styleOverrides: {
        // Wrap the style override in a function to satisfy types.
        root: (): CSSObject => ({
          position: 'fixed',
          zIndex: 1900,
        }),
      },
    },
    MuiDialog: {
      styleOverrides: { root: { zIndex: 1300 } },
    },
  },
};

