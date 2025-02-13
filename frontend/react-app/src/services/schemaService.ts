import axios from 'axios';
import Cookies from 'js-cookie';
import { BASE_URL } from 'utils/apiConfig';
import { Schema, SchemaResponse, SchemaFilters, SchemaSummary } from 'types/schema/schemaType';

const API_URL = `${BASE_URL}/v1/schema-manager`;

export const getSchemas = async (): Promise<SchemaSummary[]> => {
    const token = Cookies.get('token');
    const tenant_id = Cookies.get('tenant_id');
    const response = await axios.get(`${API_URL}/${tenant_id}/schemas?summary=true`, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
}

export const getSchemaByName = async (name: string): Promise<Schema> => {
  const token = Cookies.get('token');
  const tenant_id = Cookies.get('tenant_id');
  
  try {
    const response = await axios.get(
      `${API_URL}/${tenant_id}/schemas`, {
        params: { name },
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      throw new Error('Schema not found');
    }
    throw new Error('Failed to fetch schema');
  }
};

export const getSchemasPaginated = async ({
  name,
  contextType,
  page = 1,
  pageSize = 10,
}: Partial<SchemaFilters>): Promise<SchemaResponse> => {
  const token = Cookies.get('token');
  const tenant_id = Cookies.get('tenant_id');
  
  const params = new URLSearchParams({
    summary_paginated: 'true',
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  // Only add name parameter if it's not empty
  if (name?.trim()) params.append('name', name.trim());
  if (contextType && contextType !== 'all') params.append('context_type', contextType);

  try {
    const response = await axios.get(
      `${API_URL}/${tenant_id}/schemas?${params}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    return {
      schemas: response.data.schemas || [],
      total: response.data.total || 0,
      page: response.data.page || 1,
      page_size: response.data.page_size || pageSize
    };
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return {
        schemas: [],
        total: 0,
        page: 1,
        page_size: pageSize
      };
    }
    throw error;
  }
};

export const addSchema = async (schemaData: Schema): Promise<Schema> => {
  const token = Cookies.get('token');
  const tenantId = Cookies.get('tenant_id');
  
  try {
    const response = await axios.post(`${API_URL}/${tenantId}/schemas`, schemaData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    console.error('Add schema error:', error);
    throw error;
  }
}

export const deleteSchema = async (schemaId: string): Promise<void> => {
    const token = Cookies.get('token');
    const tenantId = Cookies.get('tenant_id');
    await axios.delete(`${API_URL}/${tenantId}/schemas/${schemaId}`, {
        headers: { Authorization: `Bearer ${token}` }
    });
}

export const updateSchemaByName = async (name: string, schemaData: Partial<Schema>): Promise<Schema> => {
  const token = Cookies.get('token');
  const tenant_id = Cookies.get('tenant_id');

  try {
    const response = await axios.put(
      `${API_URL}/${tenant_id}/schemas/${name}`,
      schemaData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data.schema || response.data;
  } catch (error) {
    console.error('Update schema error:', error);
    throw error;
  }
};