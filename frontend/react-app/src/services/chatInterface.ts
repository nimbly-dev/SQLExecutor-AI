import { BASE_URL } from '../utils/apiConfig';
import axios from 'axios';
import { GetUserContextsResponse } from '../types/chat-interface/contextUsers';
import Cookies from 'js-cookie';
import { ExternalSessionData } from '../types/authentication/externalUserSessionData';

const API_URL = `${BASE_URL}/v1/chat-interface`;

export const getUsersContext = async (page: number, orderDirection: string, pageLimit: number): Promise<GetUserContextsResponse> => {
    try {
        const tenantId = Cookies.get('tenant_id');
        const token = Cookies.get('token');
        const response = await axios.get(`${API_URL}/${tenantId}/users-context`, {
            params: {
                page,
                page_limit: pageLimit,
                order_direction: orderDirection
            },
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

export const createContextSession = async (contextUserIdentifier: string, apiKey: string): Promise<ExternalSessionData> => {
  try {
    const tenantId = Cookies.get('tenant_id');
    const response = await axios.post(
      `${BASE_URL}/v1/api-context/${tenantId}/create-context-session`,
      {
        context_user_identifier_value: contextUserIdentifier
      },
      {
        headers: {
          'x-api-key': apiKey
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        throw new Error('Bad request. Please check your input.');
      } else if (error.response?.status === 403) {
        throw new Error('Unauthorized access.');
      }
    }
    throw new Error('An unexpected error occurred.');
  }
};

export const isSessionExpired = (expiresAt: string): boolean => {
  const expiryDate = new Date(expiresAt);
  const now = new Date();
  return now > expiryDate;
};

export const fetchContextSession = async (sessionId: string, apiKey: string): Promise<ExternalSessionData> => {
  try {
    const tenantId = Cookies.get('tenant_id');
    const response = await axios.get(
      `${BASE_URL}/v1/sql-context/${tenantId}/fetch-context-session`,
      {
        params: {
          external_session_id: sessionId
        },
        headers: {
          'x-api-key': apiKey
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        sessionStorage.removeItem('contextUserSessionId');
        throw new Error('Bad request: Invalid session ID');
      } else if (error.response?.status === 403) {
        sessionStorage.removeItem('contextUserSessionId');
        throw new Error('Unauthorized: Invalid or expired session');
      }
    }
    sessionStorage.removeItem('contextUserSessionId');
    throw new Error('Network error: Unable to fetch session');
  }
};

export const invalidateContextSession = async (sessionId: string, apiKey: string): Promise<void> => {
  try {
    const tenantId = Cookies.get('tenant_id');
    await axios.delete(
      `${BASE_URL}/v1/sql-context/${tenantId}/invalidate-context-session`,
      {
        data: {
          external_session_id: sessionId
        },
        headers: {
          'x-api-key': apiKey
        }
      }
    );
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        throw new Error('Bad request: Invalid session ID');
      } else if (error.response?.status === 403) {
        throw new Error('Unauthorized: Invalid or expired session');
      }
    }
    throw new Error('Network error: Unable to invalidate session');
  }
};