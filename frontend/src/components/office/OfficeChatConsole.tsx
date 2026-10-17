"use client";

import { useState, useRef, useEffect } from "react";
import { Send, AtSign, Users, X, Sparkles } from "lucide-react";
import { AgentSpatialData } from "../../lib/types/office";

interface OfficeChatConsoleProps {
  agents: AgentSpatialData[];
  replyContext?: { roleId: string; ticketId?: string } | null;
  onClearReply?: () => void;
  onSendDirective: (mentions: string[], message: string) => void;
}

export function OfficeChatConsole({
  agents,
  replyContext,
  onClearReply,
  onSendDirective,
}: OfficeChatConsoleProps) {
  const [input, setInput] = useState<string>("");
  const [showMentionMenu, setShowMentionMenu] = useState<boolean>(false);
  const [mentionFilter, setMentionFilter] = useState<string>("");
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Synchronize when replyContext is set from an Interrupt button
  useEffect(() => {
    if (replyContext) {
      const tag = `@${replyContext.roleId.replace("role_", "")} `;
      setInput(tag);
      inputRef.current?.focus();
    }
  }, [replyContext]);

  const mentionOptions = [
    { id: "all", name: "All Hands (@all)", role_id: "all", color: "#f59e0b" },
    ...agents.map((a) => ({
      id: a.role_id,
      name: `${a.name} (@${a.role_id.replace("role_", "")})`,
      role_id: a.role_id,
      color: a.color || "#06b6d4",
    })),
  ].filter((opt) => opt.name.toLowerCase().includes(mentionFilter.toLowerCase()));

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setInput(val);
    const lastAtPos = val.lastIndexOf("@");
    if (lastAtPos !== -1 && !val.slice(lastAtPos).includes(" ")) {
      setMentionFilter(val.slice(lastAtPos + 1));
      setShowMentionMenu(true);
      setSelectedIndex(0);
    } else {
      setShowMentionMenu(false);
    }
  };

  const handleSelectMention = (roleId: string) => {
    const lastAtPos = input.lastIndexOf("@");
    const prefix = input.slice(0, lastAtPos);
    const tag = roleId === "all" ? "@all " : `@${roleId.replace("role_", "")} `;
    setInput(`${prefix}${tag}`);
    setShowMentionMenu(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (showMentionMenu && mentionOptions.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % mentionOptions.length);
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + mentionOptions.length) % mentionOptions.length);
        return;
      }
      if (e.key === "Enter" || e.key === "Tab") {
        e.preventDefault();
        handleSelectMention(mentionOptions[selectedIndex].role_id);
        return;
      }
      if (e.key === "Escape") {
        setShowMentionMenu(false);
        return;
      }
    }

    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!input.trim()) return;
    const mentionsFound = Array.from(input.matchAll(/@([a-zA-Z0-9_]+)/g)).map((m) => m[1]);
    const normalizedMentions = mentionsFound.map((m) => (m === "all" ? "all" : `role_${m}`));
    onSendDirective(normalizedMentions, input.trim());
    setInput("");
    setShowMentionMenu(false);
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto z-20 select-none">
      {/* Autocomplete Popover */}
      {showMentionMenu && mentionOptions.length > 0 && (
        <div className="absolute bottom-full mb-2 left-0 w-80 max-h-56 bg-slate-900/95 border border-slate-700/80 rounded-2xl shadow-2xl backdrop-blur-xl overflow-y-auto p-1.5 space-y-1">
          <div className="px-2.5 py-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between border-b border-slate-800">
            <span>Mention Agents (Oasis Hub)</span>
            <span className="font-mono text-[9px]">Tab/Enter</span>
          </div>
          {mentionOptions.map((opt, i) => (
            <button
              key={opt.id}
              onClick={() => handleSelectMention(opt.role_id)}
              className={`w-full text-left px-2.5 py-1.5 rounded-xl flex items-center space-x-2 text-xs transition-all ${
                i === selectedIndex
                  ? "bg-indigo-600/30 text-white border border-indigo-500/40"
                  : "text-slate-300 hover:bg-slate-800/60"
              }`}
            >
              <div
                className="w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold border"
                style={{ backgroundColor: `${opt.color}20`, borderColor: `${opt.color}80`, color: opt.color }}
              >
                {opt.id === "all" ? <Users className="w-3 h-3" /> : opt.name[0]}
              </div>
              <span className="truncate font-medium">{opt.name}</span>
            </button>
          ))}
        </div>
      )}

      {/* Floating Oasis Command Console Input */}
      <div className="bg-slate-950/90 border border-slate-800/90 rounded-2xl p-1.5 pl-3.5 flex items-center shadow-2xl backdrop-blur-md focus-within:border-indigo-500/80 transition-all">
        {replyContext ? (
          <div className="flex items-center space-x-1 px-2 py-0.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[11px] font-mono mr-2">
            <span>Interrup: @{replyContext.roleId.replace("role_", "")}</span>
            {replyContext.ticketId && <span>#{replyContext.ticketId}</span>}
            {onClearReply && (
              <button onClick={onClearReply} className="hover:text-white ml-0.5">
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        ) : (
          <AtSign className="w-4 h-4 text-indigo-400 mr-2 flex-shrink-0" />
        )}

        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Dispatch instruction with @fe, @be, @cto or @all..."
          className="flex-1 bg-transparent text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none"
        />

        <button
          onClick={handleSubmit}
          disabled={!input.trim()}
          className="ml-2 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold text-xs flex items-center space-x-1.5 transition-all shadow-md shadow-indigo-600/25 active:scale-95 flex-shrink-0"
        >
          <span>Send</span>
          <Send className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
}
