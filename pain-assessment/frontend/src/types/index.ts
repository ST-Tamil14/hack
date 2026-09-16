// Patient & Clinical Profile Types
export interface Patient {
  id: string;
  patient_id: string;
  full_name: string;
  age: number;
  gender: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  communication_ability: 'verbal' | 'non-verbal' | 'intubated' | 'cognitive_impairment';
  mobility_status: 'full' | 'restricted' | 'bedridden' | 'assisted';
  sedation_status: 'alert' | 'mild_sedation' | 'moderate_sedation' | 'heavy_sedation';
  facial_movement_limitation: boolean;
  speech_limitation: boolean;
  medical_notes?: string;
  created_at: string;
  last_assessment_at?: string;
  baseline?: PersonalizedBaseline;
}

export interface PersonalizedBaseline {
  baseline_heart_rate: number;
  baseline_hrv_rmssd: number;
  baseline_respiration_rate: number;
  baseline_eda_gsr: number;
  baseline_facial_tension: number;
  baseline_voice_pitch: number;
}

// Session Metadata
export interface AssessmentSession {
  id: string;
  patient_id: string;
  patient_name?: string;
  start_time: string;
  end_time?: string;
  status: 'active' | 'completed' | 'paused' | 'aborted';
  overall_pain_score?: number;
  ai_confidence?: number;
  signal_quality_score?: number;
  flagged_alerts_count?: number;
  clinician_notes?: string;
}

// Modality Signal Data Types
export interface FacialAnalysisData {
  face_detected: boolean;
  face_count: number;
  confidence: number;
  brow_movement: number; // 0..1
  eye_narrowing: number; // 0..1
  nose_wrinkling: number; // 0..1
  mouth_movement: number; // 0..1
  facial_tension: number; // 0..1
  blink_frequency_bpm: number;
  head_movement_index: number;
  facial_pain_score: number; // 0..100
  quality_weight: number;
}

export interface PhysiologicalData {
  heart_rate_bpm: number;
  hrv_rmssd_ms: number;
  respiratory_rate_bpm: number;
  eda_microsiemens: number;
  skin_temperature_c: number;
  spo2_percent: number;
  systolic_bp_mmhg: number;
  diastolic_bp_mmhg: number;
  pulse_waveform_sample: number[];
  signal_quality_score: number; // 0..1
  is_camera_estimate: boolean;
  is_reference_sensor: boolean;
}

export interface BehavioralData {
  restlessness_level: 'none' | 'mild' | 'moderate' | 'high';
  guarding_detected: boolean;
  unusual_stillness: boolean;
  posture_abnormality_score: number; // 0..1
  mobility_reduction_score: number; // 0..1
  agitation_score: number; // 0..1
  behavioral_pain_score: number; // 0..100
  confidence: number;
}

export interface VoiceAnalysisData {
  microphone_active: boolean;
  pitch_hz: number;
  loudness_db: number;
  jitter_percent: number;
  shimmer_percent: number;
  hnr_db: number;
  vocal_distress_detected: boolean;
  crying_detected: boolean;
  moaning_detected: boolean;
  groaning_detected: boolean;
  sighing_detected: boolean;
  audio_pain_score: number; // 0..100
  confidence: number;
}

export interface SensorDevice {
  id: string;
  name: string;
  type: 'ecg' | 'pulse_oximeter' | 'bp_monitor' | 'thermometer' | 'respiratory_belt';
  status: 'connected' | 'disconnected' | 'pairing';
  battery_percent?: number;
  latest_reading?: string;
  last_updated_at?: string;
}

// Multimodal Fusion Assessment Result
export interface MultimodalAssessmentResult {
  overall_pain_score: number; // 0..100
  pain_level: 'no_pain' | 'low' | 'moderate' | 'high';
  ai_confidence: number; // 0..100
  signal_quality: number; // 0..100
  facial_contribution: number;
  physiological_contribution: number;
  behavioral_contribution: number;
  voice_contribution: number;
  contributing_factors: string[];
  disclaimer: string;
  needs_clinical_review: boolean;
  timestamp: string;
}

// Clinical Alert Notification
export interface ClinicalAlert {
  id: string;
  patient_id: string;
  patient_name: string;
  session_id?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: string;
  acknowledged: boolean;
  acknowledged_by?: string;
}

// User / Auth State
export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'clinician' | 'researcher' | 'patient';
}
