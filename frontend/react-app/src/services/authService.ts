import axios from 'axios';
import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';
import { toast } from 'react-toastify';
import { BASE_URL } from 'utils/apiConfig';
import { AdminSessionData } from 'types/authentication/adminSessionData';
import { AdminLoginRequest } from 'types/authentication/adminLoginRequest';

const API_URL = `${BASE_URL}/v1/admin-auth`;


const setCookie = (key: string, value: string) => {
  Cookies.set(key, value, {
    secure: true,
    sameSite: 'Strict',
    expires: 1
  });
};

export const loginAdmin = async (
  tenantID: string,
  userID: string,
  password: string
): Promise<{ JWT_TOKEN: string; payload: AdminSessionData }> => {
  const requestData: AdminLoginRequest = {
    tenant_id: tenantID,
    user_id: userID,
    password: password,
  };

  const response = await axios.post(`${API_URL}/login`, requestData);

  if (response.data && response.data.JWT_TOKEN) {
    const token = response.data.JWT_TOKEN.split(' ')[1];
    const payload: AdminSessionData = jwtDecode<AdminSessionData>(token);

    setCookie('token', token);
    setCookie('tenant_id', payload.tenant_id);
    setCookie('user_id', payload.user_id);
    setCookie('role', payload.role);

    return { JWT_TOKEN: token, payload };
  } else {
    throw new Error('Invalid login response');
  }
};


export const logoutAdmin = async (): Promise<void> => {
  try {
    const token = Cookies.get('token');
    if (!token) throw new Error('User not authenticated.');


    await axios.post(`${API_URL}/logout`, null, {
      headers: { Authorization: `Bearer ${token}` },
    });


    Cookies.remove('token');
    Cookies.remove('tenant_id');
    Cookies.remove('user_id');
    Cookies.remove('role');


    toast.success('Logged out successfully!');
  } catch (error: any) {
    console.error('Logout error:', error);


    if (error.response && error.response.status === 401) {
      toast.error('Session expired. Redirecting to login...');
      Cookies.remove('token');
      window.location.href = '/login';
    } else {
      toast.error('Failed to logout. Please try again.');
    }

    throw new Error('Failed to logout.');
  }
};