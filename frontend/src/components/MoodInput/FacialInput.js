import React, { useState } from "react";
import { Button, Box, CircularProgress } from "@mui/material";
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useNavigate } from "react-router-dom";
import axios from "axios";

const FacialInput = () => {
  const [imageFile, setImageFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  // Get user token from localStorage
  const user = JSON.parse(localStorage.getItem("user"));
  const token = user?.access;

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
    }
  };

  const handleSubmit = async () => {
    if (!imageFile) {
      alert("Please upload an image first.");
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('image', imageFile);

      // First, get the emotion from facial expression
      const emotionResponse = await fetch('http://localhost:8000/api/facial_emotion/', {
        method: 'POST',
        body: formData,
      });

      if (!emotionResponse.ok) {
        throw new Error('Failed to process image');
      }

      const emotionData = await emotionResponse.json();
      console.log("Emotion detected:", emotionData);

      // Then, get music recommendations based on the emotion
      const recommendationsResponse = await axios.post(
        "https://moodify-emotion-music-app.onrender.com/api/music_recommendation/",
        { emotion: emotionData.emotion.toLowerCase() },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const { recommendations } = recommendationsResponse.data;

      // Get current user profile to update
      const currentProfileResponse = await axios.get(
        "http://localhost:8000/users/user/profile/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const currentProfile = currentProfileResponse.data;
      
      // Prepare updated data
      const updatedMoods = [
        {
          emotion: emotionData.emotion,
          timestamp: new Date().toISOString()
        },
        ...(currentProfile.recent_moods || []).slice(0, 4) // Keep only the 5 most recent moods
      ];

      const updatedRecommendations = [
        ...recommendations.slice(0, 5),
        ...(currentProfile.recent_recommendations || []).slice(0, 4) // Keep only the 5 most recent recommendations
      ];

      // Update user profile with new mood and recommendations
      const updateResponse = await axios.put(
        "http://localhost:8000/users/user/profile/update/",
        {
          recent_moods: updatedMoods,
          recent_recommendations: updatedRecommendations,
          username: currentProfile.username,
          email: currentProfile.email
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      console.log("Profile update response:", updateResponse.data);

      // Navigate to results page with the recommendations
      navigate("/results", { 
        state: { 
          emotion: emotionData.emotion, 
          recommendations 
        } 
      });

    } catch (error) {
      console.error("Error processing image:", error);
      if (error.response) {
        console.error("Server response:", error.response.data);
      }
      alert("Error processing image. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2, alignItems: "center" }}>
      <input
        accept="image/*"
        style={{ display: "none" }}
        id="raised-button-file"
        type="file"
        onChange={handleFileUpload}
        disabled={isProcessing}
      />
      <label htmlFor="raised-button-file">
        <Button
          variant="contained"
          component="span"
          startIcon={<CloudUploadIcon />}
          disabled={isProcessing}
        >
          Upload Image
        </Button>
      </label>

      {imageFile && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1, alignItems: "center" }}>
          <img 
            src={URL.createObjectURL(imageFile)} 
            alt="Preview" 
            style={{ maxWidth: "300px", maxHeight: "300px", objectFit: "contain" }} 
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <>
                <CircularProgress size={24} sx={{ mr: 1 }} />
                Processing...
              </>
            ) : (
              "Analyze Emotion"
            )}
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default FacialInput;
