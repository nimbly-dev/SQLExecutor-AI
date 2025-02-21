import axios from 'axios';
import Cookies from 'js-cookie';
import { BASE_URL } from 'utils/apiConfig';
import { getSettingDetail } from 'services/tenantSetting';
import { SqlGenerationResponse } from 'types/sql-generation/sqlGeneration';
import { ErrorType } from 'types/sql-generation/errors/errorTypes';
import { APIError } from 'types/sql-generation/errors/errorResponses';

const API_URL = `${BASE_URL}/v1/sql-generation`;

export const generateSql = async (run_sql: boolean, user_input: string, schema_selected: string | null): Promise<SqlGenerationResponse> => {
    try {
        const tenantId = Cookies.get('tenant_id');
        const apiKeyResponse = await getSettingDetail('API_KEYS', 'TENANT_APPLICATION_TOKEN');
        const apiKey = apiKeyResponse.setting_detail.setting_value;
        const sessionId = sessionStorage.getItem('contextUserSessionId');

        var endpoint_url = ""

        if (schema_selected != null){
            endpoint_url =  `${API_URL}/${tenantId}/${schema_selected}`
        } else{
            endpoint_url =  `${API_URL}/${tenantId}`
        }
        const response = await axios.post(
            `${endpoint_url}?run_sql=${run_sql}`,
            {
                input: user_input
            },
            {
                headers: {
                    'x-api-key': apiKey,
                    'x-session-id': sessionId
                }
            }
        );
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response?.data) {
            const errorData = error.response.data;
            
            if (typeof errorData.detail === 'string') {
                throw {
                    detail: {
                        error_type: ErrorType.RUNTIME_ERROR,
                        message: errorData.detail,
                        detail: errorData.detail
                    }
                } as APIError;
            }

            // The error data already has the correct structure, just pass it through
            throw errorData as APIError;
        }
        throw {
            detail: {
                error_type: ErrorType.RUNTIME_ERROR,
                message: 'An unexpected error occurred',
                detail: 'An unexpected error occurred'
            }
        } as APIError;
    }
};