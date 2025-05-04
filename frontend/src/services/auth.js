import axios from "axios";

const API_URL = "http://localhost:8000";

export const register = async (username, password, email) => {
  try {
    const response = await axios.post(`${API_URL}/users/register/`, {
      username,
      password,
      email,
    });
    
    console.log("Registration response:", response.data);
    
    if (response.data.tokens) {
      // Store user data with the correct structure
      const userData = {
        username: response.data.user.username,
        email: response.data.user.email,
        access: response.data.tokens.access,
        refresh: response.data.tokens.refresh
      };
      
      console.log("Storing user data in localStorage:", userData);
      localStorage.setItem("user", JSON.stringify(userData));
    }
    
    return response.data;
  } catch (error) {
    console.error("Registration error:", error);
    throw error;
  }
};

export const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_URL}/users/login/`, {
      username,
      password,
    });
    
    console.log("Login response:", response.data);
    
    if (response.data.tokens) {
      // Store user data with the correct structure
      const userData = {
        username: response.data.user.username,
        email: response.data.user.email,
        access: response.data.tokens.access,
        refresh: response.data.tokens.refresh
      };
      
      console.log("Storing user data in localStorage:", userData);
      localStorage.setItem("user", JSON.stringify(userData));
    }
    
    return response.data;
  } catch (error) {
    console.error("Login error:", error);
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem("user");
};