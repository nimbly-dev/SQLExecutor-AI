import React, { useState } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Typography,
  useTheme,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SchemaSelector from './schema-selector/SchemaSelector';
import { SchemaSummary } from '../../../types/sqlexecutor-playground/schemaModalContent';
import { APIError } from '../../../types/sql-generation/errors/errorResponses';

interface ChatInterfaceProps {
  onGenerateSQL: (prompt: string, schema: string | null, runSql: boolean) => Promise<void>;
  queryHistory: { prompt: string; sql: string }[];
  schemas: SchemaSummary[];
  isLoading?: boolean;
  onError: (error: APIError) => void;
}

/**
 * ChatInterface component to handle user input and SQL generation.
 * @param {ChatInterfaceProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onGenerateSQL,
  queryHistory,
  schemas,
  isLoading = false,
  onError,
}) => {
  const theme = useTheme();
  const [prompt, setPrompt] = useState('');
  const [sqlOnly, setSqlOnly] = useState(false);
  const [selectedSchema, setSelectedSchema] = useState<SchemaSummary | null>(null);

  // Handle SQL Generation
  const handleGenerateSQL = async () => {
    const schema = selectedSchema?.schema_name === 'Auto-Resolve Schema' ? null : selectedSchema?.schema_name || null;
    try {
      await onGenerateSQL(prompt, schema, sqlOnly);
    } catch (error) {
      if (error && typeof error === 'object') {
        onError(error as APIError);
      }
    }
  };

  return (
    <Box className={`chat-interface__container chat-interface__container--${theme.palette.mode}`}>
      {/* Schema Selector */}
      <Box className="chat-interface__schema-selector">
        <SchemaSelector
          schemas={schemas}
          selectedSchema={selectedSchema}
          onSchemaSelect={(schema) => setSelectedSchema(schema)}
        />
      </Box>

      {/* Chat Input Field */}
      <Box className="chat-interface__input">
        <TextField
          multiline
          rows={4}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          fullWidth
          placeholder="Ask your question here..."
          variant="outlined"
          InputProps={{
            endAdornment: (
              <Box className="chat-interface__send-button-wrapper">
                <Tooltip title="Generate SQL">
                  <span>
                    <IconButton
                      className="chat-interface__send-button"
                      color="primary"
                      onClick={handleGenerateSQL}
                      disabled={isLoading || !prompt.trim()}
                      size="medium"
                    >
                      <SendIcon />
                    </IconButton>
                  </span>
                </Tooltip>
              </Box>
            ),
          }}
        />
      </Box>

      {/* Toggle Options */}
      <Box className="chat-interface__options">
        <FormControlLabel
          control={<Switch checked={sqlOnly} onChange={(e) => setSqlOnly(e.target.checked)} />}
          label="Run SQL"
        />
      </Box>
    </Box>
  );
};

export default ChatInterface;
