import axios from 'axios';

const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1',
    headers: {'Content-Type': 'application/json'},
});

export const checkIdentifierStatus = async (identifier) => {
    const {data} = await apiClient.post('/auth/status/', {identifier});
    return data;
};
export const requestOTP = async (phone_number) => {
    const {data} = await apiClient.post('/auth/otp/request/', {phone_number});
    return data;
};
export const verifyOtpAndLogin = async (payload) => {
    const {data} = await apiClient.post('/auth/otp/verify/', payload);
    return data;
}
export const loginWithPassword = async (payload) => {
    const {data} = await apiClient.post('/auth/login/', payload);
    return data;
}
export const getUserProfile = async (payload) => {
    const {data} = await apiClient.post('/auth/login/', payload);
    return data;
}
export const updateUserProfile = async (payload) => {
    const {data} = await apiClient.post('/auth/login/', payload);
    return data;
}
export const setPassword = async (payload) => {
    const {data} = await apiClient.post('/auth/login/', payload);
    return data;
}
export const changePassword = async (payload) => {
    const {data} = await apiClient.post('/auth/login/', payload);
    return data;
}
export default apiClient;
