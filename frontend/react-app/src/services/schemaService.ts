import { BASE_URL } from '../utils/apiConfig';
import axios from 'axios';
import Cookies from 'js-cookie';
import { SchemaSummary } from '../types/sqlexecutor-playground/schemaModalContent';
const API_URL = `${BASE_URL}/v1/schema-manager`;

export const getSchemas = async (): Promise<SchemaSummary[]> => {
    const token = Cookies.get('token');
    const tenant_id = Cookies.get('tenant_id');
    const response = await axios.get(`${API_URL}/${tenant_id}/schemas?summary=true`, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
}