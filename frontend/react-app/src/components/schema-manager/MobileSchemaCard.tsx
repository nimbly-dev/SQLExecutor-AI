import React from 'react';
import { 
  Card, CardContent, Typography, IconButton, 
  Box, Tooltip 
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { SchemaSummary } from 'types/schema/schemaType';
import styles from 'styles/schema-manager/MobileSchemaCard.module.scss';

interface MobileSchemaCardProps {
  schema: SchemaSummary;
  onDelete: () => void;
  onView: () => void;
}

export function MobileSchemaCard({ 
  schema, 
  onDelete, 
  onView 
}: MobileSchemaCardProps) {
  return (
    <Card className={styles.card}>
      <CardContent>
        <div className={styles.cardContent}>
          <div className={styles.cardInfo}>
            <Typography variant="h6" component="div">
              {schema.schema_name}
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              {schema.description}
            </Typography>
            <Typography variant="body2">
              Type: {schema.context_type}
            </Typography>
            <Typography variant="body2">
              User: {schema.user_identifier}
            </Typography>
          </div>
          <div className={styles.actionButtons}>
            <Tooltip title="View details">
              <IconButton onClick={onView}>
                <VisibilityIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete schema">
              <IconButton color="error" onClick={onDelete}>
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
