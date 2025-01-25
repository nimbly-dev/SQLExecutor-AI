export const isExpired = (expiryDate: string): boolean => {
    const expiry = new Date(expiryDate);
    const now = new Date();
    return now > expiry;
};
