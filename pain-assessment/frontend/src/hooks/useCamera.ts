import { useState, useEffect, useRef, useCallback } from 'react';

export interface CameraState {
  isActive: boolean;
  isLoading: boolean;
  error: string | null;
  devices: MediaDeviceInfo[];
  selectedDeviceId: string;
  isMirrored: boolean;
  isRecording: boolean;
}

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [state, setState] = useState<CameraState>({
    isActive: false,
    isLoading: false,
    error: null,
    devices: [],
    selectedDeviceId: '',
    isMirrored: true,
    isRecording: false,
  });

  const getDevices = useCallback(async () => {
    try {
      const allDevices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = allDevices.filter((d) => d.kind === 'videoinput');
      setState((prev) => ({
        ...prev,
        devices: videoDevices,
        selectedDeviceId: prev.selectedDeviceId || videoDevices[0]?.deviceId || '',
      }));
    } catch (err) {
      console.warn('Could not enumerate video devices:', err);
    }
  }, []);

  const startCamera = useCallback(
    async (deviceId?: string) => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      try {
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
        }

        const constraints: MediaStreamConstraints = {
          video: {
            deviceId: deviceId ? { exact: deviceId } : undefined,
            width: { ideal: 1280 },
            height: { ideal: 720 },
            frameRate: { ideal: 30 },
          },
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }

        await getDevices();

        setState((prev) => ({
          ...prev,
          isActive: true,
          isLoading: false,
          selectedDeviceId: deviceId || prev.selectedDeviceId,
        }));
      } catch (err: any) {
        let errorMsg = 'Failed to access camera.';
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          errorMsg = 'Camera permission was denied. Please allow camera access in browser settings.';
        } else if (err.name === 'NotFoundError') {
          errorMsg = 'No camera device found on this system.';
        }
        setState((prev) => ({
          ...prev,
          isActive: false,
          isLoading: false,
          error: errorMsg,
        }));
      }
    },
    [getDevices]
  );

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setState((prev) => ({ ...prev, isActive: false, isRecording: false }));
  }, []);

  const toggleMirror = useCallback(() => {
    setState((prev) => ({ ...prev, isMirrored: !prev.isMirrored }));
  }, []);

  const captureFrameBase64 = useCallback((): string | null => {
    if (!videoRef.current || !state.isActive) return null;
    const video = videoRef.current;
    if (video.videoWidth === 0 || video.videoHeight === 0) return null;

    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
    }
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.85);
  }, [state.isActive]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return {
    videoRef,
    state,
    startCamera,
    stopCamera,
    toggleMirror,
    captureFrameBase64,
  };
}
