/**
 * File Upload Component
 * Handles image uploads with drag and drop support
 */

import React, { useState, useRef, useCallback } from 'react';
import type { FileUploadState } from '../types';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  uploadState: FileUploadState;
  accept?: string;
  maxSize?: number; // in MB
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  uploadState,
  accept = 'image/*',
  maxSize = 10, // 10MB default
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!file.type.startsWith('image/')) {
      return 'Please select an image file';
    }

    // Check file size
    if (file.size > maxSize * 1024 * 1024) {
      return `File size must be less than ${maxSize}MB`;
    }

    return null;
  };

  const handleFileSelect = useCallback((file: File) => {
    const error = validateFile(file);
    if (error) {
      // You might want to show this error in the parent component
      console.error(error);
      return;
    }

    onFileSelect(file);
  }, [onFileSelect, maxSize]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);

    const file = event.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleInputChange}
        className="hidden"
      />

      {/* Upload area */}
      <div
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
          isDragOver
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${uploadState.error ? 'border-red-300 bg-red-50' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        {uploadState.file ? (
          // File preview
          <div className="space-y-2">
            <div className="relative inline-block">
              <img
                src={uploadState.preview || ''}
                alt="Preview"
                className="max-h-32 max-w-full rounded"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onFileRemove();
                }}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
              >
                ×
              </button>
            </div>
            <p className="text-sm text-gray-600">{uploadState.file.name}</p>
          </div>
        ) : (
          // Upload prompt
          <div className="space-y-2">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div>
              <p className="text-sm text-gray-600">
                <span className="font-medium text-blue-600 hover:text-blue-500">
                  Click to upload
                </span>{' '}
                or drag and drop
              </p>
              <p className="text-xs text-gray-500">PNG, JPG, GIF up to {maxSize}MB</p>
            </div>
          </div>
        )}

        {/* Error message */}
        {uploadState.error && (
          <p className="text-sm text-red-600 mt-2">{uploadState.error}</p>
        )}

        {/* Loading state */}
        {uploadState.uploading && (
          <div className="mt-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-xs text-gray-500 mt-1">Uploading...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload; 