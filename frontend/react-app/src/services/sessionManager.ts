import Cookies from 'js-cookie';
import { ExternalSessionData } from 'types/authentication/externalUserSessionData';

export const saveExternalSession = (sessionData: ExternalSessionData) => {
    Cookies.set('external_session_id', sessionData.session_id);
    Cookies.set('external_user_id', sessionData.user_id);
    // Store session settings for later use
    Cookies.set('session_settings', JSON.stringify(sessionData.session_settings));
    Cookies.set('custom_fields', JSON.stringify(sessionData.custom_fields));
    Cookies.set('expires_at', sessionData.expires_at);
};

export const clearExternalSession = () => {
    Cookies.remove('external_session_id');
    Cookies.remove('external_user_id');
    Cookies.remove('session_settings');
};

export const getExternalSessionId = (): string | undefined => {
    return Cookies.get('external_session_id');
};

export const getSessionSettings = () => {
    const settings = Cookies.get('session_settings');
    return settings ? JSON.parse(settings) : null;
};

export const getStoredSession = (): ExternalSessionData | null => {
    const sessionId = Cookies.get('external_session_id');
    const userId = Cookies.get('external_user_id');
    const settings = Cookies.get('session_settings');
    
    if (!sessionId || !userId || !settings) {
        return null;
    }

    return {
        session_id: sessionId,
        user_id: userId,
        session_settings: JSON.parse(settings),
        custom_fields: JSON.parse(Cookies.get('custom_fields') || '{}'),
        expires_at: Cookies.get('expires_at') || '',
        tenant_id: Cookies.get('tenant_id') || '',
        created_at: Cookies.get('created_at') || ''
    };
};
