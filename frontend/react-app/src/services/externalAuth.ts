import { BASE_URL } from '../utils/apiConfig';
import axios from 'axios';
import Cookies from 'js-cookie';
import { ExternalSessionData } from '../types/authentication/externalUserSessionData';

const API_URL = `${BASE_URL}/v1/external-auth`;

export const loginExternalUser = async (auth_field: string, auth_passkey_field: string): Promise<ExternalSessionData> => {
    const auth_tenant_id = Cookies.get('tenant_id');
    console.log('tenant_id:', auth_tenant_id);
    try {
        const response = await axios.post(`${API_URL}/login`, {
            auth_tenant_id,
            auth_field,
            auth_passkey_field
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

export const logoutExternalUser = async (): Promise<void> => {
    const external_session_id = Cookies.get('external_session_id');
    try{
        await axios.post(`${API_URL}/logout/${external_session_id}`);
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