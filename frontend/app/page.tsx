"use client";

import React, { useState, useEffect, useMemo, useRef } from "react";
import {
  Zap,
  FileText,
  Upload,
  BarChart3,
  ShieldCheck,
  AlertTriangle,
  MessageSquare,
  BookOpen,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Globe,
  CheckCircle2,
  AlertCircle,
  TrendingDown,
  TrendingUp,
  Sparkles,
  Info,
  DollarSign,
  Building,
  Check,
  X,
  FileCheck,
  Calculator,
  Printer,
  Phone,
  HelpCircle,
  Flame,
  Award,
  Sliders,
  Download,
  Clock,
  Layers,
  Search,
  ExternalLink,
  Plus,
  Minus,
  Camera,
  Home
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  ReferenceLine
} from "recharts";

import {
  fetchBills,
  fetchBill,
  uploadBill,
  verifyBill,
  calculateBill,
  fetchAnalyticsSummary,
  fetchBillSavings,
  fetchTariffs,
  simulateBill,
  sendChatMessage,
  BillSummary,
  CalculationResult,
  AnalyticsSummary
} from "@/lib/api";

type TabType =
  | "dashboard"
  | "simulator"
  | "upload"
  | "my_bills"
  | "analysis"
  | "analytics"
  | "savings"
  | "chat"
  | "tariffs";

// Safe numeric currency formatter
const fmt = (n?: number | null, decimals = 2): string => {
  if (typeof n !== "number" || isNaN(n)) return "0.00";
  return n.toLocaleString("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

// Safe property extractor handling both { value: ... } objects and raw primitives
function getFieldVal(field: any, defaultVal: any = ""): any {
  if (field === null || field === undefined) return defaultVal;
  if (typeof field === "object" && "value" in field) {
    return field.value ?? defaultVal;
  }
  return field ?? defaultVal;
}

export default function BijliMitraApp() {
  const [activeTab, setActiveTab] = useState<TabType>("dashboard");
  const [lang, setLang] = useState<"en" | "te">("en");

  // Core Data States
  const [bills, setBills] = useState<BillSummary[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [selectedBillId, setSelectedBillId] = useState<number | null>(null);
  const [selectedBillData, setSelectedBillData] = useState<any>(null);
  const [calculationResult, setCalculationResult] = useState<CalculationResult | null>(null);
  const [savingsData, setSavingsData] = useState<any>(null);
  const [tariffData, setTariffData] = useState<any>(null);

  // Loading & Error States
  const [initialLoading, setInitialLoading] = useState(true);
  const [calcLoading, setCalcLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  // Upload & Verification States
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [reviewBillId, setReviewBillId] = useState<number | null>(null);
  const [reviewFields, setReviewFields] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Simulator States (Instant Calculation for Citizens)
  const [simUnits, setSimUnits] = useState<number>(180);
  const [simUtility, setSimUtility] = useState<string>("TGSPDCL");
  const [simLoad, setSimLoad] = useState<number>(2.0);
  const [simMonth, setSimMonth] = useState<string>("2026-11");
  const [simIsGjEligible, setSimIsGjEligible] = useState<boolean>(true);
  const [simResult, setSimResult] = useState<CalculationResult | null>(null);
  const [simLoading, setSimLoading] = useState<boolean>(false);

  // Search in My Bills
  const [billSearchQuery, setBillSearchQuery] = useState("");

  // Chat Assistant States
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<
    Array<{
      sender: "user" | "assistant";
      text: string;
      facts?: string[];
      suggestions?: string[];
    }>
  >([
    {
      sender: "assistant",
      text:
        lang === "te"
          ? "నమస్కారం! నేను మీ బిజిలీ మిత్ర AI సహాయకుడిని. మీ విద్యుత్ బిల్లు, టారిఫ్ స్లాబ్‌లు, గృహజ్యోతి రాయితీ లేదా ట్రూ-అప్ ఛార్జీల గురించి ఏవైనా సందేహాలు ఉంటే అడగండి."
          : "Namaste! I am Bijli Mitra AI, your personal electricity billing advisor. Ask me anything about your bill calculations, tariff slabs, Gruha Jyothi zero-bill eligibility, or True-Up recoveries.",
      suggestions: [
        "How is my bill calculated telescopic across slabs?",
        "Am I eligible for Gruha Jyothi zero bill?",
        "What is the True-Up recovery in November 2026 bills?",
        "Why did my bill jump when I crossed 200 units?",
      ],
    },
  ]);

  // Load Initial Application Data
  const loadData = async () => {
    try {
      setServerError(null);
      const [billsData, analyticsData, tariffsData] = await Promise.all([
        fetchBills().catch(() => []),
        fetchAnalyticsSummary().catch(() => null),
        fetchTariffs().catch(() => null),
      ]);

      setBills(billsData || []);
      setAnalytics(analyticsData);
      setTariffData(tariffsData);

      if (billsData && billsData.length > 0 && !selectedBillId) {
        const firstId = billsData[0].id;
        setSelectedBillId(firstId);
        loadBillDetail(firstId);
      }
    } catch (e: any) {
      console.error("Initialization error", e);
    } finally {
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Update simulator whenever simulator inputs change
  useEffect(() => {
    const runSimulation = async () => {
      setSimLoading(true);
      try {
        const res = await simulateBill({
          units: simUnits,
          contracted_load_kw: simLoad,
          billing_month: simMonth,
          utility_code: simUtility,
          gruha_jyothi_eligible: simIsGjEligible,
        });
        setSimResult(res);
      } catch (err) {
        console.error("Simulation error", err);
      } finally {
        setSimLoading(false);
      }
    };
    runSimulation();
  }, [simUnits, simUtility, simLoad, simMonth, simIsGjEligible]);

  const loadBillDetail = async (id: number) => {
    try {
      setCalcLoading(true);
      const res = await fetchBill(id);
      setSelectedBillData(res?.bill || null);
      if (res?.calculation) {
        setCalculationResult(res.calculation);
      } else {
        const calcRes = await calculateBill(id);
        setCalculationResult(calcRes);
      }
      const savingsRes = await fetchBillSavings(id).catch(() => null);
      setSavingsData(savingsRes);
    } catch (e) {
      console.error("Error loading bill detail", e);
    } finally {
      setCalcLoading(false);
    }
  };

  const handleSelectBill = (id: number) => {
    setSelectedBillId(id);
    loadBillDetail(id);
    setActiveTab("analysis");
  };

  // Automated Upload & Extraction Pipeline
  const processUploadFile = async (file: File) => {
    setUploadFile(file);
    setUploadLoading(true);
    setUploadMessage(
      lang === "te"
        ? "బిల్లును హై-రిజల్యూషన్ OCRతో చదువుతోంది మరియు టారిఫ్ లెక్కిస్తోంది..."
        : "Scanning bill with high-res OCR & computing statutory TGERC tariff..."
    );
    try {
      const res = await uploadBill(file);
      setUploadMessage(res.message);
      const billId = res.bill_id;
      if (billId) {
        setSelectedBillId(billId);
        setReviewBillId(billId);
        setReviewFields(res.extracted_data);
        if (res.calculation) {
          setCalculationResult(res.calculation);
        } else {
          const calcRes = await calculateBill(billId);
          setCalculationResult(calcRes);
        }
        await loadBillDetail(billId);
        await loadData();
        // Immediately navigate to detailed Bill Analysis & AI Explanations!
        setActiveTab("analysis");
      }
    } catch (err: any) {
      setUploadMessage(`Error: ${err.message}`);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    await processUploadFile(uploadFile);
  };

  // Verification submit (Module 4)
  const handleSaveVerification = async () => {
    if (!reviewBillId || !reviewFields) return;
    setCalcLoading(true);
    try {
      const payload = {
        utility_code: getFieldVal(reviewFields.utility_code, "TGSPDCL"),
        service_number: getFieldVal(reviewFields.service_number, ""),
        consumer_name: getFieldVal(reviewFields.consumer_name, ""),
        consumer_category: getFieldVal(reviewFields.consumer_category, "LT-I Domestic"),
        billing_month: getFieldVal(reviewFields.billing_month, "2026-11"),
        consumption_units: Number(getFieldVal(reviewFields.consumption_units, 0)),
        contracted_load_kw: Number(getFieldVal(reviewFields.contracted_load_kw, 1.0)),
        printed_total: Number(getFieldVal(reviewFields.printed_total, 0)),
        is_gruha_jyothi: Boolean(getFieldVal(reviewFields.is_gruha_jyothi, false)),
        gruha_jyothi_eligible: Boolean(getFieldVal(reviewFields.gruha_jyothi_eligible, false)),
      };
      await verifyBill(reviewBillId, payload);
      const calcRes = await calculateBill(reviewBillId);
      setCalculationResult(calcRes);
      setSelectedBillId(reviewBillId);
      await loadBillDetail(reviewBillId);
      await loadData();
      setActiveTab("analysis");
    } catch (e: any) {
      alert(`Verification error: ${e.message}`);
    } finally {
      setCalcLoading(false);
    }
  };

  // Chat send
  const handleSendChat = async (userPrompt?: string) => {
    const textToSend = userPrompt || chatInput;
    if (!textToSend.trim()) return;

    const newMsgs = [
      ...chatMessages,
      { sender: "user" as const, text: textToSend },
    ];
    setChatMessages(newMsgs);
    setChatInput("");
    setChatLoading(true);

    try {
      const res = await sendChatMessage(
        textToSend,
        selectedBillId || undefined,
        lang
      );
      setChatMessages([
        ...newMsgs,
        {
          sender: "assistant",
          text: lang === "te" ? res.reply_te : res.reply_en,
          facts: res.grounded_facts || [],
          suggestions: res.suggested_questions || [],
        },
      ]);
    } catch (err: any) {
      setChatMessages([
        ...newMsgs,
        {
          sender: "assistant",
          text:
            lang === "te"
              ? "క్షమించండి, సర్వర్‌ను సంప్రదించడంలో సమస్య ఏర్పడింది. దయచేసి మళ్లీ ప్రయత్నించండి."
              : "Apologies, could not connect to the billing advisor service. Please check if the backend server is active.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // Filtered bills for My Bills tab
  const filteredBills = useMemo(() => {
    if (!billSearchQuery.trim()) return bills;
    const q = billSearchQuery.toLowerCase();
    return bills.filter(
      (b) =>
        b.billing_month.toLowerCase().includes(q) ||
        (b.service_number && b.service_number.toLowerCase().includes(q)) ||
        b.utility_code.toLowerCase().includes(q) ||
        (b.consumer_name && b.consumer_name.toLowerCase().includes(q))
    );
  }, [bills, billSearchQuery]);

  // Safe arrays for active calculation
  const energySlabs = calculationResult?.energy_slabs ?? [];
  const itemizedCharges = calculationResult?.itemized_charges ?? [];
  const anomalies = calculationResult?.anomalies ?? [];
  const sourceCitations = calculationResult?.source_citations ?? [];

  return (
    <div className="min-h-screen bg-slate-100/70 text-slate-900 flex flex-col font-sans selection:bg-emerald-200 antialiased pb-20 md:pb-0">
      {/* ========================================================
          1. COMPACT & MOBILE-FIRST OFFICIAL HEADER
      ======================================================== */}
      <header className="bg-gradient-to-r from-emerald-950 via-teal-950 to-emerald-900 text-white border-b-2 sm:border-b-4 border-amber-500 shadow-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-3.5 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-2.5 sm:py-3.5 gap-2">
            {/* Government Crest & Title */}
            <div className="flex items-center space-x-2.5 sm:space-x-3.5 min-w-0">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-md border border-amber-300/60 shrink-0">
                <Zap className="w-5 h-5 sm:w-7 sm:h-7 text-emerald-950 fill-current" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center space-x-1.5">
                  <span className="text-[9px] sm:text-[10px] tracking-wider uppercase font-black text-amber-400 bg-emerald-900/90 px-1.5 py-0.2 sm:px-2 sm:py-0.5 rounded border border-amber-400/40 truncate">
                    Govt of Telangana • తెలంగాణ ప్రభుత్వం
                  </span>
                </div>
                <h1 className="text-base sm:text-xl font-black tracking-tight text-white flex items-center gap-1.5 truncate">
                  <span>BIJLI MITRA AI</span>
                  <span className="text-amber-400 font-semibold text-xs sm:text-sm hidden xs:inline">
                    (బిజిలీ మిత్ర)
                  </span>
                </h1>
                <p className="text-[10px] sm:text-xs text-emerald-200/90 font-medium truncate hidden sm:block">
                  {lang === "te"
                    ? "తెలంగాణ విద్యుత్ బిల్లింగ్ సహాయ వేదిక (TGSPDCL & TGNPDCL)"
                    : "Personalized Electricity Billing Assistance (TGSPDCL & TGNPDCL)"}
                </p>
              </div>
            </div>

            {/* Helpline & Language Toggle */}
            <div className="flex items-center space-x-2 shrink-0">
              {/* 24x7 Helpline */}
              <a
                href="tel:1912"
                className="flex items-center space-x-1 text-xs bg-amber-500 hover:bg-amber-400 text-emerald-950 font-black px-2.5 py-1.5 rounded-xl shadow-xs transition-all active:scale-95"
                title="Telangana 24x7 Electricity Toll-Free Helpline"
              >
                <Phone className="w-3.5 h-3.5 text-emerald-950 fill-current" />
                <span className="font-mono">1912</span>
              </a>

              {/* Bilingual Language Switcher */}
              <div className="flex items-center bg-emerald-900/90 p-0.5 sm:p-1 rounded-xl border border-emerald-700 shadow-inner">
                <button
                  onClick={() => setLang("en")}
                  className={`px-2 sm:px-3 py-1 text-[11px] sm:text-xs font-bold rounded-lg transition-all cursor-pointer ${
                    lang === "en"
                      ? "bg-amber-400 text-emerald-950 shadow-xs font-black"
                      : "text-emerald-200 hover:text-white"
                  }`}
                >
                  EN
                </button>
                <button
                  onClick={() => setLang("te")}
                  className={`px-2 sm:px-3 py-1 text-[11px] sm:text-xs font-bold rounded-lg transition-all cursor-pointer ${
                    lang === "te"
                      ? "bg-amber-400 text-emerald-950 shadow-xs font-black"
                      : "text-emerald-200 hover:text-white"
                  }`}
                >
                  తె
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================
            HORIZONTAL TAB SCROLLER (TOP BAR)
        ======================================================== */}
        <div className="bg-emerald-900/95 border-t border-emerald-800/80 px-3 sm:px-6 lg:px-8 overflow-x-auto scrollbar-none shadow-inner">
          <div className="max-w-7xl mx-auto flex space-x-1.5 py-1.5 sm:py-2 min-w-max">
            {[
              { id: "dashboard", icon: Zap, label_en: "Dashboard", label_te: "హోమ్‌పేజీ" },
              { id: "simulator", icon: Calculator, label_en: "Live Simulator", label_te: "కాలిక్యులేటర్", highlight: true },
              { id: "upload", icon: Upload, label_en: "Upload Bill", label_te: "బిల్లు అప్‌లోడ్" },
              { id: "my_bills", icon: FileText, label_en: "My Bills", label_te: "నా బిల్లులు", badge: bills.length },
              { id: "analysis", icon: ShieldCheck, label_en: "Bill Analysis", label_te: "సమగ్ర విశ్లేషణ" },
              { id: "analytics", icon: BarChart3, label_en: "Trends", label_te: "వినియోగ గ్రాఫ్" },
              { id: "savings", icon: Sparkles, label_en: "Savings Advisor", label_te: "పొదుపు సలహాలు" },
              { id: "chat", icon: MessageSquare, label_en: "Ask AI", label_te: "ఏఐ సహాయకుడు" },
              { id: "tariffs", icon: BookOpen, label_en: "Tariff Schedules", label_te: "అధికారిక టారిఫ్‌లు" },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer select-none active:scale-95 ${
                    isActive
                      ? tab.highlight
                        ? "bg-amber-400 text-emerald-950 shadow-md ring-2 ring-amber-300"
                        : "bg-emerald-700 text-white shadow-md ring-1 ring-emerald-500"
                      : tab.highlight
                      ? "text-amber-300 hover:bg-emerald-800/80 hover:text-amber-200"
                      : "text-emerald-200 hover:bg-emerald-800/60 hover:text-white"
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${tab.highlight && !isActive ? "text-amber-400" : ""}`} />
                  <span>{lang === "te" ? tab.label_te : tab.label_en}</span>
                  {tab.badge !== undefined && tab.badge > 0 && (
                    <span className="bg-emerald-950 text-amber-300 text-[9px] px-1.5 py-0.2 rounded-full font-mono border border-emerald-700">
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* ========================================================
          MAIN CONTENT CONTAINER (PADDED FOR MOBILE)
      ======================================================== */}
      <main className="max-w-7xl mx-auto px-3.5 sm:px-6 lg:px-8 py-4 sm:py-7 flex-1 w-full">
        {initialLoading ? (
          <div className="flex flex-col items-center justify-center py-20 space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center shadow-inner">
              <RefreshCw className="w-7 h-7 text-emerald-800 animate-spin" />
            </div>
            <p className="font-bold text-slate-800 text-sm">
              Connecting to Telangana State Billing Engine...
            </p>
          </div>
        ) : (
          <>
            {/* ========================================================
                TAB 1: CITIZEN DASHBOARD
            ======================================================== */}
            {activeTab === "dashboard" && (
              <div className="space-y-4 sm:space-y-6">
                {/* Hero Card */}
                <div className="bg-gradient-to-br from-emerald-900 via-teal-900 to-emerald-950 text-white p-4 sm:p-7 rounded-2xl sm:rounded-3xl shadow-xl border-b-4 border-amber-400 relative overflow-hidden">
                  <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div className="space-y-1.5">
                      <div className="flex items-center space-x-2">
                        <span className="bg-amber-400 text-emerald-950 font-black text-[9px] sm:text-[10px] px-2 py-0.5 rounded uppercase tracking-wider shadow-xs">
                          Telangana Energy Department
                        </span>
                        <span className="text-emerald-200 text-xs font-semibold">
                          Praja Palana • Gruha Jyothi
                        </span>
                      </div>
                      <h2 className="text-xl sm:text-3xl font-black tracking-tight text-white">
                        {lang === "te"
                          ? "మీ విద్యుత్ బిల్లు పూర్తి పారదర్శకతతో"
                          : "Transparent & Auditable Electricity Billing"}
                      </h2>
                      <p className="text-xs sm:text-sm text-emerald-100/90 max-w-2xl leading-relaxed">
                        {lang === "te"
                          ? "మీ బిల్లులోని ప్రతి పైసా లెక్క, టెలిస్కోపిక్ స్లాబ్‌లు, గృహజ్యోతి జీరో బిల్లు అర్హత మరియు ట్రూ-అప్ ఛార్జీల ఖచ్చితత్వాన్ని తెలుసుకోండి."
                          : "Understand every Rupee on your bill, verify telescopic domestic slabs, track Gruha Jyothi zero-bill eligibility, and audit charges."}
                      </p>
                    </div>

                    <div className="flex w-full sm:w-auto gap-2.5">
                      <button
                        onClick={() => setActiveTab("simulator")}
                        className="flex-1 sm:flex-none justify-center px-4 py-2.5 sm:px-5 sm:py-3 bg-gradient-to-r from-amber-400 to-amber-500 text-emerald-950 rounded-xl sm:rounded-2xl text-xs font-black flex items-center space-x-2 shadow-md transition-all active:scale-95 cursor-pointer"
                      >
                        <Calculator className="w-4 h-4 fill-current" />
                        <span>{lang === "te" ? "బిల్లు లెక్కించండి" : "Simulate Bill"}</span>
                      </button>
                      <button
                        onClick={() => setActiveTab("upload")}
                        className="flex-1 sm:flex-none justify-center px-4 py-2.5 sm:px-5 sm:py-3 bg-white/10 hover:bg-white/20 text-white border border-white/30 rounded-xl sm:rounded-2xl text-xs font-black flex items-center space-x-2 transition-all active:scale-95 cursor-pointer"
                      >
                        <Upload className="w-4 h-4" />
                        <span>{lang === "te" ? "బిల్లు అప్‌లోడ్" : "Upload Bill"}</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* KPI Metrics Cards (2 columns on mobile, 4 on desktop) */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4">
                  {/* Latest Bill */}
                  <div className="bg-white p-3.5 sm:p-5 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider">
                          {lang === "te" ? "తాజా బిల్లు" : "Latest Bill"}
                        </p>
                        <h3 className="text-lg sm:text-2xl font-black text-slate-900 mt-1 font-mono">
                          ₹ {fmt(analytics?.latest_bill_amount)}
                        </h3>
                      </div>
                      <span className="p-2 sm:p-2.5 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-100">
                        <DollarSign className="w-4 h-4" />
                      </span>
                    </div>
                    <p className="text-[10px] sm:text-xs text-slate-500 mt-1.5 truncate">
                      {lang === "te" ? "చివరి నెలకు బిల్లు" : "For active consumer bill"}
                    </p>
                  </div>

                  {/* Latest Consumption */}
                  <div className="bg-white p-3.5 sm:p-5 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider">
                          {lang === "te" ? "తాజా వినియోగం" : "Consumption"}
                        </p>
                        <h3 className="text-lg sm:text-2xl font-black text-slate-900 mt-1 font-mono">
                          {analytics?.latest_units ?? 0}{" "}
                          <span className="text-xs font-normal text-slate-500">kWh</span>
                        </h3>
                      </div>
                      <span className="p-2 sm:p-2.5 rounded-xl bg-amber-50 text-amber-800 border border-amber-100">
                        <Zap className="w-4 h-4 fill-current" />
                      </span>
                    </div>
                    <div className="flex items-center text-[10px] sm:text-xs mt-1.5 font-bold truncate">
                      {analytics?.consumption_change_pct !== null &&
                      analytics?.consumption_change_pct !== undefined ? (
                        analytics.consumption_change_pct >= 0 ? (
                          <span className="text-rose-600 flex items-center">
                            <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
                            +{analytics.consumption_change_pct}%
                          </span>
                        ) : (
                          <span className="text-emerald-600 flex items-center">
                            <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
                            {analytics.consumption_change_pct}%
                          </span>
                        )
                      ) : (
                        <span className="text-slate-400">Baseline</span>
                      )}
                      <span className="text-slate-400 ml-1 font-normal truncate">vs prev</span>
                    </div>
                  </div>

                  {/* Gruha Jyothi Status */}
                  <div className="bg-white p-3.5 sm:p-5 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider">
                          {lang === "te" ? "గృహజ్యోతి" : "Gruha Jyothi"}
                        </p>
                        <h3 className="text-sm sm:text-lg font-black text-slate-900 mt-1 flex items-center">
                          {(analytics?.latest_units ?? 0) <= 200 ? (
                            <span className="text-emerald-700 flex items-center truncate">
                              <CheckCircle2 className="w-4 h-4 mr-1 shrink-0" />
                              Zero Bill
                            </span>
                          ) : (
                            <span className="text-rose-600 flex items-center text-xs truncate">
                              <AlertTriangle className="w-3.5 h-3.5 mr-1 shrink-0" />
                              &gt;200 Units
                            </span>
                          )}
                        </h3>
                      </div>
                      <span className="p-2 sm:p-2.5 rounded-xl bg-teal-50 text-teal-800 border border-teal-100">
                        <Award className="w-4 h-4" />
                      </span>
                    </div>
                    <p className="text-[10px] sm:text-xs text-slate-500 mt-1.5 truncate">
                      {(analytics?.latest_units ?? 0) <= 200
                        ? "100% Subsidy (<=200u)"
                        : "Full tariff charged"}
                    </p>
                  </div>

                  {/* Audit Discrepancies */}
                  <div className="bg-white p-3.5 sm:p-5 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider">
                          {lang === "te" ? "ఆడిట్ ఫలితాలు" : "Audit Status"}
                        </p>
                        <h3 className="text-lg sm:text-2xl font-black text-slate-900 mt-1 font-mono">
                          {analytics?.discrepancies_detected_count ?? 0}
                        </h3>
                      </div>
                      <span className="p-2 sm:p-2.5 rounded-xl bg-purple-50 text-purple-800 border border-purple-100">
                        <FileCheck className="w-4 h-4" />
                      </span>
                    </div>
                    <p className="text-[10px] sm:text-xs text-slate-500 mt-1.5 truncate">
                      TGERC 18% Rule
                    </p>
                  </div>
                </div>

                {/* Gruha Jyothi Threshold Visualizer */}
                <div className="bg-white p-4 sm:p-6 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-3">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1.5">
                    <div>
                      <h3 className="font-bold text-slate-900 text-xs sm:text-sm flex items-center gap-1.5">
                        <Award className="w-4 h-4 text-emerald-700" />
                        <span>
                          {lang === "te"
                            ? "గృహజ్యోతి పథకం పరిమితి సూచిక (200 Units Ceiling)"
                            : "Gruha Jyothi 200-Unit Threshold Visualizer"}
                        </span>
                      </h3>
                      <p className="text-[11px] text-slate-500">
                        {lang === "te"
                          ? "200 యూనిట్ల లోపు వాడితే బిల్లు ₹0. 201 యూనిట్లకు చేరితే ₹1,000+ పూర్తి బిల్లు చెల్లించాలి!"
                          : "Consuming <=200 units yields ₹0 zero bill. Crossing 200 charges full LT-I(B)(ii) rates!"}
                      </p>
                    </div>
                    <span className="font-mono text-xs font-black px-2.5 py-1 bg-slate-100 rounded-lg text-slate-800 border">
                      {analytics?.latest_units ?? 0} / 200 kWh
                    </span>
                  </div>

                  <div className="w-full bg-slate-100 h-4 rounded-full overflow-hidden p-0.5 border border-slate-200 shadow-inner">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        (analytics?.latest_units ?? 0) <= 180
                          ? "bg-gradient-to-r from-emerald-500 to-emerald-600"
                          : (analytics?.latest_units ?? 0) <= 200
                          ? "bg-gradient-to-r from-amber-400 to-amber-500"
                          : "bg-gradient-to-r from-rose-500 to-rose-600"
                      }`}
                      style={{
                        width: `${Math.min(
                          100,
                          ((analytics?.latest_units ?? 0) / 200) * 100
                        )}%`,
                      }}
                    />
                  </div>

                  <div className="flex justify-between text-[10px] sm:text-[11px] text-slate-500 font-mono font-semibold">
                    <span>0u (Free)</span>
                    <span className="text-emerald-700 font-bold">100u [LT-I(A)]</span>
                    <span className="text-amber-600 font-bold">200u [Limit]</span>
                    <span className="text-rose-600 font-bold">201u+ [Loss]</span>
                  </div>
                </div>

                {/* Recent Bills: Mobile Responsive Cards on Mobile, Table on Desktop */}
                <div className="bg-white rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="p-4 sm:p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <div>
                      <h3 className="font-black text-slate-900 text-sm">
                        {lang === "te" ? "ఇటీవలి బిల్లులు" : "Recent Analyzed Bills"}
                      </h3>
                      <p className="text-[11px] text-slate-500">
                        Tap any bill to view line-item tariff audit
                      </p>
                    </div>
                    <button
                      onClick={() => setActiveTab("my_bills")}
                      className="px-2.5 py-1 bg-emerald-50 text-emerald-800 rounded-lg text-xs font-bold flex items-center space-x-1 border border-emerald-200 cursor-pointer"
                    >
                      <span>{lang === "te" ? "అన్నీ" : "View All"}</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Mobile Stacked Cards (<640px) */}
                  <div className="block sm:hidden divide-y divide-slate-100 p-2 space-y-2">
                    {bills.slice(0, 4).map((b) => (
                      <div
                        key={b.id}
                        className={`p-3.5 rounded-xl border border-slate-200 space-y-2.5 ${
                          selectedBillId === b.id ? "bg-emerald-50/60 border-emerald-300" : "bg-white"
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-black text-slate-900 font-mono text-sm">
                            {b.billing_month}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 font-black text-[10px]">
                            {b.utility_code}
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-xs">
                          <div>
                            <span className="text-slate-500">Usage: </span>
                            <span className="font-bold text-slate-800 font-mono">{b.consumption_units} kWh</span>
                          </div>
                          <div>
                            <span className="text-slate-500">Payable: </span>
                            <span className="font-black text-slate-900 font-mono text-sm">₹ {fmt(b.printed_total)}</span>
                          </div>
                        </div>
                        <div className="flex justify-between items-center pt-1 border-t border-slate-100">
                          {b.is_gruha_jyothi ? (
                            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              Zero Bill (₹0)
                            </span>
                          ) : (
                            <span className="text-[10px] text-slate-500">Standard Domestic</span>
                          )}
                          <button
                            onClick={() => handleSelectBill(b.id)}
                            className="px-3 py-1.5 bg-emerald-800 text-white rounded-lg font-bold text-xs shadow-xs active:scale-95 cursor-pointer"
                          >
                            Inspect Bill
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Desktop Full Table (>=640px) */}
                  <div className="hidden sm:block overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-100/70 text-slate-600 font-bold border-b border-slate-200">
                        <tr>
                          <th className="p-3.5">Bill Month</th>
                          <th className="p-3.5">Service Connection</th>
                          <th className="p-3.5">Utility</th>
                          <th className="p-3.5 text-right">Units</th>
                          <th className="p-3.5 text-right">Printed Total</th>
                          <th className="p-3.5 text-center">Gruha Jyothi</th>
                          <th className="p-3.5 text-center">Status</th>
                          <th className="p-3.5 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {bills.slice(0, 5).map((b) => (
                          <tr
                            key={b.id}
                            className={`hover:bg-slate-50/80 transition ${
                              selectedBillId === b.id ? "bg-emerald-50/60 font-semibold" : ""
                            }`}
                          >
                            <td className="p-3.5 font-bold text-slate-900 font-mono">{b.billing_month}</td>
                            <td className="p-3.5 font-mono text-slate-600">{b.service_number || "TG-SERVICE"}</td>
                            <td className="p-3.5">
                              <span className="px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-900 font-black text-[10px]">
                                {b.utility_code}
                              </span>
                            </td>
                            <td className="p-3.5 text-right font-black text-slate-800 font-mono">
                              {b.consumption_units} kWh
                            </td>
                            <td className="p-3.5 text-right font-black text-slate-900 font-mono text-sm">
                              ₹ {fmt(b.printed_total)}
                            </td>
                            <td className="p-3.5 text-center">
                              {b.is_gruha_jyothi ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800">
                                  Zero Bill (₹0)
                                </span>
                              ) : (
                                <span className="text-slate-400 text-[10px]">Standard</span>
                              )}
                            </td>
                            <td className="p-3.5 text-center">
                              {b.has_discrepancy ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-100 text-rose-800">
                                  Flagged
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800">
                                  Verified
                                </span>
                              )}
                            </td>
                            <td className="p-3.5 text-right">
                              <button
                                onClick={() => handleSelectBill(b.id)}
                                className="px-3.5 py-1.5 bg-emerald-800 hover:bg-emerald-900 text-white rounded-xl font-bold text-xs cursor-pointer active:scale-95"
                              >
                                Inspect
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ========================================================
                TAB 2: LIVE BILL SIMULATOR (MOBILE OPTIMIZED)
            ======================================================== */}
            {activeTab === "simulator" && (
              <div className="space-y-4 sm:space-y-6">
                <div className="bg-white p-4 sm:p-8 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-5">
                  <div className="flex items-center space-x-3 border-b border-slate-100 pb-4">
                    <div className="p-2.5 sm:p-3 bg-amber-100 text-amber-900 rounded-xl sm:rounded-2xl border border-amber-200">
                      <Calculator className="w-5 h-5 sm:w-6 sm:h-6" />
                    </div>
                    <div>
                      <h2 className="text-lg sm:text-2xl font-black text-slate-900">
                        {lang === "te" ? "లైవ్ టారిఫ్ కాలిక్యులేటర్" : "Interactive Bill Calculator"}
                      </h2>
                      <p className="text-xs text-slate-500">
                        Slide units to see instant tariff calculations & Gruha Jyothi zero-bill eligibility
                      </p>
                    </div>
                  </div>

                  {/* Simulator Controls */}
                  <div className="p-4 sm:p-5 bg-slate-50/80 rounded-2xl border border-slate-200 space-y-4">
                    <div className="space-y-2.5">
                      <div className="flex justify-between items-center">
                        <label className="text-xs font-black text-slate-700 uppercase tracking-wider">
                          {lang === "te" ? "వినియోగం (Units)" : "Monthly Consumption"}
                        </label>
                        <div className="flex items-center space-x-1.5">
                          <button
                            type="button"
                            onClick={() => setSimUnits((prev) => Math.max(1, prev - 10))}
                            className="p-2 bg-white hover:bg-slate-100 rounded-lg border text-slate-700 shadow-xs cursor-pointer active:scale-95 font-bold text-xs"
                            title="-10"
                          >
                            -10
                          </button>
                          <input
                            type="number"
                            min="1"
                            max="1500"
                            value={simUnits}
                            onChange={(e) => setSimUnits(Number(e.target.value))}
                            className="w-20 text-center font-black text-emerald-900 font-mono text-base sm:text-lg bg-white border border-slate-300 rounded-lg p-1"
                          />
                          <button
                            type="button"
                            onClick={() => setSimUnits((prev) => prev + 10)}
                            className="p-2 bg-white hover:bg-slate-100 rounded-lg border text-slate-700 shadow-xs cursor-pointer active:scale-95 font-bold text-xs"
                            title="+10"
                          >
                            +10
                          </button>
                        </div>
                      </div>

                      <input
                        type="range"
                        min="1"
                        max="850"
                        value={simUnits}
                        onChange={(e) => setSimUnits(Number(e.target.value))}
                        className="w-full accent-emerald-700 cursor-pointer h-3 bg-slate-200 rounded-lg"
                      />

                      {/* Quick Presets */}
                      <div className="grid grid-cols-3 sm:flex sm:flex-wrap gap-1.5 sm:gap-2 pt-1">
                        <button
                          type="button"
                          onClick={() => setSimUnits(80)}
                          className={`p-2 rounded-lg border text-[11px] font-bold cursor-pointer text-center ${
                            simUnits === 80 ? "bg-emerald-800 text-white" : "bg-white text-slate-700"
                          }`}
                        >
                          80u [LT-I(A)]
                        </button>
                        <button
                          type="button"
                          onClick={() => setSimUnits(180)}
                          className={`p-2 rounded-lg border text-[11px] font-bold cursor-pointer text-center ${
                            simUnits === 180 ? "bg-emerald-800 text-white" : "bg-white text-slate-700"
                          }`}
                        >
                          180u [Free]
                        </button>
                        <button
                          type="button"
                          onClick={() => setSimUnits(200)}
                          className={`p-2 rounded-lg border text-[11px] font-black cursor-pointer text-center ${
                            simUnits === 200 ? "bg-amber-500 text-emerald-950" : "bg-white text-amber-700 border-amber-300"
                          }`}
                        >
                          200u [Ceiling]
                        </button>
                        <button
                          type="button"
                          onClick={() => setSimUnits(201)}
                          className={`p-2 rounded-lg border text-[11px] font-black cursor-pointer text-center col-span-2 sm:col-span-1 ${
                            simUnits === 201 ? "bg-rose-600 text-white" : "bg-white text-rose-700 border-rose-300"
                          }`}
                        >
                          201u [Cliff Loss Alert]
                        </button>
                        <button
                          type="button"
                          onClick={() => setSimUnits(350)}
                          className={`p-2 rounded-lg border text-[11px] font-bold cursor-pointer text-center ${
                            simUnits === 350 ? "bg-emerald-800 text-white" : "bg-white text-slate-700"
                          }`}
                        >
                          350u [Tier 3]
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                      <div>
                        <label className="text-[11px] font-bold text-slate-700 uppercase">Utility</label>
                        <select
                          value={simUtility}
                          onChange={(e) => setSimUtility(e.target.value)}
                          className="w-full mt-1 p-2.5 text-xs bg-white rounded-xl border border-slate-300 font-bold"
                        >
                          <option value="TGSPDCL">TGSPDCL (Southern)</option>
                          <option value="TGNPDCL">TGNPDCL (Northern)</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-[11px] font-bold text-slate-700 uppercase">Contracted Load</label>
                        <select
                          value={simLoad}
                          onChange={(e) => setSimLoad(Number(e.target.value))}
                          className="w-full mt-1 p-2.5 text-xs bg-white rounded-xl border border-slate-300 font-bold"
                        >
                          <option value={1}>1.0 kW</option>
                          <option value={2}>2.0 kW (Standard)</option>
                          <option value={3}>3.0 kW</option>
                          <option value={5}>5.0 kW</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Gruha Jyothi Checkbox */}
                  <div className="flex items-center space-x-3 p-3.5 bg-emerald-50 rounded-xl border border-emerald-200">
                    <input
                      type="checkbox"
                      id="simGjMobile"
                      checked={simIsGjEligible}
                      onChange={(e) => setSimIsGjEligible(e.target.checked)}
                      className="w-5 h-5 accent-emerald-700 rounded cursor-pointer shrink-0"
                    />
                    <label htmlFor="simGjMobile" className="text-xs text-emerald-950 font-bold cursor-pointer leading-tight">
                      Gruha Jyothi Registered (White Ration Card / Praja Palana)
                    </label>
                  </div>

                  {/* Simulator Results */}
                  {simLoading ? (
                    <div className="p-8 text-center">
                      <RefreshCw className="w-6 h-6 animate-spin text-emerald-700 mx-auto" />
                    </div>
                  ) : simResult ? (
                    <div className="space-y-4">
                      {/* Zero Bill Banner */}
                      {simResult.subsidies > 0 ? (
                        <div className="p-4 sm:p-5 bg-gradient-to-r from-emerald-900 to-teal-900 text-white rounded-2xl border-2 border-amber-400 flex flex-col sm:flex-row justify-between items-center gap-3 shadow-md">
                          <div className="space-y-1 text-center sm:text-left">
                            <span className="px-2 py-0.5 rounded bg-emerald-950 text-amber-400 font-black text-[9px] uppercase">
                              Zero Bill Active
                            </span>
                            <h4 className="font-black text-base sm:text-lg">
                              Net Payable Amount: ₹ 0.00 (Zero Bill)
                            </h4>
                            <p className="text-xs text-emerald-200">
                              Telangana Govt provides 100% subsidy for your ₹ {fmt(simResult.computed_total + simResult.subsidies)} bill.
                            </p>
                          </div>
                          <div className="text-center sm:text-right bg-emerald-950/90 px-4 py-2 rounded-xl border border-emerald-800">
                            <p className="text-[10px] text-emerald-300">Govt Subsidy</p>
                            <p className="text-xl sm:text-2xl font-black text-amber-400 font-mono">
                              ₹ {fmt(simResult.subsidies)}
                            </p>
                          </div>
                        </div>
                      ) : simIsGjEligible && simUnits > 200 ? (
                        <div className="p-4 bg-rose-50 text-rose-900 rounded-2xl border border-rose-300 flex items-start space-x-3 shadow-xs">
                          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                          <div className="text-xs space-y-1">
                            <h4 className="font-black text-sm text-rose-900">
                              Gruha Jyothi Disqualified: &gt;200 Units!
                            </h4>
                            <p className="text-rose-800 leading-relaxed">
                              You used {simUnits} units ({simUnits - 200} units above ceiling). Zero subsidy applies; full bill of ₹ {fmt(simResult.computed_total)} payable.
                            </p>
                          </div>
                        </div>
                      ) : null}

                      {/* Metrics 2x2 grid on mobile */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3.5">
                        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                          <p className="text-slate-500 font-bold text-[10px]">Category</p>
                          <p className="font-black text-slate-800 text-xs mt-0.5 truncate">
                            {simResult.category_determined.split(" ")[0]}
                          </p>
                        </div>
                        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                          <p className="text-slate-500 font-bold text-[10px]">Energy Charges</p>
                          <p className="font-black text-emerald-800 text-sm mt-0.5 font-mono">
                            ₹ {fmt(simResult.energy_charges)}
                          </p>
                        </div>
                        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                          <p className="text-slate-500 font-bold text-[10px]">Customer Fee</p>
                          <p className="font-black text-slate-800 text-sm mt-0.5 font-mono">
                            ₹ {fmt(simResult.customer_charges)}
                          </p>
                        </div>
                        <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-xs">
                          <p className="text-emerald-800 font-bold text-[10px]">Net Payable</p>
                          <p className="font-black text-emerald-800 text-base mt-0.5 font-mono">
                            ₹ {fmt(simResult.computed_total)}
                          </p>
                        </div>
                      </div>

                      {/* Slabs breakdown */}
                      {(simResult.energy_slabs ?? []).length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-bold text-slate-700 uppercase">
                            Telescopic Slabs ({simResult.energy_slabs?.length ?? 0} Tiers)
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                            {(simResult.energy_slabs ?? []).map((s, idx) => (
                              <div
                                key={idx}
                                className="p-3 bg-white rounded-xl border border-slate-200 text-xs space-y-1 shadow-xs"
                              >
                                <div className="flex justify-between font-bold text-slate-800">
                                  <span>{s.slab}</span>
                                  <span className="text-emerald-700 font-mono">₹ {fmt(s.rate)}/u</span>
                                </div>
                                <div className="flex justify-between text-slate-500 text-[11px]">
                                  <span>Units: {s.units}</span>
                                  <span className="font-mono">₹ {fmt(s.amount)}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              </div>
            )}

            {/* ========================================================
                TAB 3: BILL UPLOAD (MOBILE CAMERA FRIENDLY)
            ======================================================== */}
            {activeTab === "upload" && (
              <div className="space-y-4 sm:space-y-6">
                <div className="bg-white p-4 sm:p-8 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-5">
                  <div>
                    <h2 className="text-lg sm:text-2xl font-black text-slate-900">
                      {lang === "te" ? "విద్యుత్ బిల్లు అప్‌లోడ్" : "Upload Electricity Bill"}
                    </h2>
                    <p className="text-xs text-slate-500 mt-1">
                      Snap a camera photo of your paper bill or select a PDF file
                    </p>
                  </div>

                  <form onSubmit={handleUpload} className="space-y-4">
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="border-2 border-dashed border-slate-300 hover:border-emerald-600 rounded-2xl sm:rounded-3xl p-6 sm:p-10 text-center transition-all bg-slate-50/70 cursor-pointer active:scale-98"
                    >
                      <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-2xl bg-emerald-100/70 flex items-center justify-center mx-auto mb-3">
                        <Camera className="w-6 h-6 sm:w-8 sm:h-8 text-emerald-800" />
                      </div>
                      <p className="text-sm sm:text-base font-black text-slate-800">
                        {uploadFile ? uploadFile.name : "Tap to Take Photo or Browse"}
                      </p>
                      <p className="text-[11px] text-slate-400 mt-1">
                        Camera photo, PDF, JPG, PNG supported
                      </p>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*,application/pdf"
                        onChange={(e) => {
                          const f = e.target.files?.[0];
                          if (f) {
                            processUploadFile(f);
                          }
                        }}
                        className="hidden"
                      />
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          fileInputRef.current?.click();
                        }}
                        className="inline-block mt-3 px-4 py-2 bg-emerald-800 text-white rounded-xl text-xs font-black shadow-md cursor-pointer"
                      >
                        {uploadFile ? "Change File" : "Choose File / Camera"}
                      </button>
                    </div>

                    {uploadFile && (
                      <div className="flex flex-col sm:flex-row justify-between items-center p-3 sm:p-4 bg-emerald-50 rounded-2xl border border-emerald-200 text-xs gap-3">
                        <span className="font-bold text-emerald-950 truncate max-w-xs">
                          {uploadFile.name} ({(uploadFile.size / 1024).toFixed(1)} KB)
                        </span>
                        <div className="flex items-center space-x-2 w-full sm:w-auto">
                          <button
                            type="button"
                            onClick={() => setUploadFile(null)}
                            className="flex-1 sm:flex-none px-3 py-2 bg-white text-slate-700 rounded-xl font-bold border"
                          >
                            Clear
                          </button>
                          <button
                            type="submit"
                            disabled={uploadLoading}
                            className="flex-1 sm:flex-none px-4 py-2 bg-emerald-800 text-white rounded-xl font-black shadow-md flex items-center justify-center space-x-1.5 disabled:opacity-50"
                          >
                            {uploadLoading ? (
                              <>
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                <span>Extracting...</span>
                              </>
                            ) : (
                              <>
                                <Check className="w-4 h-4" />
                                <span>Extract Bill</span>
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    )}
                  </form>

                  {uploadMessage && (
                    <div className="p-3.5 bg-slate-100 rounded-xl text-xs font-medium text-slate-700 border flex items-center space-x-2">
                      {uploadLoading && <RefreshCw className="w-4 h-4 animate-spin text-emerald-700 shrink-0" />}
                      <span>{uploadMessage}</span>
                    </div>
                  )}

                  {/* MODULE 4: VERIFICATION ON MOBILE */}
                  {reviewFields && (
                    <div className="p-4 sm:p-6 bg-amber-50/80 border-2 border-amber-300 rounded-2xl sm:rounded-3xl space-y-4">
                      <div>
                        <span className="px-2 py-0.5 rounded bg-amber-200 text-amber-950 font-black text-[9px] uppercase">
                          Module 4 Verification
                        </span>
                        <h3 className="font-black text-base text-slate-900 mt-1">
                          Review & Confirm Values
                        </h3>
                        <p className="text-[11px] text-slate-600">
                          Confirm meter units and dates before tariff calculation
                        </p>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                        <div>
                          <label className="font-bold text-slate-700">Service Number</label>
                          <input
                            type="text"
                            value={getFieldVal(reviewFields.service_number, "")}
                            onChange={(e) =>
                              setReviewFields({
                                ...reviewFields,
                                service_number: { value: e.target.value, confidence: 1.0 },
                              })
                            }
                            className="w-full mt-1 p-2.5 bg-white rounded-xl border border-slate-300 font-bold"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-slate-700">Units (kWh)</label>
                          <input
                            type="number"
                            value={getFieldVal(reviewFields.consumption_units, 0)}
                            onChange={(e) =>
                              setReviewFields({
                                ...reviewFields,
                                consumption_units: { value: Number(e.target.value), confidence: 1.0 },
                              })
                            }
                            className="w-full mt-1 p-2.5 bg-white rounded-xl border border-slate-300 font-black text-emerald-900"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-slate-700">Month (YYYY-MM)</label>
                          <input
                            type="text"
                            value={getFieldVal(reviewFields.billing_month, "2026-11")}
                            onChange={(e) =>
                              setReviewFields({
                                ...reviewFields,
                                billing_month: { value: e.target.value, confidence: 1.0 },
                              })
                            }
                            className="w-full mt-1 p-2.5 bg-white rounded-xl border border-slate-300 font-bold"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-slate-700">Printed Total (₹)</label>
                          <input
                            type="number"
                            step="0.01"
                            value={getFieldVal(reviewFields.printed_total, 0)}
                            onChange={(e) =>
                              setReviewFields({
                                ...reviewFields,
                                printed_total: { value: Number(e.target.value), confidence: 1.0 },
                              })
                            }
                            className="w-full mt-1 p-2.5 bg-white rounded-xl border border-slate-300 font-black text-slate-900"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-slate-700">Consumer Name</label>
                          <input
                            type="text"
                            value={getFieldVal(reviewFields.consumer_name, "")}
                            onChange={(e) =>
                              setReviewFields({
                                ...reviewFields,
                                consumer_name: { value: e.target.value, confidence: 1.0 },
                              })
                            }
                            className="w-full mt-1 p-2.5 bg-white rounded-xl border border-slate-300 font-bold"
                          />
                        </div>
                        <div>
                          <label className="font-bold text-slate-700">Category</label>
                          <input
                            type="text"
                            value={getFieldVal(reviewFields.consumer_category, "LT-I Domestic")}
                            onChange={(e) =>
                              setReviewFields({
                                ...reviewFields,
                                consumer_category: { value: e.target.value, confidence: 1.0 },
                              })
                            }
                            className="w-full mt-1 p-2.5 bg-white rounded-xl border border-slate-300 font-bold"
                          />
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 pt-1">
                        <input
                          type="checkbox"
                          id="revGjMob"
                          checked={Boolean(getFieldVal(reviewFields.gruha_jyothi_eligible, false))}
                          onChange={(e) =>
                            setReviewFields({
                              ...reviewFields,
                              gruha_jyothi_eligible: { value: e.target.checked, confidence: 1.0 },
                            })
                          }
                          className="w-4 h-4 accent-emerald-700"
                        />
                        <label htmlFor="revGjMob" className="text-xs font-bold text-slate-900">
                          Gruha Jyothi Registered Connection
                        </label>
                      </div>

                      <div className="flex space-x-2 pt-2 border-t border-amber-200">
                        <button
                          type="button"
                          onClick={() => setReviewFields(null)}
                          className="flex-1 py-2.5 bg-white rounded-xl font-bold text-xs border"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          onClick={handleSaveVerification}
                          className="flex-1 py-2.5 bg-emerald-800 text-white rounded-xl font-black text-xs shadow-md"
                        >
                          Confirm & Calculate
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ========================================================
                TAB 4: MY BILLS (MOBILE CARDS)
            ======================================================== */}
            {activeTab === "my_bills" && (
              <div className="space-y-4 sm:space-y-6">
                <div className="bg-white p-4 sm:p-8 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div>
                      <h2 className="text-lg sm:text-2xl font-black text-slate-900">
                        {lang === "te" ? "నా నమోదిత బిల్లులు" : "My Analyzed Bills"}
                      </h2>
                      <p className="text-xs text-slate-500">
                        Audit history verified against TGERC orders
                      </p>
                    </div>

                    <div className="relative w-full sm:w-64">
                      <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                      <input
                        type="text"
                        value={billSearchQuery}
                        onChange={(e) => setBillSearchQuery(e.target.value)}
                        placeholder="Search bills..."
                        className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 rounded-xl border border-slate-200"
                      />
                    </div>
                  </div>

                  {/* Mobile Stacked Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {filteredBills.map((b) => (
                      <div
                        key={b.id}
                        className="p-4 bg-slate-50/80 rounded-2xl border border-slate-200 space-y-3"
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-black text-slate-900 font-mono text-base">
                            {b.billing_month}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 font-black text-[10px]">
                            {b.utility_code}
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-xs">
                          <div>
                            <p className="text-slate-400 text-[10px]">UNITS</p>
                            <p className="font-bold text-slate-800 font-mono text-sm">{b.consumption_units} kWh</p>
                          </div>
                          <div className="text-right">
                            <p className="text-slate-400 text-[10px]">PAYABLE</p>
                            <p className="font-black text-slate-900 font-mono text-sm">₹ {fmt(b.printed_total)}</p>
                          </div>
                        </div>
                        <div className="flex justify-between items-center pt-2 border-t border-slate-200">
                          {b.is_gruha_jyothi ? (
                            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              Zero Bill
                            </span>
                          ) : (
                            <span className="text-[10px] text-slate-500 font-medium">Standard</span>
                          )}
                          <button
                            onClick={() => handleSelectBill(b.id)}
                            className="px-3.5 py-1.5 bg-emerald-800 text-white rounded-xl font-bold text-xs shadow-xs active:scale-95 cursor-pointer"
                          >
                            View Audit
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ========================================================
                TAB 5: DEEP BILL ANALYSIS (MOBILE RESPONSIVE BREAKDOWN)
            ======================================================== */}
            {activeTab === "analysis" && (
              <div className="space-y-4 sm:space-y-6">
                {calcLoading ? (
                  <div className="p-16 text-center bg-white rounded-3xl border border-slate-200">
                    <RefreshCw className="w-8 h-8 animate-spin text-emerald-700 mx-auto mb-3" />
                    <p className="font-bold text-sm text-slate-800">
                      Evaluating Tariff Rules...
                    </p>
                  </div>
                ) : calculationResult ? (
                  <>
                    {/* Top Action Bar */}
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2.5 bg-white p-3.5 sm:p-4 rounded-2xl border border-slate-200 shadow-xs">
                      <div className="flex items-center space-x-2 w-full sm:w-auto">
                        <span className="text-xs font-bold text-slate-500 uppercase">Bill:</span>
                        <select
                          value={selectedBillId || ""}
                          onChange={(e) => handleSelectBill(Number(e.target.value))}
                          className="flex-1 sm:flex-none text-xs p-2 bg-slate-50 rounded-xl border border-slate-300 font-bold"
                        >
                          {bills.map((b) => (
                            <option key={b.id} value={b.id}>
                              {b.billing_month} ({b.consumption_units}u) - ₹ {fmt(b.printed_total)}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="flex items-center space-x-2 w-full sm:w-auto">
                        <button
                          onClick={() => {
                            setActiveTab("chat");
                            setChatInput(
                              `Explain my ${calculationResult.tariff_version} bill for ${calculationResult.consumption_units} units (₹ ${fmt(calculationResult.computed_total)}).`
                            );
                          }}
                          className="flex-1 sm:flex-none justify-center px-3 py-2 bg-emerald-50 text-emerald-800 rounded-xl text-xs font-bold flex items-center space-x-1 border border-emerald-200"
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                          <span>Ask AI</span>
                        </button>
                        <button
                          onClick={() => window.print()}
                          className="flex-1 sm:flex-none justify-center px-3 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold flex items-center space-x-1"
                        >
                          <Printer className="w-3.5 h-3.5" />
                          <span>Print</span>
                        </button>
                      </div>
                    </div>

                    {/* Gruha Jyothi Banner */}
                    {calculationResult.subsidies > 0 && (
                      <div className="bg-gradient-to-r from-emerald-950 via-emerald-900 to-teal-900 text-white p-5 rounded-2xl sm:rounded-3xl shadow-lg border-2 border-amber-400 flex flex-col sm:flex-row justify-between items-center gap-3">
                        <div className="space-y-1 text-center sm:text-left">
                          <span className="text-[9px] font-black text-amber-400 uppercase tracking-widest bg-emerald-950 px-2 py-0.5 rounded border border-amber-400/40">
                            Zero Bill Scheme Active
                          </span>
                          <h3 className="text-base sm:text-xl font-black">Gruha Jyothi Benefit Applied</h3>
                          <p className="text-xs text-emerald-200/90 leading-relaxed">
                            100% bill subsidy credited in advance by Telangana Government under Section 65.
                          </p>
                        </div>
                        <div className="text-center sm:text-right bg-emerald-950/90 px-4 py-2.5 rounded-xl border border-emerald-800">
                          <p className="text-[10px] text-emerald-300">Total Subsidy</p>
                          <p className="text-xl sm:text-2xl font-black text-amber-400 font-mono">
                            ₹ {fmt(calculationResult.subsidies)}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Discrepancies */}
                    {anomalies.length > 0 && (
                      <div className="space-y-2">
                        {anomalies.map((an, idx) => (
                          <div
                            key={idx}
                            className="p-4 rounded-2xl border bg-rose-50 border-rose-300 text-rose-950 space-y-1.5 shadow-xs"
                          >
                            <div className="flex items-center space-x-2">
                              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                              <span className="font-black text-[10px] uppercase tracking-wider bg-white px-2 py-0.5 rounded border">
                                {an.issue_type}
                              </span>
                            </div>
                            <p className="font-bold text-xs sm:text-sm leading-relaxed">{an.description}</p>
                            {an.suggested_action && (
                              <p className="text-[11px] text-slate-700 bg-white/70 p-2 rounded-xl mt-1">
                                <strong>Rights: </strong>{an.suggested_action}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Explanation */}
                    <div className="bg-white p-4 sm:p-6 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-2">
                      <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                        <div className="flex items-center space-x-1.5">
                          <Sparkles className="w-4 h-4 text-amber-500 fill-current" />
                          <h4 className="font-black text-xs sm:text-sm text-slate-900">
                            Regulatory Audit Summary
                          </h4>
                        </div>
                        <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-100 rounded text-slate-600">
                          {calculationResult.tariff_version}
                        </span>
                      </div>
                      <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-sans">
                        {lang === "te"
                          ? calculationResult.explanation_te
                          : calculationResult.explanation_en}
                      </p>
                    </div>

                    {/* Itemized Charges Breakdown (Mobile Stacked Cards) */}
                    <div className="bg-white rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm p-4 sm:p-6 space-y-4">
                      <div>
                        <h4 className="font-black text-sm text-slate-900">
                          Itemized Charge Audit
                        </h4>
                        <p className="text-xs text-slate-500">
                          Category: <strong className="text-emerald-800">{calculationResult.category_determined}</strong> ({calculationResult.consumption_units} kWh)
                        </p>
                      </div>

                      <div className="space-y-2.5">
                        {itemizedCharges.map((item, idx) => (
                          <div
                            key={idx}
                            className={`p-3.5 rounded-xl border text-xs space-y-1.5 ${
                              item.is_discrepant ? "bg-rose-50/70 border-rose-200" : "bg-slate-50/80 border-slate-200"
                            }`}
                          >
                            <div className="flex justify-between items-start">
                              <span className="font-bold text-slate-900">{item.label}</span>
                              <span className="font-black text-emerald-800 font-mono text-sm">
                                ₹ {fmt(item.computed_amount)}
                              </span>
                            </div>
                            <p className="text-slate-500 text-[11px]">{item.explanation}</p>
                            {item.legal_source && (
                              <p className="text-[9px] text-slate-400 font-mono">{item.legal_source}</p>
                            )}
                          </div>
                        ))}
                      </div>

                      {/* Net Total Summary */}
                      <div className="p-4 bg-emerald-950 text-white rounded-2xl flex justify-between items-center shadow-inner">
                        <div>
                          <p className="text-[10px] text-emerald-300 font-bold uppercase">Net Amount Payable</p>
                          <p className="text-xs text-emerald-100">Including 6 ps/unit State Duty</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xl sm:text-2xl font-black text-amber-400 font-mono">
                            ₹ {fmt(calculationResult.computed_total)}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Telescopic Slabs */}
                    {energySlabs.length > 0 && (
                      <div className="bg-white p-4 sm:p-6 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-3">
                        <h4 className="font-black text-xs sm:text-sm text-slate-900">
                          Telescopic Slabs Calculation
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                          {energySlabs.map((s, idx) => (
                            <div
                              key={idx}
                              className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1"
                            >
                              <span className="font-bold text-slate-800">{s.slab}</span>
                              <div className="flex justify-between text-slate-500 text-[11px]">
                                <span>Units: {s.units}</span>
                                <span>Rate: ₹ {fmt(s.rate)}/u</span>
                              </div>
                              <p className="font-black text-emerald-800 text-sm pt-1 border-t border-slate-200 font-mono">
                                ₹ {fmt(s.amount)}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-16 text-center bg-white rounded-2xl border">
                    <p className="text-slate-500 text-xs">Select a bill from the dashboard to view audit</p>
                  </div>
                )}
              </div>
            )}

            {/* ========================================================
                TAB 6: CONSUMPTION TRENDS
            ======================================================== */}
            {activeTab === "analytics" && (
              <div className="space-y-4 sm:space-y-6">
                <div className="bg-white p-4 sm:p-8 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-4">
                  <div>
                    <h2 className="text-lg sm:text-2xl font-black text-slate-900">
                      Consumption Trends
                    </h2>
                    <p className="text-xs text-slate-500">
                      Historical consumption with Gruha Jyothi 200-unit ceiling
                    </p>
                  </div>

                  {analytics?.monthly_trend && analytics.monthly_trend.length > 0 ? (
                    <div className="h-64 sm:h-80 w-full pt-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={analytics.monthly_trend}
                          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                          <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                          <YAxis tick={{ fontSize: 10 }} />
                          <Tooltip
                            formatter={(value: any, name: any) => [
                              name === "units" ? `${value} kWh` : `₹ ${fmt(value)}`,
                              name === "units" ? "Units" : "Amount",
                            ]}
                          />
                          <ReferenceLine
                            y={200}
                            label={{ value: "200u Limit", fill: "#d97706", fontSize: 9, position: "top" }}
                            stroke="#d97706"
                            strokeDasharray="4 4"
                          />
                          <Bar dataKey="units" fill="#047857" radius={[4, 4, 0, 0]} name="Units" />
                          <Bar dataKey="amount" fill="#d97706" radius={[4, 4, 0, 0]} name="Amount" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="p-12 text-center text-slate-400 text-xs">
                      No consumption history recorded.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ========================================================
                TAB 7: SAVINGS ADVISOR
            ======================================================== */}
            {activeTab === "savings" && (
              <div className="space-y-4 sm:space-y-6">
                <div className="bg-white p-4 sm:p-8 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-5">
                  <div>
                    <h2 className="text-lg sm:text-2xl font-black text-slate-900">
                      Savings Recommendations
                    </h2>
                    <p className="text-xs text-slate-500">
                      Actionable measures with calculated Rupee savings under Telangana tariff slabs
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                    <div className="p-4 sm:p-6 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl border border-emerald-200 space-y-2">
                      <div className="flex items-center space-x-2">
                        <Award className="w-5 h-5 text-emerald-800" />
                        <h3 className="font-black text-sm text-emerald-950">Target 200 Units (Zero Bill)</h3>
                      </div>
                      <p className="text-xs text-slate-600">
                        Conserving just 5-15 units to stay at or below 200 units saves over ₹1,000 every month under Gruha Jyothi.
                      </p>
                      <div className="p-3 bg-white rounded-xl border border-emerald-200 flex justify-between items-center text-xs">
                        <span className="font-bold text-slate-700">Monthly Savings:</span>
                        <span className="text-base font-black text-emerald-700 font-mono">₹ 1,027.00+</span>
                      </div>
                    </div>

                    <div className="p-4 sm:p-6 bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-200 space-y-2">
                      <div className="flex items-center space-x-2">
                        <Flame className="w-5 h-5 text-amber-800" />
                        <h3 className="font-black text-sm text-amber-950">AC 24°C + BLDC Fan</h3>
                      </div>
                      <p className="text-xs text-slate-600">
                        Every degree below 24°C on your AC uses 6% more electricity. Setting 24°C yields instant savings.
                      </p>
                      <div className="p-3 bg-white rounded-xl border border-amber-200 flex justify-between items-center text-xs">
                        <span className="font-bold text-slate-700">Monthly Savings:</span>
                        <span className="text-base font-black text-amber-700 font-mono">₹ 350 - ₹ 500</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ========================================================
                TAB 8: ASK AI (MOBILE CHAT BUBBLES)
            ======================================================== */}
            {activeTab === "chat" && (
              <div className="space-y-4">
                <div className="bg-white p-4 sm:p-6 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-3">
                  <div className="flex justify-between items-center border-b pb-3">
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="w-5 h-5 text-emerald-800" />
                      <h2 className="text-base sm:text-xl font-black text-slate-900">
                        Bijli Mitra AI Advisor
                      </h2>
                    </div>
                    <span className="text-[10px] bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded font-black">
                      TGERC Grounded
                    </span>
                  </div>

                  {/* Message Stream */}
                  <div className="space-y-3 min-h-[280px] max-h-[55vh] overflow-y-auto p-3 sm:p-4 bg-slate-50/70 rounded-2xl border border-slate-200">
                    {chatMessages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`flex flex-col ${
                          msg.sender === "user" ? "items-end" : "items-start"
                        }`}
                      >
                        <div
                          className={`max-w-[88%] sm:max-w-xl p-3 sm:p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                            msg.sender === "user"
                              ? "bg-emerald-800 text-white rounded-br-xs"
                              : "bg-white text-slate-800 border border-slate-200 shadow-xs rounded-bl-xs"
                          }`}
                        >
                          <p>{msg.text}</p>
                          {msg.facts && msg.facts.length > 0 && (
                            <div className="mt-2.5 pt-2 border-t border-slate-100 text-[10px] text-slate-500">
                              <p className="font-bold">Sources:</p>
                              <ul className="list-disc list-inside">
                                {msg.facts.map((f, i) => (
                                  <li key={i}>{f}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        {msg.suggestions && msg.suggestions.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-2">
                            {msg.suggestions.map((q, i) => (
                              <button
                                key={i}
                                onClick={() => handleSendChat(q)}
                                className="text-[10px] px-2.5 py-1 bg-white text-emerald-900 border border-slate-200 rounded-lg shadow-xs active:scale-95"
                              >
                                {q}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}

                    {chatLoading && (
                      <div className="flex items-center space-x-1.5 text-xs text-slate-500 p-1">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-700" />
                        <span>Verifying tariff rules...</span>
                      </div>
                    )}
                  </div>

                  {/* Input */}
                  <div className="flex space-x-2 pt-1">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
                      placeholder="Ask about your bill..."
                      className="flex-1 p-3 text-xs sm:text-sm bg-slate-50 rounded-xl border border-slate-300 focus:outline-none focus:border-emerald-700"
                    />
                    <button
                      onClick={() => handleSendChat()}
                      disabled={chatLoading || !chatInput.trim()}
                      className="px-5 py-3 bg-emerald-800 text-white rounded-xl text-xs sm:text-sm font-black disabled:opacity-50 active:scale-95 cursor-pointer"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* ========================================================
                TAB 9: TARIFF SCHEDULES
            ======================================================== */}
            {activeTab === "tariffs" && (
              <div className="space-y-4">
                <div className="bg-white p-4 sm:p-8 rounded-2xl sm:rounded-3xl border border-slate-200 shadow-sm space-y-4">
                  <h2 className="text-lg sm:text-2xl font-black text-slate-900">
                    Official Tariff Schedules
                  </h2>
                  <div className="space-y-4">
                    {tariffData?.schedules?.map((sch: any, idx: number) => (
                      <div key={idx} className="p-4 bg-slate-50 rounded-2xl border space-y-2.5">
                        <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 font-bold text-[10px]">
                          {sch.financial_year}
                        </span>
                        <h3 className="font-bold text-sm text-slate-900">{sch.title}</h3>
                        <div className="overflow-x-auto rounded-xl border border-slate-200">
                          <table className="w-full text-left text-xs bg-white">
                            <thead className="bg-slate-100 font-bold border-b">
                              <tr>
                                <th className="p-2">Slab</th>
                                <th className="p-2">Range</th>
                                <th className="p-2 text-right">Rate</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {sch.slabs.map((sl: any, sIdx: number) => (
                                <tr key={sIdx}>
                                  <td className="p-2 font-bold">{sl.category}</td>
                                  <td className="p-2 font-mono text-[11px]">{sl.min_units} - {sl.max_units >= 999999 ? "Above" : sl.max_units}</td>
                                  <td className="p-2 text-right font-black text-emerald-800 font-mono">₹ {fmt(sl.rate)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* ========================================================
          STICKY MOBILE BOTTOM NAVIGATION BAR (<768px)
      ======================================================== */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-white/95 backdrop-blur-lg border-t border-slate-200 shadow-2xl px-2 py-1.5 pb-safe flex justify-around items-center">
        {[
          { id: "dashboard", icon: Home, label_en: "Home", label_te: "హోమ్" },
          { id: "simulator", icon: Calculator, label_en: "Calculate", label_te: "లెక్కించు", highlight: true },
          { id: "upload", icon: Upload, label_en: "Upload", label_te: "అప్‌లోడ్" },
          { id: "analysis", icon: ShieldCheck, label_en: "Audit", label_te: "విశ్లేషణ" },
          { id: "chat", icon: MessageSquare, label_en: "Ask AI", label_te: "ఏఐ" },
        ].map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as TabType)}
              className={`flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all cursor-pointer min-w-[56px] ${
                isActive
                  ? item.highlight
                    ? "text-amber-600 font-black"
                    : "text-emerald-800 font-black"
                  : "text-slate-500 hover:text-slate-800 font-medium"
              }`}
            >
              <div
                className={`p-1 rounded-xl transition-all ${
                  isActive
                    ? item.highlight
                      ? "bg-amber-100 text-amber-800"
                      : "bg-emerald-100 text-emerald-900"
                    : ""
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>
              <span className="text-[10px] mt-0.5 tracking-tight">
                {lang === "te" ? item.label_te : item.label_en}
              </span>
            </button>
          );
        })}
      </nav>

      {/* FOOTER */}
      <footer className="bg-gradient-to-r from-emerald-950 via-teal-950 to-emerald-950 text-emerald-200 border-t-2 border-emerald-800 py-6 text-center text-xs">
        <p className="font-black text-white">BIJLI MITRA AI — Telangana Challenge 13</p>
        <p className="text-[10px] text-emerald-400 mt-1">
          24x7 Helpline: <strong className="text-amber-400">1912 (Toll Free)</strong> • TGSPDCL & TGNPDCL
        </p>
      </footer>
    </div>
  );
}
