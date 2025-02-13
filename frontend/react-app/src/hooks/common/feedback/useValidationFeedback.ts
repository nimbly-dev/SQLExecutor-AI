import { useState, useCallback } from 'react';

export type AlertSeverity = 'error' | 'info' | 'success' | 'warning';

interface FeedbackState {
  message: string;
  type: AlertSeverity;
}

export function useValidationFeedback() {
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);

  const showFeedback = useCallback((message: string, type: AlertSeverity) => {
    setFeedback({ message, type });
  }, []);

  const clearFeedback = useCallback(() => {
    setFeedback(null);
  }, []);

  return { feedback, showFeedback, clearFeedback };
}
