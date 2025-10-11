import React, { useEffect, useRef } from 'react';

interface SimpleAnimationProps {
  type: 'circle' | 'square' | 'triangle' | 'text';
  color?: string;
  duration?: number;
  size?: number;
  text?: string;
}

const SimpleAnimation: React.FC<SimpleAnimationProps> = ({
  type,
  color = '#3B82F6',
  duration = 2000,
  size = 100,
  text = 'Animation'
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = size * 2;
    canvas.height = size * 2;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Animation variables
    const startTime = Date.now();
    let animationId: number;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Set color
      ctx.fillStyle = color;
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const currentSize = size * progress;

      switch (type) {
        case 'circle':
          ctx.beginPath();
          ctx.arc(centerX, centerY, currentSize, 0, 2 * Math.PI);
          ctx.fill();
          break;
          
        case 'square':
          ctx.fillRect(
            centerX - currentSize,
            centerY - currentSize,
            currentSize * 2,
            currentSize * 2
          );
          break;
          
        case 'triangle':
          ctx.beginPath();
          ctx.moveTo(centerX, centerY - currentSize);
          ctx.lineTo(centerX - currentSize, centerY + currentSize);
          ctx.lineTo(centerX + currentSize, centerY + currentSize);
          ctx.closePath();
          ctx.fill();
          break;
          
        case 'text':
          ctx.font = `${currentSize / 2}px Arial`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(text, centerX, centerY);
          break;
      }

      if (progress < 1) {
        animationId = requestAnimationFrame(animate);
      }
    };

    animate();

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [type, color, duration, size, text]);

  return (
    <div className="flex justify-center items-center p-4">
      <canvas
        ref={canvasRef}
        className="border border-gray-300 rounded-lg"
        style={{ width: size * 2, height: size * 2 }}
      />
    </div>
  );
};

export default SimpleAnimation; 