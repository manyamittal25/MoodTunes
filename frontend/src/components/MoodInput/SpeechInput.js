import React, { useState, useRef } from "react";
import { Box, Button, CircularProgress, Typography } from "@mui/material";
import MicIcon from "@mui/icons-material/Mic";
import StopIcon from "@mui/icons-material/Stop";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { useNavigate } from "react-router-dom";
import { detectSpeechEmotion } from "../../services/emotion";

const SpeechInput = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioFile, setAudioFile] = useState(null);
  const [error, setError] = useState("");
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const navigate = useNavigate();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          sampleSize: 16,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      // Use WebM format which is well-supported
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 16000
      });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        try {
          // Create a WebM blob
          const webmBlob = new Blob(chunksRef.current, { type: "audio/webm" });
          
          // Convert WebM to WAV using AudioContext
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const arrayBuffer = await webmBlob.arrayBuffer();
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          
          // Create WAV file
          const wavBlob = await audioBufferToWav(audioBuffer);
          const audioFile = new File([wavBlob], "recording.wav", { type: "audio/wav" });
          
          setAudioFile(audioFile);
          stream.getTracks().forEach(track => track.stop());
          setError("");
        } catch (error) {
          console.error("Error converting audio:", error);
          setError("Error processing audio. Please try again.");
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      setError("Error accessing microphone. Please ensure you have granted microphone permissions.");
    }
  };

  // Helper function to convert AudioBuffer to WAV
  const audioBufferToWav = (buffer) => {
    const numChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;
    
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    
    const wav = new ArrayBuffer(44 + buffer.length * blockAlign);
    const view = new DataView(wav);
    
    // Write WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + buffer.length * blockAlign, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    writeString(view, 36, 'data');
    view.setUint32(40, buffer.length * blockAlign, true);
    
    // Write audio data
    const data = new Float32Array(buffer.length);
    const channel = buffer.getChannelData(0);
    for (let i = 0; i < buffer.length; i++) {
      data[i] = channel[i];
    }
    
    let offset = 44;
    for (let i = 0; i < data.length; i++) {
      const sample = Math.max(-1, Math.min(1, data[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
    
    return new Blob([wav], { type: 'audio/wav' });
  };

  // Helper function to write strings to DataView
  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check if file is a supported audio format
      const supportedFormats = ['audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac', 'audio/m4a', 'audio/webm'];
      if (!supportedFormats.includes(file.type)) {
        setError("Unsupported audio format. Please upload a WAV, MP3, OGG, FLAC, M4A, or WEBM file.");
        return;
      }
      setAudioFile(file);
      setError("");
    }
  };

  const handleSubmit = async () => {
    if (!audioFile) {
      setError("Please record or upload an audio file first.");
      return;
    }

    setIsProcessing(true);
    setError("");

    try {
      const response = await detectSpeechEmotion(audioFile);
      console.log("Emotion detected:", response);

      // Navigate to results page with the emotion and recommendations
      navigate("/results", { 
        state: { 
          emotion: response.emotion, 
          recommendations: response.recommendations 
        } 
      });

    } catch (error) {
      console.error("Error processing audio:", error);
      setError(error.response?.data?.error || "Error processing audio. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2, alignItems: "center", p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Record your voice or upload an audio file:
      </Typography>
      
      <Box sx={{ display: "flex", gap: 2 }}>
        <Button
          variant="contained"
          color={isRecording ? "error" : "primary"}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          startIcon={isRecording ? <StopIcon /> : <MicIcon />}
        >
          {isRecording ? "Stop Recording" : "Start Recording"}
        </Button>

        <input
          accept="audio/*"
          style={{ display: "none" }}
          id="audio-file-input"
          type="file"
          onChange={handleFileUpload}
          disabled={isProcessing}
        />
        <label htmlFor="audio-file-input">
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            disabled={isProcessing}
          >
            Upload Audio
          </Button>
        </label>
      </Box>

      {error && (
        <Typography color="error" sx={{ mt: 1 }}>
          {error}
        </Typography>
      )}

      {audioFile && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1, alignItems: "center" }}>
          <audio controls style={{ width: "300px" }}>
            <source src={URL.createObjectURL(audioFile)} type={audioFile.type} />
            Your browser does not support the audio element.
          </audio>
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

export default SpeechInput;
