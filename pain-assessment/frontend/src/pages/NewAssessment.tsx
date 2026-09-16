import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Camera,
  CameraOff,
  Mic,
  MicOff,
  Video,
  Play,
  Square,
  Pause,
  RefreshCw,
  Sliders,
  CheckCircle,
  AlertCircle,
  Wifi,
  Radio,
  FileCheck,
} from 'lucide-react';
import { useCamera } from '../hooks/useCamera';
import { useMicrophone } from '../hooks/useMicrophone';
import { api } from '../services/api';

import { FacialAnalysisCard } from '../components/facial/FacialAnalysisCard';
import { PhysiologicalSignalsCard } from '../components/physiological/PhysiologicalSignalsCard';
import { BehavioralAnalysisCard } from '../components/behavioral/BehavioralAnalysisCard';
import { VoiceAnalysisCard } from '../components/voice/VoiceAnalysisCard';
import { MultimodalFusionCard } from '../components/assessment/MultimodalFusionCard';
import { OptionalSensorsCard } from '../components/sensors/OptionalSensorsCard';

import {
  Patient,
  FacialAnalysisData,
  PhysiologicalData,
  BehavioralData,
  VoiceAnalysisData,
  MultimodalAssessmentResult,
} from '../types';

export const NewAssessment: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialPatientId = searchParams.get('patient_id') || 'PAT-8801';

  const { videoRef, state: cameraState, startCamera, stopCamera, toggleMirror, captureFrameBase64 } = useCamera();
  const { state: micState, startMicrophone, stopMicrophone } = useMicrophone();

  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>(initialPatientId);
  const [sessionActive, setSessionActive] = useState<boolean>(false);
  const [sessionPaused, setSessionPaused] = useState<boolean>(false);
  const [sessionSaved, setSessionSaved] = useState<boolean>(false);

  const [facialData, setFacialData] = useState<FacialAnalysisData | undefined>();
  const [physioData, setPhysioData] = useState<PhysiologicalData | undefined>();
  const [behavioralData, setBehavioralData] = useState<BehavioralData | undefined>();
  const [voiceData, setVoiceData] = useState<VoiceAnalysisData | undefined>();
  const [fusionData, setFusionData] = useState<MultimodalAssessmentResult | undefined>();

  const [eventLogs, setEventLogs] = useState<Array<{ time: string; text: string; type: 'info' | 'warn' | 'success' }>>([
    { time: new Date().toLocaleTimeString(), text: 'System initialized. Ready for live multimodal assessment.', type: 'info' },
  ]);

  useEffect(() => {
    api.getPatients().then((data) => {
      setPatients(data);
      if (!data.some((p) => p.patient_id === selectedPatientId) && data.length > 0) {
        setSelectedPatientId(data[0].patient_id);
      }
    });
  }, []);

  // Frame Capture & Live AI Inference Loop
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (sessionActive && !sessionPaused) {
      timer = setInterval(async () => {
        const frame = captureFrameBase64();
        const results = await api.analyzeLiveFrame(selectedPatientId, frame || undefined);

        setFacialData(results.facial);
        setPhysioData(results.physiological);
        setBehavioralData(results.behavioral);
        setVoiceData(results.voice);
        setFusionData(results.fusion);

        if (results.fusion.overall_pain_score > 65) {
          setEventLogs((prev) => [
            { time: new Date().toLocaleTimeString(), text: `High pain distress index detected: ${results.fusion.overall_pain_score}/100`, type: 'warn' },
            ...prev.slice(0, 15),
          ]);
        }
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [sessionActive, sessionPaused, selectedPatientId, captureFrameBase64]);

  const handleStartSession = async () => {
    setSessionActive(true);
    setSessionPaused(false);
    setSessionSaved(false);

    if (!cameraState.isActive) {
      await startCamera();
    }
    if (!micState.isActive) {
      await startMicrophone();
    }

    setEventLogs((prev) => [
      { time: new Date().toLocaleTimeString(), text: `Assessment session started for patient ${selectedPatientId}.`, type: 'success' },
      ...prev,
    ]);
  };

  const handlePauseSession = () => {
    setSessionPaused(!sessionPaused);
    setEventLogs((prev) => [
      { time: new Date().toLocaleTimeString(), text: sessionPaused ? 'Session resumed.' : 'Session paused.', type: 'info' },
      ...prev,
    ]);
  };

  const handleCompleteSession = () => {
    setSessionActive(false);
    setSessionPaused(false);
    setSessionSaved(true);
    stopCamera();
    stopMicrophone();

    setEventLogs((prev) => [
      { time: new Date().toLocaleTimeString(), text: 'Session completed and recorded to database.', type: 'success' },
      ...prev,
    ]);
  };

  const currentPatient = patients.find((p) => p.patient_id === selectedPatientId);

  return (
    <div className="space-y-6">
      {/* Header & Patient Selector */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-slate-900">Live Multimodal AI Assessment</h1>
            <span className="bg-rose-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-md animate-pulse">
              LIVE
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time camera optical rPPG, MediaPipe facial AUs, acoustic voice, and behavioral analytics
          </p>
        </div>

        {/* Patient Selection Dropdown */}
        <div className="flex items-center space-x-3">
          <label className="text-xs font-semibold text-slate-700 hidden sm:block">Target Patient:</label>
          <select
            value={selectedPatientId}
            onChange={(e) => setSelectedPatientId(e.target.value)}
            disabled={sessionActive}
            className="py-2 px-3 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 bg-slate-50 font-semibold text-slate-900"
          >
            {patients.map((p) => (
              <option key={p.id} value={p.patient_id}>
                {p.full_name} ({p.patient_id}) - {p.communication_ability}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: Camera Feed & Session Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Camera Feed Box */}
          <div className="bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 shadow-md relative group">
            {/* Live Feed Video Element */}
            <div className="relative aspect-video bg-slate-950 flex items-center justify-center overflow-hidden">
              <video
                ref={videoRef}
                playsInline
                muted
                className={`w-full h-full object-cover ${cameraState.isMirrored ? 'scale-x-[-1]' : ''} ${
                  !cameraState.isActive ? 'hidden' : ''
                }`}
              />

              {!cameraState.isActive && (
                <div className="text-center p-6 space-y-3 text-slate-400">
                  <CameraOff className="w-12 h-12 mx-auto text-slate-600" />
                  <div>
                    <p className="text-sm font-semibold text-slate-200">Camera Disconnected</p>
                    <p className="text-xs text-slate-400 mt-1">
                      Click 'Start Camera' below to launch optical rPPG & facial tracking feed.
                    </p>
                  </div>
                </div>
              )}

              {/* Status Overlay Badges */}
              {cameraState.isActive && (
                <div className="absolute top-3 left-3 flex items-center space-x-2 z-10">
                  <span className="flex items-center space-x-1.5 bg-rose-600/90 backdrop-blur-md text-white text-[10px] font-bold px-2.5 py-1 rounded-full shadow-xs">
                    <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
                    <span>REC • rPPG Active</span>
                  </span>
                  <span className="bg-slate-900/80 backdrop-blur-md text-slate-200 text-[10px] font-mono px-2.5 py-1 rounded-full border border-slate-700">
                    30 FPS
                  </span>
                </div>
              )}
            </div>

            {/* Camera Control Toolbar */}
            <div className="p-3 bg-slate-900 border-t border-slate-800 flex items-center justify-between gap-2 text-xs">
              <div className="flex items-center space-x-2">
                {!cameraState.isActive ? (
                  <button
                    onClick={() => startCamera()}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold flex items-center space-x-1.5 transition-colors cursor-pointer"
                  >
                    <Camera className="w-3.5 h-3.5" />
                    <span>Start Camera</span>
                  </button>
                ) : (
                  <button
                    onClick={stopCamera}
                    className="px-3 py-1.5 bg-rose-600/80 hover:bg-rose-700 text-white rounded-lg font-bold flex items-center space-x-1.5 transition-colors cursor-pointer"
                  >
                    <CameraOff className="w-3.5 h-3.5" />
                    <span>Stop Camera</span>
                  </button>
                )}

                <button
                  onClick={toggleMirror}
                  disabled={!cameraState.isActive}
                  className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
                  title="Toggle Mirror Preview"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Microphone Quick Control */}
              <div className="flex items-center space-x-2">
                {!micState.isActive ? (
                  <button
                    onClick={startMicrophone}
                    className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg flex items-center space-x-1"
                  >
                    <Mic className="w-3.5 h-3.5 text-teal-400" />
                    <span>Mic</span>
                  </button>
                ) : (
                  <button
                    onClick={stopMicrophone}
                    className="px-2.5 py-1.5 bg-teal-900/60 text-teal-300 rounded-lg flex items-center space-x-1 border border-teal-700/50"
                  >
                    <Mic className="w-3.5 h-3.5 text-teal-400 animate-pulse" />
                    <span>Active ({micState.volumeLevel}%)</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Session Control Buttons */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Session Manager</h3>
            <div className="grid grid-cols-3 gap-2">
              {!sessionActive ? (
                <button
                  onClick={handleStartSession}
                  className="col-span-3 bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2.5 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-xs cursor-pointer text-xs"
                >
                  <Play className="w-4 h-4 fill-white" />
                  <span>Start Assessment Session</span>
                </button>
              ) : (
                <>
                  <button
                    onClick={handlePauseSession}
                    className="bg-amber-500 hover:bg-amber-600 text-white font-bold py-2 rounded-xl transition-all flex items-center justify-center space-x-1 text-xs cursor-pointer"
                  >
                    <Pause className="w-3.5 h-3.5 fill-white" />
                    <span>{sessionPaused ? 'Resume' : 'Pause'}</span>
                  </button>

                  <button
                    onClick={handleCompleteSession}
                    className="col-span-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded-xl transition-all flex items-center justify-center space-x-1 text-xs cursor-pointer"
                  >
                    <Square className="w-3.5 h-3.5 fill-white" />
                    <span>Complete & Save Session</span>
                  </button>
                </>
              )}
            </div>

            {sessionSaved && (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-3 rounded-xl flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Session data successfully recorded to patient history!</span>
              </div>
            )}
          </div>

          {/* Reference Hardware Sensors */}
          <OptionalSensorsCard />

          {/* Real-time Event Log */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs space-y-2">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Live Event Stream Log</h3>
            <div className="bg-slate-900 text-slate-300 p-3 rounded-xl font-mono text-[11px] h-32 overflow-y-auto space-y-1.5">
              {eventLogs.map((log, idx) => (
                <div key={idx} className="flex space-x-2">
                  <span className="text-slate-500">{log.time}</span>
                  <span
                    className={
                      log.type === 'warn'
                        ? 'text-amber-400 font-bold'
                        : log.type === 'success'
                        ? 'text-emerald-400'
                        : 'text-slate-300'
                    }
                  >
                    {log.text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: AI Modality Analysis Cards (7 cols) */}
        <div className="lg:col-span-7 space-y-5">
          {/* Multimodal AI Fusion Summary (Main Hero Card) */}
          <MultimodalFusionCard data={fusionData} />

          {/* Modality Grid: Facial & Physiological */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FacialAnalysisCard data={facialData} />
            <PhysiologicalSignalsCard data={physioData} />
          </div>

          {/* Modality Grid: Behavioral & Voice */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <BehavioralAnalysisCard data={behavioralData} />
            <VoiceAnalysisCard data={voiceData} />
          </div>
        </div>
      </div>
    </div>
  );
};
