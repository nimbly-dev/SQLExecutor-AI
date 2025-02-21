export const sleep = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms));

export const debounceAsync = <T extends (...args: any[]) => Promise<any>>(
  fn: T,
  delay: number
): T => {
  let timeoutId: NodeJS.Timeout;
  let lastCall = 0;

  return ((...args: Parameters<T>) => {
    return new Promise<ReturnType<T>>(async (resolve, reject) => {
      const now = Date.now();
      const timeSinceLastCall = now - lastCall;

      clearTimeout(timeoutId);

      if (timeSinceLastCall < delay) {
        await sleep(delay - timeSinceLastCall);
      }

      try {
        lastCall = Date.now();
        const result = await fn(...args);
        resolve(result);
      } catch (error) {
        reject(error);
      }
    });
  }) as T;
};
