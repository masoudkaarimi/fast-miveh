import {clsx} from "clsx";
import {twMerge} from "tailwind-merge"

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

/**
 * Extracts a user-friendly error message from an axios error object.
 * Handles different error structures from Django Rest Framework.
 * @param {object} error The error object from axios.
 * @param fallbackMessage
 * @returns {string} A displayable error message.
 */
export function getErrorMessage(error, fallbackMessage = "An unexpected error occurred. Please try again.") {
    const errorData = error?.response?.data;

    if (!errorData) {
        return fallbackMessage;
    }

    // Handles { "detail": "Error message" }
    if (typeof errorData.detail === 'string') {
        return errorData.detail;
    }

    // Handles { "non_field_errors": ["Error message"] }
    if (Array.isArray(errorData.non_field_errors) && errorData.non_field_errors.length > 0) {
        return errorData.non_field_errors[0];
    }

    // Handles ["Error message"]
    if (Array.isArray(errorData) && errorData.length > 0 && typeof errorData[0] === 'string') {
        return errorData[0];
    }

    // Handles { "field_name": ["Error message for this field"] }
    if (typeof errorData === 'object' && !Array.isArray(errorData)) {
        const firstErrorKey = Object.keys(errorData)[0];
        if (firstErrorKey && Array.isArray(errorData[firstErrorKey]) && errorData[firstErrorKey].length > 0) {
            return errorData[firstErrorKey][0];
        }
    }

    return fallbackMessage;
}


/**
 * Extracts a success message from an axios response object.
 * Looks for a "detail" or "message" key.
 * @param {object} response The successful response object from axios.
 * @param {string} fallbackMessage A default message to use if none is found.
 * @returns {string} A displayable success message.
 */
export function getSuccessMessage(response, fallbackMessage = "Operation successful!") {
    const data = response?.data;

    // Check for a specific message from the backend first
    if (data && typeof data.detail === 'string') {
        return data.detail;
    }
    if (data && typeof data.message === 'string') {
        return data.message;
    }

    // If no message is found, return the fallback
    return fallbackMessage;
}

// --- Format Iranian phone numbers ---
export function formatPhoneNumber(identifier) {
    // Regular expression to match numbers starting with "09" and having 11 digits
    const iranianMobileRegex = /^09\d{9}$/;

    // This condition is the key
    if (iranianMobileRegex.test(identifier)) {
        // This block only runs if the number is like "0912..."
        return `+98${identifier.substring(1)}`;
    }

    // If the condition is false, the original input is returned
    return identifier;
}

// --- Determine the type of identifier (email or phone number) ---
export function getIdentifierType(identifier) {
    // Standard regex for email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Regex for an 11-digit Iranian mobile number starting with 09
    const iranianMobileRegex = /^09\d{9}$/;

    if (emailRegex.test(identifier)) {
        return 'email';
    }

    if (iranianMobileRegex.test(identifier)) {
        return 'phone_number';
    }

    // Return 'invalid' if it's neither
    return 'invalid';
}

// --- Join URL parts with proper formatting ---
export function joinUrlParts(base, path) {
    // Remove trailing slash from the base URL, if it exists
    const cleanedBase = base.replace(/\/+$/, '');
    // Remove leading slash from the path, if it exists
    const cleanedPath = path.replace(/^\/+/, '');
    // Join them with a single slash
    return `${cleanedBase}/${cleanedPath}`;
}