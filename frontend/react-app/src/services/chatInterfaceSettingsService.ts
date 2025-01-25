import axios from 'axios';
import { BASE_URL } from '../utils/apiConfig';
import { SettingsResponse, SettingsUpdatePayload } from '../types/chat-interface/chatInterfaceSettings';
import Cookies from 'js-cookie';

export const fetchChatInterfaceSettings = async (sessionId: string): Promise<SettingsResponse> => {
  try {
    const tenantId = Cookies.get('tenant_id'); 
    const token = Cookies.get('token'); 

    const response = await axios.get(
      `${BASE_URL}/v1/chat-interface/${tenantId}/${sessionId}/chat-interface-settings`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        throw new Error('Bad request: Invalid session ID');
      } else if (error.response?.status === 403) {
        throw new Error('Unauthorized: Invalid or expired session');
      }
    }
    throw new Error('Failed to fetch settings');
  }
};

export const updateChatInterfaceSettings = async (
  sessionId: string,
  payload: SettingsUpdatePayload
): Promise<void> => {
  try {
    const tenantId = Cookies.get('tenant_id');
    const token = Cookies.get('token'); 

    await axios.patch(
      `${BASE_URL}/v1/chat-interface/${tenantId}/${sessionId}/chat-interface-settings`,
      payload,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
  } catch (error) {
    console.error('Update settings error:', error);
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        throw new Error('Bad request: Invalid settings data');
      } else if (error.response?.status === 403) {
        throw new Error('Unauthorized: Invalid or expired session');
      }
    }
    throw new Error('Failed to update settings');
  }
};
