import React from 'react';
import BlockIcon from '@mui/icons-material/Block';
import SearchOffIcon from '@mui/icons-material/SearchOff';
import SchemaIcon from '@mui/icons-material/Schema';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { SvgIconProps } from '@mui/material';
import { ErrorType } from '../../../../types/sql-generation/errors/errorTypes';

/**
 * Props for ErrorIcon component
 */
interface ErrorIconProps extends SvgIconProps {
  errorType?: ErrorType;
}

/**
 * ErrorIcon component that displays an appropriate icon based on error type.
 * @param {ErrorIconProps} props - The component props
 * @returns {JSX.Element} The rendered icon
 */
const ErrorIcon: React.FC<ErrorIconProps> = ({ errorType, ...props }) => {
  switch (errorType) {
    case ErrorType.ACCESS_DENIED:
      return <BlockIcon {...props} />;
    case ErrorType.QUERY_SCOPE_ERROR:
      return <SearchOffIcon {...props} />;
    case ErrorType.SCHEMA_DISCOVERY_ERROR:
      return <SchemaIcon {...props} />;
    default:
      return <ErrorOutlineIcon {...props} />;
  }
};

export default ErrorIcon;
