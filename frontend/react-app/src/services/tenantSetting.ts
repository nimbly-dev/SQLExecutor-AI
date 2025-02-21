import axios from 'axios';
import Cookies from 'js-cookie';
import { BASE_URL } from 'utils/apiConfig';
import { SettingDetail, TenantSetting, TenantSettingCategoryDetails } from 'types/settings/tenantSettingType';

interface CategoryResponse {
    categories: string[];
}

const API_URL = `${BASE_URL}/v1/tenants`;

export const getSettingDetail = async (setting_category_key: string, setting_key: string):  Promise<TenantSetting> =>{
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

export const updateSettingDetail = async (
  setting_category_key: string,
  setting_key: string,
  settingDetail: SettingDetail
): Promise<SettingDetail> => {
  try {
    const tenantId = Cookies.get('tenant_id');
    const token = Cookies.get('token');
    const response = await axios.put(
      `${API_URL}/${tenantId}/settings/${setting_category_key}`,
      {
        [setting_key]: settingDetail
      },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        throw new Error('Bad request. Please check your input.');
      } else if (error.response?.status === 403) {
        throw new Error('Unauthorized.');
      }
    }
    throw new Error('An unexpected error occurred while updating the setting.');
  }
};

export const getSettingCategoryKeys = async (): Promise<string[]> => {
    try {
        const tenantId = Cookies.get('tenant_id');
        const token = Cookies.get('token');
        const response = await axios.get<CategoryResponse>(`${API_URL}/${tenantId}/settings`, {
            headers: {
                Authorization: `Bearer ${token}`
            },
            params:{
                categories_only: true
            }
        });
        
        // Extract the categories array from the response
        if (response.data && Array.isArray(response.data.categories)) {
            return response.data.categories;
        }
        
        console.warn('Unexpected API response format:', response.data);
        return [];
    } catch (error) {
        console.error('Error fetching category keys:', error);
        return [];
    }
}

export const getSettingDetailsByCategory = async (setting_category_key: string): Promise<TenantSettingCategoryDetails> => {
    try {
        const tenantId = Cookies.get('tenant_id');
        const token = Cookies.get('token');
        const response = await axios.get(`${API_URL}/${tenantId}/settings/${setting_category_key}`, {
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