import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, Search, Plus, Filter, UserCheck, ShieldAlert, ArrowRight, X } from 'lucide-react';
import { api } from '../services/api';
import { Patient } from '../types';

export const Patients: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [search, setSearch] = useState('');
  const [commFilter, setCommFilter] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);

  const [newPatient, setNewPatient] = useState<Partial<Patient>>({
    full_name: '',
    age: 45,
    gender: 'female',
    communication_ability: 'verbal',
    mobility_status: 'full',
    sedation_status: 'alert',
    facial_movement_limitation: false,
    speech_limitation: false,
    medical_notes: '',
  });

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    const data = await api.getPatients();
    setPatients(data);
  };

  const handleCreatePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createPatient(newPatient);
    setShowAddModal(false);
    loadPatients();
  };

  const filteredPatients = patients.filter((p) => {
    const matchesSearch =
      p.full_name.toLowerCase().includes(search.toLowerCase()) ||
      p.patient_id.toLowerCase().includes(search.toLowerCase());

    const matchesComm =
      commFilter === 'all' || p.communication_ability === commFilter;

    return matchesSearch && matchesComm;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Patient Clinical Roster</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Registered patients with personalized baselines & clinical profile settings
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 rounded-xl transition-all shadow-xs flex items-center space-x-2 w-max cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Patient</span>
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-2xs">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Patient Name or ID (e.g. PAT-8801)..."
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={commFilter}
            onChange={(e) => setCommFilter(e.target.value)}
            className="py-2 px-3 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 bg-white"
          >
            <option value="all">All Communication Profiles</option>
            <option value="verbal">Verbal Patients</option>
            <option value="non-verbal">Non-Verbal Profile</option>
            <option value="intubated">Intubated</option>
          </select>
        </div>
      </div>

      {/* Patients Roster Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-2xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-400 font-semibold uppercase text-[10px]">
              <tr>
                <th className="p-4">Patient Name & ID</th>
                <th className="p-4">Age / Gender</th>
                <th className="p-4">Communication Profile</th>
                <th className="p-4">Mobility & Sedation</th>
                <th className="p-4">Last Assessment</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredPatients.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-4">
                    <div className="font-bold text-slate-900">{p.full_name}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{p.patient_id}</div>
                  </td>
                  <td className="p-4 text-slate-700 font-medium">
                    {p.age} yrs • <span className="capitalize">{p.gender}</span>
                  </td>
                  <td className="p-4">
                    {p.communication_ability === 'non-verbal' ? (
                      <span className="bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold px-2 py-0.5 rounded-md inline-block">
                        Non-Verbal Profile
                      </span>
                    ) : p.communication_ability === 'intubated' ? (
                      <span className="bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold px-2 py-0.5 rounded-md inline-block">
                        Intubated
                      </span>
                    ) : (
                      <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-medium px-2 py-0.5 rounded-md inline-block">
                        Verbal
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-slate-600">
                    <div className="capitalize">{p.mobility_status} mobility</div>
                    <div className="text-[11px] text-slate-400 capitalize">{p.sedation_status}</div>
                  </td>
                  <td className="p-4 text-slate-500">
                    {p.last_assessment_at ? new Date(p.last_assessment_at).toLocaleDateString() : 'No sessions yet'}
                  </td>
                  <td className="p-4 text-right space-x-2">
                    <Link
                      to={`/patient/${p.id}`}
                      className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:text-cyan-700 bg-slate-100 hover:bg-cyan-50 rounded-lg transition-colors inline-block"
                    >
                      Profile & Baseline
                    </Link>
                    <Link
                      to={`/assessment/new?patient_id=${p.patient_id}`}
                      className="px-2.5 py-1 text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors inline-block"
                    >
                      Assess
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Patient Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4 border border-slate-200 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">Register New Clinical Patient</h2>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePatient} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Full Patient Name</label>
                <input
                  type="text"
                  required
                  value={newPatient.full_name}
                  onChange={(e) => setNewPatient({ ...newPatient, full_name: e.target.value })}
                  placeholder="e.g. John Doe"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Age (Years)</label>
                  <input
                    type="number"
                    value={newPatient.age}
                    onChange={(e) => setNewPatient({ ...newPatient, age: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Gender</label>
                  <select
                    value={newPatient.gender}
                    onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value as any })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 bg-white"
                  >
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Communication Ability</label>
                  <select
                    value={newPatient.communication_ability}
                    onChange={(e) => setNewPatient({ ...newPatient, communication_ability: e.target.value as any })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 bg-white"
                  >
                    <option value="verbal">Verbal Patient</option>
                    <option value="non-verbal">Non-Verbal Profile</option>
                    <option value="intubated">Intubated</option>
                    <option value="cognitive_impairment">Cognitive Impairment</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Mobility Status</label>
                  <select
                    value={newPatient.mobility_status}
                    onChange={(e) => setNewPatient({ ...newPatient, mobility_status: e.target.value as any })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 bg-white"
                  >
                    <option value="full">Full Mobility</option>
                    <option value="restricted">Restricted / Limited</option>
                    <option value="bedridden">Bedridden</option>
                    <option value="assisted">Assisted</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Medical Notes & History</label>
                <textarea
                  rows={2}
                  value={newPatient.medical_notes}
                  onChange={(e) => setNewPatient({ ...newPatient, medical_notes: e.target.value })}
                  placeholder="Post-op recovery details, chronic conditions..."
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-white bg-cyan-600 hover:bg-cyan-700 rounded-xl font-bold"
                >
                  Save Patient Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
