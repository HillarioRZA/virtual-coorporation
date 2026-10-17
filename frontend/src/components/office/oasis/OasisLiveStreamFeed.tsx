"use client";

import { useEffect, useRef, useMemo, useState } from "react";
import { Radio, Sparkles, Filter, ArrowDown } from "lucide-react";
import { OasisStreamCategory, OasisStreamEvent } from "../../../lib/types/office";
import { OasisEventCard } from "./OasisEventCard";

interface OasisLiveStreamFeedProps {
  events: OasisStreamEvent[];
  selectedProjectId: string;
  categoryFilter: OasisStreamCategory;
  onInterrupt: (roleId: string, ticketId?: string) => void;
  onHold: (ticketId: string) => void;
  onWatchScreen: (roleId: string) => void;
  onApproveGate?: (ticketId: string) => void;
}

export function OasisLiveStreamFeed({
  events,
  selectedProjectId,
  categoryFilter,
  onInterrupt,
  onHold,
  onWatchScreen,
  onApproveGate,
}: OasisLiveStreamFeedProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);

  // Filter events based on active project and selected category
  const filteredEvents = useMemo(() => {
    return events.filter((evt) => {
      if (selectedProjectId !== "all" && evt.projectId !== selectedProjectId) return false;
      if (categoryFilter === "ALL") return true;
      return evt.category === categoryFilter;
    });
  }, [events, selectedProjectId, categoryFilter]);

  // Handle user scroll detection
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 60;
    setAutoScroll(isAtBottom);
  };

  // Auto-scroll when new events arrive if user hasn't scrolled up
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [filteredEvents, autoScroll]);

  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" });
      setAutoScroll(true);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950/60 rounded-2xl border border-slate-800/90 overflow-hidden relative shadow-2xl backdrop-blur-xl">
      {/* Stream Header */}
      <div className="px-4 py-3 border-b border-slate-800/80 bg-slate-900/60 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-2">
          <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
          <h2 className="text-xs font-bold text-white tracking-wide uppercase">
            Oasis Live Multi-Agent Stream
          </h2>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
            {filteredEvents.length} events
          </span>
        </div>
        <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <span>Category: <strong className="text-slate-200">{categoryFilter}</strong></span>
        </div>
      </div>

      {/* Events List Feed */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 p-3.5 space-y-3 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800"
      >
        {filteredEvents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200">Listening to Autonomous Venture Stream...</p>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Gunakan konsol input <span className="text-indigo-400 font-mono">@mention</span> di bawah atau panggil <span className="text-amber-400 font-mono">All Hands</span> untuk berinteraksi langsung dengan para agen.
              </p>
            </div>
          </div>
        ) : (
          filteredEvents.map((evt) => (
            <OasisEventCard
              key={evt.id}
              event={evt}
              onInterrupt={onInterrupt}
              onHold={onHold}
              onWatchScreen={onWatchScreen}
              onApproveGate={onApproveGate}
            />
          ))
        )}
      </div>

      {/* Scroll to bottom button if user scrolled up */}
      {!autoScroll && filteredEvents.length > 0 && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-3 right-5 px-3 py-1.5 rounded-full bg-indigo-600/90 hover:bg-indigo-600 text-white text-xs font-semibold shadow-xl flex items-center space-x-1.5 backdrop-blur-md transition-all active:scale-95 animate-bounce"
        >
          <ArrowDown className="w-3.5 h-3.5" />
          <span>New events below</span>
        </button>
      )}
    </div>
  );
}
