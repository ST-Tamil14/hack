import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { User, Activity, Heart, Shield, FileText, Video, ArrowLeft, Sliders, CheckCircle } from 'lucide-react';
import { api } from '../services/api';
import { Patient } from '../types';

export const PatientProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [patient, setPatient] = useState<Patient | null>(null);

  useEffect(() => {
    if (id) {
      api.getPatientById(id).then(setPatient);
    }
  }, [id]);

  if (!patient) {
    return (
      <div className="p-8 text-center text-slate-500">
        Loading patient profile...
      </div>
    );
  }

  const baseline = patient.baseline || {
    baseline_heart_rate: 72,
    baseline_hrv_rmssd: 45,
    baseline_respiration_rate: 15,
    baseline_eda_gsr: 2.2,
    baseline_facial_tension: 0.12,
    baseline_voice_pitch: 185,
  };

  return (
    <div className="space-y-6">
      {/* Back Button & Header */}
      <div>
        <Link to="/patients" className="inline-flex items-center space-x-1.5 text-xs text-slate-500 hover:text-cyan-600 mb-3 font-medium">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Patient Roster</span>
        </Link>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-cyan-50 border border-cyan-200 flex items-center justify-center text-cyan-700 font-bold text-xl">
              {patient.full_name.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold text-slate-900">{patient.full_name}</h1>
                <span className="font-mono text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-semibold">
                  {patient.patient_id}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {patient.age} yrs • <span className="capitalize">{patient.gender}</span> • Registered {new Date(patient.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          <Link
            to={`/assessment/new?patient_id=${patient.patient_id}`}
            className="px-4 py-2.5 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 rounded-xl transition-all shadow-xs flex items-center space-x-2 w-max"
          >
            <Video className="w-4 h-4" />
            <span>Start Assessment for {patient.full_name.split(' ')[0]}</span>
          </Link>
        </div>
      </div>

      {/* Clinical Profile Attributes & Notes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Attributes (1 Column) */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-3">
          <h2 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
            Clinical Indicators
          </h2>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Communication Mode:</span>
              <span className="font-semibold text-slate-800 capitalize">{patient.communication_ability}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Mobility Status:</span>
              <span className="font-semibold text-slate-800 capitalize">{patient.mobility_status}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Sedation State:</span>
              <span className="font-semibold text-slate-800 capitalize">{patient.sedation_status}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Facial Movement Limitation:</span>
              <span className="font-semibold text-slate-800">{patient.facial_movement_limitation ? 'Yes' : 'No'}</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Speech Limitation:</span>
              <span className="font-semibold text-slate-800">{patient.speech_limitation ? 'Yes' : 'No'}</span>
            </div>
          </div>
        </div>

        {/* Personalized Baseline Benchmarks (2 Columns) */}
        <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Personalized Resting Baselines</h2>
              <p className="text-xs text-slate-500">Individual patient reference calibration parameters</p>
            </div>
            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
              Calibrated
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-[10px]">Baseline Heart Rate</div>
              <div className="text-base font-bold text-slate-900">{baseline.baseline_heart_rate} BPM</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-[10px]">Baseline HRV RMSSD</div>
              <div className="text-base font-bold text-slate-900">{baseline.baseline_hrv_rmssd} ms</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-[10px]">Baseline Respiration</div>
              <div className="text-base font-bold text-slate-900">{baseline.baseline_respiration_rate} br/min</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-[10px]">Baseline EDA Perfusion</div>
              <div className="text-base font-bold text-slate-900">{baseline.baseline_eda_gsr} μS</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-[10px]">Facial Resting Tension</div>
              <div className="text-base font-bold text-slate-900">{baseline.baseline_facial_tension}</div>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-[10px]">Resting Voice Pitch</div>
              <div className="text-base font-bold text-slate-900">{baseline.baseline_voice_pitch} Hz</div>
            </div>
          </div>

          {patient.medical_notes && (
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/60 text-xs">
              <div className="font-semibold text-slate-800 mb-1">Clinical History & Notes:</div>
              <p className="text-slate-600 leading-relaxed">{patient.medical_notes}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
