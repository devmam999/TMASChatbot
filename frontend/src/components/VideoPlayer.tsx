/**
 * Video Player Component for Manim Animations
 * Handles autoplay, error states, and loading states
 */

import React, { useRef, useEffect, useState } from 'react';

interface VideoPlayerProps {
  src: string;
  className?: string;
  autoplay?: boolean;
  muted?: boolean;
  loop?: boolean;
  controls?: boolean;
  onError?: (error: string) => void;
  onLoad?: () => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  src,
  className = '',
  autoplay = true,
  muted = true,
  loop = true,
  controls = false,
  onError,
  onLoad,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleLoadStart = () => {
      setIsLoading(true);
      setHasError(false);
    };

    const handleCanPlay = () => {
      setIsLoading(false);
      onLoad?.();
    };

    const handleError = (e: Event) => {
      setIsLoading(false);
      setHasError(true);
      setErrorMessage('Failed to load video');
      onError?.('Failed to load video');
      console.error('Video error:', e);
    };

    const handleLoadedData = () => {
      setIsLoading(false);
    };

    // Add event listeners
    video.addEventListener('loadstart', handleLoadStart);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('error', handleError);
    video.addEventListener('loadeddata', handleLoadedData);

    // Cleanup
    return () => {
      video.removeEventListener('loadstart', handleLoadStart);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('error', handleError);
      video.removeEventListener('loadeddata', handleLoadedData);
    };
  }, [onLoad, onError]);

  // Auto-play when video is ready
  useEffect(() => {
    const video = videoRef.current;
    if (video && autoplay && !isLoading && !hasError) {
      video.play().catch((error) => {
        console.warn('Autoplay failed:', error);
        // Autoplay might fail due to browser policies
        // This is normal and not a real error
      });
    }
  }, [autoplay, isLoading, hasError]);

  if (hasError) {
    return (
      <div className={`bg-gray-100 rounded-lg p-4 text-center ${className}`}>
        <div className="text-gray-500 mb-2">
          <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <p className="text-sm text-gray-600">{errorMessage}</p>
        <button
          onClick={() => {
            setHasError(false);
            setErrorMessage('');
            if (videoRef.current) {
              videoRef.current.load();
            }
          }}
          className="mt-2 text-blue-500 hover:text-blue-700 text-sm"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading animation...</p>
          </div>
        </div>
      )}
      
      <video
        ref={videoRef}
        className={`w-full rounded-lg ${isLoading ? 'opacity-0' : 'opacity-100'}`}
        autoPlay={autoplay}
        muted={muted}
        loop={loop}
        controls={controls}
        playsInline
        preload="metadata"
      >
        <source src={src} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default VideoPlayer; 