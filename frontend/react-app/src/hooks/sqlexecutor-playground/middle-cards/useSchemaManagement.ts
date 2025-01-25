import { useState, useEffect } from 'react';
import { getSchemas } from '../../../services/schemaService';
import { SchemaSummary } from '../../../types/sqlexecutor-playground/schemaModalContent';

export const useSchemaManagement = () => {
  const [schemas, setSchemas] = useState<SchemaSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSchemas = async () => {
      try {
        const schemaData = await getSchemas();
        setSchemas(schemaData);
      } catch (error) {
        console.error('Error fetching schemas:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSchemas();
  }, []);

  return {
    schemas,
    loading
  };
};
