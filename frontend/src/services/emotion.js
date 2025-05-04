import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

// Get the user token from localStorage
const getToken = () => {
  const user = JSON.parse(localStorage.getItem("user"));
  return user?.access;
};

// Create axios instance with authorization header
const createAuthAxios = () => {
  const token = getToken();
  return axios.create({
    baseURL: API_URL,
    headers: {
      Authorization: token ? `Bearer ${token}` : "",
      "Content-Type": "application/json",
    },
  });
};

export const detectTextEmotion = async (text) => {
  try {
    const authAxios = createAuthAxios();
    console.log("Making request to:", `${API_URL}/api/text_emotion/`);
    const response = await authAxios.post("/api/text_emotion/", { text });
    return response.data;
  } catch (error) {
    console.error("Text emotion detection error:", error);
    if (error.response) {
      console.error("Error response:", error.response.data);
      console.error("Error status:", error.response.status);
    }
    throw error;
  }
};

export const detectSpeechEmotion = async (audioFile) => {
  try {
    const authAxios = createAuthAxios();
    const formData = new FormData();
    formData.append("audio_file", audioFile);
    
    console.log("Making request to:", `${API_URL}/api/speech_emotion/`);
    const response = await authAxios.post("/api/speech_emotion/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    
    return response.data;
  } catch (error) {
    console.error("Speech emotion detection error:", error);
    if (error.response) {
      console.error("Error response:", error.response.data);
      console.error("Error status:", error.response.status);
    }
    throw error;
  }
};

export const detectFacialEmotion = async (imageFile) => {
  try {
    const authAxios = createAuthAxios();
    const formData = new FormData();
    formData.append("image", imageFile);
    
    const response = await authAxios.post("/api/facial_emotion/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    
    return response.data;
  } catch (error) {
    console.error("Facial emotion detection error:", error);
    if (error.response) {
      console.error("Error response:", error.response.data);
      console.error("Error status:", error.response.status);
    }
    throw error;
  }
};
