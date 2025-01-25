import { BASE_URL } from '../utils/apiConfig';
import axios from 'axios';
import { TenantSetting } from '../types/settings/tenantSetting';
import Cookies from 'js-cookie';

const API_URL = `${BASE_URL}/v1/tenants`;


export const getSetting = async (setting_category_key: string, setting_key: string):  Promise<TenantSetting> =>{
    try {
        const tenantId = Cookies.get('tenant_id');
        const token = Cookies.get('token');
        const response = await axios.get(`${API_URL}/${tenantId}/settings/${setting_category_key}/${setting_key}`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            if (error.response?.status === 400) {
                throw new Error('Bad request. Please check your input.');
            } else if (error.response?.status === 403) {
                throw new Error('Unauthorized. Logout failed.');
            }
        }
        throw new Error('An unexpected error occurred.');
    }
}