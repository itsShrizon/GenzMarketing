import React, { useState, useRef } from 'react';
import { Mic, MicOff, Upload, X } from 'lucide-react';
import { chatService } from '../services/api';

interface VoiceInputProps {
  onTranscript: (transcript: string) => void;
  onClose: () => void;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript, onClose }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        const file = new File([blob], 'recording.wav', { type: 'audio/wav' });
        await processAudioFile(file);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Error accessing microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudioFile = async (file: File) => {
    setIsProcessing(true);
    try {
      const result = await chatService.speechToText(file);      if (result.status === 'success' && result.transcript) {
        onTranscript(result.transcript);
        onClose();
      } else {
        alert('Failed to transcribe audio. Please try again.');
      }
    } catch (error) {
      console.error('Error transcribing audio:', error);
      alert('Error transcribing audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      processAudioFile(file);
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };
  return (
    <div className="voice-input-container">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Voice Input</h3>
        <button
          onClick={onClose}
          className="p-1 rounded-full hover:bg-gray-200 transition-colors"
          title="Close"
        >
          <X size={20} />
        </button>
      </div>
      <div className="flex gap-2 items-center"><button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`p-3 rounded-full transition-colors ${
            isRecording
              ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
        >
          {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
        </button>

        <button
          onClick={triggerFileUpload}
          disabled={isProcessing}
          className={`p-3 rounded-full bg-green-500 hover:bg-green-600 text-white transition-colors ${
            isProcessing ? 'opacity-50 cursor-not-allowed' : ''
          }`}
          title="Upload Audio File"
        >
          <Upload size={20} />
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileUpload}
          className="hidden"
        />        {(isRecording || isProcessing) && (
          <span className="text-sm text-gray-600">
            {isRecording ? 'Recording...' : 'Processing...'}
          </span>
        )}
      </div>
    </div>
  );
};

export default VoiceInput;
