import React, { useState } from 'react';
import { Box, Select, MenuItem, SelectChangeEvent } from '@mui/material';
import SchemaSelectorModal from './SchemaSelectorModal';
import { SchemaSummary } from '../../../../types/sqlexecutor-playground/schemaModalContent';

interface SchemaSelectorProps {
    schemas: SchemaSummary[];
    selectedSchema: SchemaSummary | null;
    onSchemaSelect: (schema: SchemaSummary | null) => void;
}

const SchemaSelector: React.FC<SchemaSelectorProps> = ({
    schemas,
    selectedSchema,
    onSchemaSelect,
}) => {
    const [isModalOpen, setModalOpen] = useState(false);

    const handleOpenModal = () => setModalOpen(true);
    const handleCloseModal = () => setModalOpen(false);

    const handleSelectSchema = (schema: SchemaSummary) => {
        onSchemaSelect(schema); 
        setModalOpen(false);
    };

    const handleSchemaChange = (event: SelectChangeEvent<string>) => {
        const value = event.target.value;
        if (value === 'Auto-Resolve Schema') {
            onSchemaSelect(null);
        } else if (value === 'Custom Schema') {
            handleOpenModal();
        } else {
            const selected = schemas.find(schema => schema.schema_name === value);
            if (selected) {
                onSchemaSelect(selected);
            }
        }
    };

    return (
        <Box>
            <Select
                value={selectedSchema?.schema_name || 'Auto-Resolve Schema'}
                onChange={handleSchemaChange}
            >
                <MenuItem value="Auto-Resolve Schema">Auto-Resolve Schema</MenuItem>
                {selectedSchema && (
                    <MenuItem value={selectedSchema.schema_name}>{selectedSchema.schema_name}</MenuItem>
                )}
                <MenuItem value="Custom Schema">Select a Schema</MenuItem>
            </Select>

            {/* Schema Modal */}
            <SchemaSelectorModal
                open={isModalOpen}
                onClose={handleCloseModal}
                schemas={schemas}
                onSelectSchema={handleSelectSchema}
                selectedSchema={selectedSchema}
            />
        </Box>
    );
};

export default SchemaSelector;
