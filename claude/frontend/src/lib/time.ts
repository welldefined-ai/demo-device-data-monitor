/**
 * Time formatting utilities to ensure consistent local timezone display
 */

/**
 * Format timestamp to local date and time
 */
export const formatDateTime = (timestamp: string | Date): string => {
  return new Date(timestamp).toLocaleString();
};

/**
 * Format timestamp to local time only
 */
export const formatTime = (timestamp: string | Date): string => {
  return new Date(timestamp).toLocaleTimeString();
};

/**
 * Format timestamp to local date only
 */
export const formatDate = (timestamp: string | Date): string => {
  return new Date(timestamp).toLocaleDateString();
};
