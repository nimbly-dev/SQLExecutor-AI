const getBaseURL = (): string => {
    const env = process.env.NODE_ENV; 
    if (env === 'development') {
      //http://localhost:5001
      //http://localhost:5000
      return 'http://localhost:5001'; 
    }
    // Placeholder for production (adjust later)
    return 'https://api.sqlexecutor.com'; 
  };
  
  export const BASE_URL = getBaseURL();
  