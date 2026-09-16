import { useState, useEffect, useRef, useCallback } from 'react';

export interface MicrophoneState {
  isActive: boolean;
  isLoading: boolean;
  error: string | null;
  volumeLevel: number; // 0..100
  audioWaveform: number[];
}

export function useMicrophone() {
  const [state, setState] = useState<MicrophoneState>({
    isActive: false,
    isLoading: false,
    error: null,
    volumeLevel: 0,
    audioWaveform: [],
  });

  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyzerRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);

  const startMicrophone = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioCtxRef.current = audioCtx;

      const source = audioCtx.createMediaStreamSource(stream);
      const analyzer = audioCtx.createAnalyser();
      analyzer.fftSize = 64;
      source.connect(analyzer);
      analyzerRef.current = analyzer;

      const dataArray = new Uint8Array(analyzer.frequencyBinCount);

      const updateAudio = () => {
        if (!analyzerRef.current) return;
        analyzerRef.current.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        const volume = Math.min(100, Math.round((avg / 128) * 100));

        const waveform = Array.from(dataArray.slice(0, 16)).map((v) => v / 255);

        setState((prev) => ({
          ...prev,
          volumeLevel: volume,
          audioWaveform: waveform,
        }));

        animFrameRef.current = requestAnimationFrame(updateAudio);
      };

      updateAudio();

      setState((prev) => ({
        ...prev,
        isActive: true,
        isLoading: false,
      }));
    } catch (err: any) {
      let errorMsg = 'Failed to access microphone.';
      if (err.name === 'NotAllowedError') {
        errorMsg = 'Microphone permission was denied.';
      }
      setState((prev) => ({
        ...prev,
        isActive: false,
        isLoading: false,
        error: errorMsg,
      }));
    }
  }, []);

  const stopMicrophone = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close();
      audioCtxRef.current = null;
    }
    analyzerRef.current = null;

    setState({
      isActive: false,
      isLoading: false,
      error: null,
      volumeLevel: 0,
      audioWaveform: [],
    });
  }, []);

  useEffect(() => {
    return () => {
      stopMicrophone();
    };
  }, [stopMicrophone]);

  return {
    state,
    startMicrophone,
    stopMicrophone,
  };
}
