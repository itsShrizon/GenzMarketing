import React, { useState } from 'react';
import { Video, Loader, X } from 'lucide-react';
import { chatService } from '../services/api';

interface AvatarGeneratorProps {
  text: string;
  onClose: () => void;
}

const AvatarGenerator = ({ text, onClose }: AvatarGeneratorProps) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const generateAvatar = async () => {    if (!text.trim()) {
      alert('Please provide text to generate avatar video.');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setVideoUrl(null);

    try {
      console.log('Starting avatar generation...'); // Debug log
      const result = await chatService.createAvatar(text);
      console.log('Avatar generation result:', result); // Debug log
      
      if (result.status === 'success' && result.video_url) {
        setVideoUrl(result.video_url);
      } else {
        setError(result.error || 'Failed to generate avatar video');
      }
    } catch (error: any) {
      console.error('Error generating avatar:', error);
      
      // Better error handling for timeout and network errors
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        setError('Avatar generation is taking longer than expected. This may be normal for longer text. Please wait and try again if it fails.');
      } else if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.response?.status === 500) {
        setError('Server error occurred. Please try again.');
      } else {
        setError('Error generating avatar video. Please try again.');
      }
    } finally {
      setIsGenerating(false);
    }
  };
  return (
    <div className="avatar-generator">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Avatar Generator</h3>
        <button
          onClick={onClose}
          className="p-1 rounded-full hover:bg-gray-200 transition-colors"
          title="Close"
        >
          <X size={20} />
        </button>
      </div>      <div className="mb-3">
        <p className="text-sm text-gray-600 mb-2">Generate a talking avatar video from the last bot response:</p>
        <div className="p-3 bg-gray-100 rounded-lg text-sm max-h-20 overflow-y-auto">
          {text || 'No text available for avatar generation'}
        </div>
      </div>

      <button
        onClick={generateAvatar}
        disabled={isGenerating || !text.trim()}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2 ${
          isGenerating || !text.trim()
            ? 'bg-gray-300 cursor-not-allowed'
            : 'bg-purple-500 hover:bg-purple-600 text-white'
        }`}
        aria-label="Generate talking avatar video"
      >
        {isGenerating ? (
          <>
            {typeof Loader === 'function' ? <Loader className="animate-spin" size={16} aria-hidden="true" /> : <span role="img" aria-label="Loading" className="animate-spin">⏳</span>}
            Generating Avatar...
          </>
        ) : (
          <>
            {typeof Video === 'function' ? <Video size={16} aria-hidden="true" /> : <span role="img" aria-label="Video">🎥</span>}
            Create Talking Avatar
          </>
        )}
      </button>

      {error && (
        <div className="mt-2 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700" role="alert">
          <span className="font-semibold">Error:</span> {error}
        </div>
      )}

      {videoUrl && (
        <div className="mt-4">
          <video
            controls
            className="w-full max-w-md rounded-lg shadow-lg"
            src={videoUrl}
            aria-label="Generated avatar video"
            onLoadStart={() => setIsGenerating(true)}
            onLoadedData={() => setIsGenerating(false)}
          >
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
};

export default AvatarGenerator;
