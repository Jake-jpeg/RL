"use client";

import { useState, useRef, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { 
  loadSession, 
  createSession, 
  saveSession, 
  type SessionData,
  type Phase1Data,
  type Phase2Data,
  type Phase3Data,
} from "../../lib/session";

// PDF Service URL - set this in your environment variables
const PDF_SERVICE_URL = process.env.NEXT_PUBLIC_PDF_SERVICE_URL || "http://localhost:8080";

function FormsContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  
  const [isValidating, setIsValidating] = useState(true);
  const [isValid, setIsValid] = useState(false);
  const [paymentIntentId, setPaymentIntentId] = useState<string | null>(null);
  const [session, setSession] = useState<SessionData | null>(null);
  
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const [currentPhase, setCurrentPhase] = useState<1 | 2 | 3>(1);
  const [phase1Data, setPhase1Data] = useState<Partial<Phase1Data>>({});
  const [phase2Data, setPhase2Data] = useState<Partial<Phase2Data>>({});
  const [phase3Data, setPhase3Data] = useState<Partial<Phase3Data>>({});
  const [phase1Complete, setPhase1Complete] = useState(false);
  const [phase2Complete, setPhase2Complete] = useState(false);
  const [phase3Complete, setPhase3Complete] = useState(false);
  const [isDisqualified, setIsDisqualified] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const validateSession = async () => {
      if (!sessionId) { setIsValidating(false); return; }
      try {
        const res = await fetch("/api/validate-session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessionId }),
        });
        const data = await res.json();
        if (data.valid && data.paymentIntentId) {
          setIsValid(true);
          setPaymentIntentId(data.paymentIntentId);
          let existingSession = loadSession(data.paymentIntentId);
          if (!existingSession) existingSession = createSession(data.paymentIntentId);
          setSession(existingSession);
          setCurrentPhase(existingSession.currentPhase);
          setPhase1Data(existingSession.phase1Data || {});
          setPhase2Data(existingSession.phase2Data || {});
          setPhase3Data(existingSession.phase3Data || {});
          setPhase1Complete(existingSession.phase1Complete);
          setPhase2Complete(existingSession.phase2Complete);
          setPhase3Complete(existingSession.phase3Complete);
          setMessages(existingSession.chatHistory || []);
          setIsDisqualified(existingSession.disqualified);
          if (existingSession.chatHistory.length === 0) setTimeout(() => sendInitialGreeting(), 500);
        }
      } catch (error) { console.error("Session validation error:", error); }
      finally { setIsValidating(false); }
    };
    validateSession();
  }, [sessionId]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  useEffect(() => {
    if (paymentIntentId && messages.length > 0) {
      const updatedSession: SessionData = {
        paymentIntentId,
        createdAt: session?.createdAt || new Date().toISOString(),
        lastUpdated: new Date().toISOString(),
        currentPhase, phase1Complete, phase2Complete, phase3Complete,
        phase1Data, phase2Data, phase3Data,
        disqualified: isDisqualified, disqualifyReason: '', chatHistory: messages,
      };
      saveSession(updatedSession);
    }
  }, [phase1Data, phase2Data, phase3Data, messages, currentPhase, phase1Complete, phase2Complete, phase3Complete, paymentIntentId, isDisqualified]);

  const sendInitialGreeting = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/forms/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [{ role: "user", content: "Hi, I'm ready to start." }], currentPhase: 1, phase1Data: {}, phase2Data: {}, phase3Data: {} }),
      });
      const data = await res.json();
      setMessages([{ role: "assistant", content: data.reply }]);
    } catch { setMessages([{ role: "assistant", content: "Welcome! Let's start Phase 1 - the Summons with Notice (UD-1). What is the Plaintiff's full legal name?" }]); }
    finally { setIsLoading(false); }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const userMessage = input.trim();
    
    // Check if user wants to restart/go back
    const restartKeywords = ['start over', 'restart', 'go back', 'made a mistake', 'redo', 'begin again', 'phase 1 again'];
    const wantsRestart = restartKeywords.some(kw => userMessage.toLowerCase().includes(kw));
    
    if (wantsRestart && currentPhase > 1) {
      setInput("");
      resetToPhase1();
      return;
    }
    
    setInput("");
    const newMessages = [...messages, { role: "user" as const, content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);
    try {
      const res = await fetch("/api/forms/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newMessages, currentPhase, phase1Data, phase2Data, phase3Data }),
      });
      const data = await res.json();
      if (data.extractedData) {
        // Route fields to correct phase based on field name, not current phase
        const phase1Fields = ['plaintiffName', 'defendantName', 'qualifyingCounty', 'qualifyingParty', 
                             'qualifyingAddress', 'plaintiffPhone', 'plaintiffAddress', 'defendantAddress', 'ceremonyType'];
        const phase2Fields = ['indexNumber', 'marriageDate', 'marriageCity', 'marriageState', 'breakdownDate', 'hasWaiver'];
        const phase3Fields = ['judgmentEntryDate', 'defendantCurrentAddress'];
        
        const p1Data: Record<string, string> = {};
        const p2Data: Record<string, string> = {};
        const p3Data: Record<string, string> = {};
        
        for (const [key, value] of Object.entries(data.extractedData)) {
          if (phase1Fields.includes(key)) p1Data[key] = value as string;
          else if (phase2Fields.includes(key)) p2Data[key] = value as string;
          else if (phase3Fields.includes(key)) p3Data[key] = value as string;
        }
        
        if (Object.keys(p1Data).length > 0) setPhase1Data(prev => ({ ...prev, ...p1Data }));
        if (Object.keys(p2Data).length > 0) setPhase2Data(prev => ({ ...prev, ...p2Data }));
        if (Object.keys(p3Data).length > 0) setPhase3Data(prev => ({ ...prev, ...p3Data }));
      }
      if (data.phase1Complete) setPhase1Complete(true);
      if (data.phase2Complete) setPhase2Complete(true);
      if (data.phase3Complete) setPhase3Complete(true);
      if (data.isDisqualified) setIsDisqualified(true);
      setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
    } catch { setMessages(prev => [...prev, { role: "assistant", content: "Sorry, something went wrong." }]); }
    finally { setIsLoading(false); inputRef.current?.focus(); }
  };

  const advancePhase = () => {
    if (currentPhase === 1 && phase1Complete) {
      setCurrentPhase(2);
      setMessages(prev => [...prev, { role: "assistant", content: "Welcome to Phase 2! What is your Index Number? (Format: 12345/2026)" }]);
    } else if (currentPhase === 2 && phase2Complete) {
      setCurrentPhase(3);
      setMessages(prev => [...prev, { role: "assistant", content: "Welcome to Phase 3! What date was the Judgment entered?" }]);
    }
  };

  const resetToPhase1 = () => {
    setCurrentPhase(1);
    setPhase1Data({});
    setPhase1Complete(false);
    setPhase2Data({});
    setPhase2Complete(false);
    setPhase3Data({});
    setPhase3Complete(false);
    setMessages(prev => [...prev, { role: "assistant", content: "No problem! Let's start fresh with Phase 1. What is the Plaintiff's full legal name? (Please provide it in English, exactly as it appears on your driver's license or government-issued ID)" }]);
  };

  const generateDocuments = async () => {
    setIsGenerating(true);
    try {
      if (currentPhase === 1) {
        // Generate UD-1 (still using local API since it's pdf-lib based)
        const res = await fetch("/api/forms/ud1", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            plaintiffName: phase1Data.plaintiffName,
            defendantName: phase1Data.defendantName,
            filingCounty: phase1Data.qualifyingCounty,
            qualifyingParty: phase1Data.qualifyingParty,
            qualifyingAddress: phase1Data.qualifyingAddress,
            plaintiffAddress: phase1Data.plaintiffAddress,
            plaintiffPhone: phase1Data.plaintiffPhone || '',
          }),
        });
        if (!res.ok) throw new Error("Failed to generate UD-1");
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `UD-1_Summons_${(phase1Data.plaintiffName || "Document").replace(/\s+/g, "_")}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else if (currentPhase === 2) {
        // Generate Phase 2 package using Python PDF microservice
        const formData = {
          plaintiffName: phase1Data.plaintiffName || '',
          defendantName: phase1Data.defendantName || '',
          county: phase1Data.qualifyingCounty || '',
          indexNumber: phase2Data.indexNumber || '',
          plaintiffAddress: phase1Data.plaintiffAddress || '',
          defendantAddress: phase1Data.defendantAddress || '',
          marriageDate: phase2Data.marriageDate || '',
          marriageCity: phase2Data.marriageCity || '',
          marriageState: phase2Data.marriageState || '',
          marriagePlace: `${phase2Data.marriageCity || ''}, ${phase2Data.marriageState || ''}`,
          breakdownDate: phase2Data.breakdownDate || '',
          religiousCeremony: phase1Data.ceremonyType === 'religious',
          // Additional fields for UD-5, UD-6
          serviceWithinNY: true,
          defendantAppeared: true,
          residencyType: 'A',
        };
        
        try {
          const res = await fetch(`${PDF_SERVICE_URL}/generate/phase2-package`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
          });
          
          if (!res.ok) {
            const error = await res.json();
            throw new Error(error.error || "Failed to generate package");
          }
          
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `Phase2_Filing_Package_${(phase1Data.plaintiffName || "Document").replace(/\s+/g, "_")}.zip`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          
          const formCount = phase1Data.ceremonyType === 'religious' ? 8 : 7;
          alert(`Downloaded ${formCount} forms in ZIP package:\n• UD-5 Affirmation of Regularity\n• UD-6 Affidavit of Plaintiff\n• UD-7 Affidavit of Defendant\n• UD-9 Note of Issue\n• UD-10 Findings of Fact\n• UD-11 Judgment of Divorce\n• UD-12 Part 130 Certification${phase1Data.ceremonyType === 'religious' ? '\n• UD-4 Barriers to Remarriage' : ''}`);
        } catch (error) {
          console.error('PDF generation error:', error);
          alert('Failed to generate PDFs. Please try again.');
        }
      } else if (currentPhase === 3) {
        // Generate Phase 3 package using Python PDF microservice
        const formData = {
          plaintiffName: phase1Data.plaintiffName || '',
          defendantName: phase1Data.defendantName || '',
          county: phase1Data.qualifyingCounty || '',
          indexNumber: phase2Data.indexNumber || '',
          plaintiffAddress: phase1Data.plaintiffAddress || '',
          defendantAddress: phase1Data.defendantAddress || '',
          defendantCurrentAddress: phase3Data.defendantCurrentAddress || phase1Data.defendantAddress || '',
        };
        
        try {
          const res = await fetch(`${PDF_SERVICE_URL}/generate/phase3-package`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
          });
          
          if (!res.ok) {
            const error = await res.json();
            throw new Error(error.error || "Failed to generate package");
          }
          
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `Phase3_Final_Forms_${(phase1Data.plaintiffName || "Document").replace(/\s+/g, "_")}.zip`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          
          alert(`Downloaded Phase 3 forms:\n• UD-14 Notice of Entry\n• UD-15 Affidavit of Service by Mail`);
        } catch (error) {
          console.error('PDF generation error:', error);
          alert('Failed to generate PDFs. Please try again.');
        }
      }
    } catch (error) {
      console.error("Document generation error:", error);
      alert("Failed to generate document. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const phase1Fields = [
    { key: 'plaintiffName', label: 'Plaintiff Name', desc: 'Person filing' },
    { key: 'defendantName', label: 'Defendant Name', desc: 'Other spouse' },
    { key: 'qualifyingCounty', label: 'Filing County', desc: 'Where to file' },
    { key: 'qualifyingParty', label: 'Residency Basis', desc: 'Who qualifies' },
    { key: 'qualifyingAddress', label: 'Qualifying Address', desc: 'Residency address' },
    { key: 'plaintiffPhone', label: 'Phone', desc: 'Court contact' },
    { key: 'plaintiffAddress', label: 'Plaintiff Address', desc: 'Mailing address' },
    { key: 'defendantAddress', label: 'Defendant Address', desc: 'Service address' },
    { key: 'ceremonyType', label: 'Ceremony Type', desc: 'Civil or Religious' },
  ];

  const phase2Fields = [
    { key: 'indexNumber', label: 'Index Number', desc: 'From clerk' },
    { key: 'marriageDate', label: 'Marriage Date', desc: 'When married' },
    { key: 'marriageCity', label: 'Marriage City', desc: 'Where married' },
    { key: 'marriageState', label: 'Marriage State', desc: 'State/Country' },
    { key: 'breakdownDate', label: 'Breakdown Date', desc: 'DRL §170(7)' },
    ...(phase1Data.ceremonyType === 'religious' ? [{ key: 'hasWaiver', label: 'DRL §253 Waiver', desc: 'Barriers check' }] : []),
  ];

  const phase3Fields = [
    { key: 'judgmentEntryDate', label: 'Entry Date', desc: 'JOD filed date' },
    { key: 'defendantCurrentAddress', label: 'Current Address', desc: 'For mailing' },
  ];

  const getPhaseData = (p: number) => p === 1 ? phase1Data : p === 2 ? phase2Data : phase3Data;
  const getPhaseFields = (p: number) => p === 1 ? phase1Fields : p === 2 ? phase2Fields : phase3Fields;
  const currentFields = getPhaseFields(currentPhase);
  const currentData = getPhaseData(currentPhase) as Record<string, string | undefined>;
  const completedCount = currentFields.filter(f => currentData[f.key]).length;

  if (isValidating) return <div className="flex min-h-screen items-center justify-center bg-zinc-50"><div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-[#1a365d] border-t-transparent" /></div>;
  if (!isValid || !sessionId) return <div className="flex min-h-screen items-center justify-center bg-zinc-50 p-4"><div className="text-center"><h2 className="text-xl font-bold">Session Not Found</h2><Link href="/qualify" className="mt-4 inline-block rounded-full bg-[#c59d5f] px-6 py-3 text-white">Start Over</Link></div></div>;

  return (
    <div className="flex min-h-screen flex-col bg-zinc-50">
      <header className="sticky top-0 z-50 border-b border-zinc-100 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#1a365d] to-[#2c5282]"><span className="text-lg">⚖️</span></div>
            <div><h1 className="text-lg font-semibold text-zinc-900">DivorceGPT</h1><p className="text-xs text-zinc-500">Phase {currentPhase}: {currentPhase === 1 ? 'Commencement' : currentPhase === 2 ? 'Submission' : 'Post-Judgment'}</p></div>
          </Link>
          <div className="hidden items-center gap-2 sm:flex"><div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" /><span className="text-sm text-zinc-500">Session active</span></div>
        </div>
      </header>

      <main className="flex flex-1 flex-col lg:flex-row">
        <div className="flex flex-1 flex-col lg:w-2/3 lg:border-r lg:border-zinc-200">
          <div className="flex-1 overflow-y-auto p-4 sm:p-6">
            <div className="mx-auto max-w-2xl space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${msg.role === "user" ? "bg-gradient-to-br from-[#1a365d] to-[#2c5282] text-white" : "bg-white text-zinc-800 ring-1 ring-zinc-100"}`}>
                    <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isLoading && <div className="flex justify-start"><div className="rounded-2xl bg-white px-4 py-3 ring-1 ring-zinc-100"><div className="flex gap-1"><div className="h-2 w-2 animate-bounce rounded-full bg-[#c59d5f]" /><div className="h-2 w-2 animate-bounce rounded-full bg-[#c59d5f] [animation-delay:0.15s]" /><div className="h-2 w-2 animate-bounce rounded-full bg-[#c59d5f] [animation-delay:0.3s]" /></div></div></div>}
              <div ref={messagesEndRef} />
            </div>
          </div>
          <div className="border-t border-zinc-100 bg-white/80 p-4">
            <div className="mx-auto max-w-2xl flex gap-3">
              <input ref={inputRef} type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && sendMessage()} placeholder="Type your answer..." className="flex-1 rounded-full bg-zinc-100 px-5 py-3 text-zinc-900 ring-1 ring-zinc-200 focus:outline-none focus:ring-2 focus:ring-[#c59d5f]" />
              <button onClick={sendMessage} disabled={isLoading || !input.trim()} className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[#1a365d] to-[#2c5282] text-white disabled:opacity-50">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" /></svg>
              </button>
            </div>
          </div>
        </div>

        <div className="border-t border-zinc-200 bg-white p-4 sm:p-6 lg:w-1/3 lg:border-t-0 lg:overflow-y-auto">
          <div className="mx-auto max-w-md">
            <div className="mb-6">
              <div className="text-xs font-medium text-zinc-500 mb-2">DIVORCE WORKFLOW</div>
              <div className="flex gap-1">{[1, 2, 3].map((p) => (<div key={p} className={`flex-1 h-2 rounded-full ${p < currentPhase ? 'bg-green-500' : p === currentPhase ? 'bg-[#c59d5f]' : 'bg-zinc-200'}`} />))}</div>
              <div className="flex justify-between mt-1 text-xs text-zinc-400"><span>Commence</span><span>Submit</span><span>Finalize</span></div>
            </div>

            <div className="flex items-center justify-between mb-4">
              <div><h2 className="text-lg font-bold text-zinc-900">Phase {currentPhase}</h2><p className="text-sm text-zinc-500">{currentPhase === 1 ? 'UD-1 Summons' : currentPhase === 2 ? 'Filing Package' : 'Notice & Service'}</p></div>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100 text-lg font-bold text-zinc-700">{completedCount}/{currentFields.length}</div>
            </div>
            
            <div className="mb-6 h-2 w-full overflow-hidden rounded-full bg-zinc-200"><div className="h-full bg-gradient-to-r from-[#1a365d] to-[#c59d5f] transition-all" style={{ width: `${(completedCount / currentFields.length) * 100}%` }} /></div>

            <div className="mb-6 rounded-xl bg-zinc-50 p-4">
              <h3 className="text-sm font-semibold text-zinc-700 mb-3">FORMS</h3>
              <div className="space-y-2 text-sm">
                {currentPhase === 1 && <FormItem label="UD-1" desc="Summons with Notice" done={phase1Complete} />}
                {currentPhase === 2 && (<>
                  {phase1Data.ceremonyType === 'religious' && <FormItem label="UD-4" desc="DRL §253 Barriers" done={!!phase2Data.hasWaiver} highlight />}
                  <FormItem label="UD-5" desc="Affirmation of Regularity" done={phase2Complete} />
                  <FormItem label="UD-6" desc="Plaintiff's Affidavit" done={phase2Complete} />
                  <FormItem label="UD-7" desc="Defendant's Affidavit" done={phase2Complete} />
                  <FormItem label="UD-9" desc="Note of Issue" done={phase2Complete} />
                  <FormItem label="UD-10" desc="Findings of Fact" done={phase2Complete} />
                  <FormItem label="UD-11" desc="Judgment of Divorce" done={phase2Complete} />
                  <FormItem label="UD-12" desc="Part 130 Certification" done={phase2Complete} />
                </>)}
                {currentPhase === 3 && (<><FormItem label="UD-14" desc="Notice of Entry" done={phase3Complete} /><FormItem label="UD-15" desc="Affidavit of Service" done={phase3Complete} /></>)}
              </div>
            </div>
            
            <div className="space-y-3">{currentFields.map((f) => (<FieldCard key={f.key} label={f.label} value={currentData[f.key]} description={f.desc} />))}</div>

            {(currentPhase === 1 && phase1Complete) && (
              <div className="mt-6 space-y-3">
                <button onClick={generateDocuments} disabled={isGenerating} className="w-full rounded-full bg-[#c59d5f] py-4 text-lg font-semibold text-white shadow-xl disabled:opacity-50">{isGenerating ? 'Generating...' : 'Download UD-1'}</button>
                <button onClick={advancePhase} className="w-full rounded-full border-2 border-[#1a365d] py-3 text-sm font-semibold text-[#1a365d] hover:bg-[#1a365d] hover:text-white">I have my Index Number → Phase 2</button>
                <button onClick={resetToPhase1} className="w-full text-sm text-zinc-500 hover:text-zinc-700 underline">Start over</button>
              </div>
            )}
            {(currentPhase === 2 && !phase2Complete) && (
              <div className="mt-6">
                <button onClick={resetToPhase1} className="w-full text-sm text-zinc-500 hover:text-zinc-700 underline">← Go back to Phase 1</button>
              </div>
            )}
            {(currentPhase === 2 && phase2Complete) && (
              <div className="mt-6 space-y-3">
                <button onClick={generateDocuments} disabled={isGenerating} className="w-full rounded-full bg-[#c59d5f] py-4 text-lg font-semibold text-white shadow-xl disabled:opacity-50">{isGenerating ? 'Generating...' : 'Download Package'}</button>
                <button onClick={advancePhase} className="w-full rounded-full border-2 border-[#1a365d] py-3 text-sm font-semibold text-[#1a365d] hover:bg-[#1a365d] hover:text-white">Judgment Entered → Phase 3</button>
              </div>
            )}
            {(currentPhase === 3 && !phase3Complete) && (
              <div className="mt-6">
                <button onClick={() => { setCurrentPhase(2); }} className="w-full text-sm text-zinc-500 hover:text-zinc-700 underline">← Go back to Phase 2</button>
              </div>
            )}
            {(currentPhase === 3 && phase3Complete) && (<button onClick={generateDocuments} disabled={isGenerating} className="mt-6 w-full rounded-full bg-green-600 py-4 text-lg font-semibold text-white shadow-xl disabled:opacity-50">{isGenerating ? 'Generating...' : '✓ Download Final Forms'}</button>)}

            <div className="mt-6 rounded-xl bg-blue-50 p-4"><div className="flex gap-3"><svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg><div className="text-sm text-blue-800"><p className="font-medium">Need help?</p><p className="text-blue-700">Just ask in the chat!</p></div></div></div>
          </div>
        </div>
      </main>

      <footer className="border-t border-zinc-100 bg-white py-4"><p className="text-center text-xs text-zinc-500">DivorceGPT is a document preparation service. This is not legal advice.</p></footer>
    </div>
  );
}

function FormItem({ label, desc, done, highlight }: { label: string; desc: string; done: boolean; highlight?: boolean }) {
  return (
    <div className={`flex items-center justify-between py-1 ${highlight ? 'text-amber-700' : ''}`}>
      <div className="flex items-center gap-2">
        {done ? <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth="2.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg> : <div className={`h-4 w-4 rounded-full border-2 ${highlight ? 'border-amber-400' : 'border-zinc-300'}`} />}
        <span className="font-medium">{label}</span>
      </div>
      <span className={`text-xs ${highlight ? 'text-amber-600' : 'text-zinc-400'}`}>{desc}</span>
    </div>
  );
}

function FieldCard({ label, value, description }: { label: string; value?: string; description: string }) {
  const done = !!value;
  return (
    <div className={`rounded-xl p-4 ${done ? "bg-green-50 ring-1 ring-green-200" : "bg-zinc-50 ring-1 ring-zinc-200"}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1"><span className="text-sm font-medium text-zinc-700">{label}</span>{done ? <p className="mt-1 truncate text-sm text-zinc-900">{value}</p> : <p className="mt-1 text-xs text-zinc-400">{description}</p>}</div>
        {done ? <div className="flex h-6 w-6 items-center justify-center rounded-full bg-green-500"><svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" strokeWidth="2.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg></div> : <div className="flex h-6 w-6 items-center justify-center rounded-full bg-zinc-200"><span className="text-xs text-zinc-400">...</span></div>}
      </div>
    </div>
  );
}

export default function FormsPage() {
  return (<Suspense fallback={<div className="flex min-h-screen items-center justify-center bg-zinc-50"><div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-[#1a365d] border-t-transparent" /></div>}><FormsContent /></Suspense>);
}
