import axios from 'axios';
import { BASE_URL } from '../utils/apiConfig';

const API_URL = `${BASE_URL}/v1/admin-auth`;


export const loginApi = async (tenantID: string, userID: string, password: string) => {
  const response = await axios.post(`${API_URL}/login`, {
    tenant_id: tenantID,
    user_id: userID,
    password: password,
  });
  return response.data;
};
