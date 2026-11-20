"use client";

import React from "react";
import Link from "next/link";
import { Download, ExternalLink, ArrowLeft, Zap, ShieldCheck } from "lucide-react";

export default function PitchDeckPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col font-sans">
      {/* Top Bar */}
      <header className="bg-emerald-950/90 border-b border-emerald-800/60 sticky top-0 z-50 backdrop-blur-md px-4 sm:px-8 py-3.5 flex justify-between items-center shadow-lg">
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="flex items-center space-x-2 text-xs font-bold bg-emerald-900/80 hover:bg-emerald-800 text-emerald-200 hover:text-white px-3 py-1.5 rounded-lg border border-emerald-700/60 transition-all active:scale-95"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to App</span>
          </Link>
          <div className="h-4 w-px bg-emerald-800 hidden sm:block" />
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-amber-500 flex items-center justify-center">
              <Zap className="w-4 h-4 text-emerald-950 fill-current" />
            </div>
            <span className="font-extrabold text-sm sm:text-base tracking-tight text-white">
              BIJLI MITRA AI <span className="text-amber-400 font-semibold text-xs sm:text-sm">Pitch Deck</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2.5">
          <a
            href="/BIJLI_MITRA_AI_PITCH_DECK.pdf"
            download="BIJLI_MITRA_AI_PITCH_DECK.pdf"
            className="flex items-center space-x-1.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-emerald-950 text-xs font-black px-3.5 py-2 rounded-xl shadow-md transition-all active:scale-95"
          >
            <Download className="w-3.5 h-3.5 text-emerald-950" />
            <span>Download PDF</span>
          </a>
          <a
            href="/pitch-deck.html"
            target="_blank"
            className="hidden sm:flex items-center space-x-1.5 bg-emerald-900/80 hover:bg-emerald-800 text-emerald-100 text-xs font-bold px-3 py-2 rounded-xl border border-emerald-700/80 transition-all"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Full-Screen HTML</span>
          </a>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex-1 flex flex-col items-center p-3 sm:p-6 w-full max-w-7xl mx-auto">
        <div className="w-full bg-emerald-900/30 border border-emerald-800/40 rounded-2xl p-4 sm:p-6 mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <div className="inline-flex items-center gap-1.5 bg-amber-400/10 text-amber-300 border border-amber-400/30 text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full mb-1.5">
              <ShieldCheck className="w-3 h-3 text-amber-400" />
              Telangana Government Challenge 13 • Energy Department
            </div>
            <h1 className="text-lg sm:text-2xl font-black text-white">
              Executive Submission Pitch Deck
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1">
              Personalized Electricity Billing Assistance & Tariff Transparency Platform (TGSPDCL & TGNPDCL).
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <a
              href="/BIJLI_MITRA_AI_PITCH_DECK.pdf"
              target="_blank"
              className="text-xs font-bold text-amber-300 hover:text-amber-200 underline"
            >
              Open Raw PDF in New Tab &rarr;
            </a>
          </div>
        </div>

        {/* Embedded Interactive Viewer */}
        <div className="w-full flex-1 rounded-2xl overflow-hidden border border-emerald-800/60 shadow-2xl bg-black min-h-[750px]">
          <iframe
            src="/pitch-deck.html"
            title="BIJLI MITRA AI Pitch Deck"
            className="w-full h-full min-h-[750px] border-none"
          />
        </div>
      </div>
    </div>
  );
}
