import "./App.css";
import { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { sendMessage, addUserMessage } from "./store/chatSlice";
import { setField, resetForm } from "./store/formSlice";

function App() {
  const dispatch = useDispatch();
  const form = useSelector((s) => s.form);
  const { messages, status } = useSelector((s) => s.chat);

  const [input, setInput] = useState("");
  const [time, setTime] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || status === "loading") return;
    dispatch(addUserMessage(text));
    dispatch(sendMessage(text));
    setInput("");
  };

  const update = (field) => (e) => {
    const value =
      e.target.type === "checkbox" ? e.target.checked : e.target.value;
    dispatch(setField({ field, value }));
  };

  return (
    <div className="container">
      <div className="left-panel">
        <div className="page-header">
          <h1 className="page-title">Log HCP Interaction</h1>
          <button
            className="ghost-button"
            onClick={() => dispatch(resetForm())}
          >
            Clear
          </button>
        </div>

        <h2 className="section-title">Interaction Details</h2>

        <div className="row">
          <div className="form-group" style={{ flex: 1 }}>
            <label>HCP Name</label>
            <input
              value={form.hcp_name || ""}
              onChange={update("hcp_name")}
              placeholder="Search or select HCP..."
            />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Interaction Type</label>
            <select
              value={form.interaction_type || ""}
              onChange={update("interaction_type")}
            >
              <option value="">Select</option>
              <option value="Meeting">Meeting</option>
              <option value="Call">Call</option>
              <option value="Email">Email</option>
            </select>
          </div>
        </div>

        <div className="row">
          <div className="form-group" style={{ flex: 1 }}>
            <label>Date</label>
            <input
              type="date"
              value={form.date || ""}
              onChange={update("date")}
            />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Time</label>
            <input
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Attendees</label>
          <input
            value={form.attendees || ""}
            onChange={update("attendees")}
            placeholder="Enter names or search..."
          />
        </div>

        <div className="form-group">
          <label>Topics Discussed</label>
          <textarea
            value={form.topics || ""}
            onChange={update("topics")}
            placeholder="Enter key discussion points..."
          />
          <a className="voice-link" href="#voice" onClick={(e) => e.preventDefault()}>
            <span role="img" aria-label="mic">🎙️</span> Summarize from Voice Note (Requires Consent)
          </a>
        </div>

        <h2 className="section-title">Materials Shared / Samples Distributed</h2>

        <div className="form-group">
          <label>Materials Shared</label>
          <div className="checkbox">
            <input
              type="checkbox"
              checked={!!form.materials_shared}
              onChange={update("materials_shared")}
            />
            <span>Brochures shared</span>
          </div>
        </div>

        <div className="form-group">
          <label>Sentiment</label>
          <input
            value={form.sentiment || ""}
            onChange={update("sentiment")}
            placeholder="positive / neutral / negative"
          />
        </div>

        {form.summary && (
          <div className="form-group">
            <label>Summary</label>
            <div className="readonly-field summary">{form.summary}</div>
          </div>
        )}

        {form.validation && (
          <div
            className={`status-banner ${
              form.validation.is_valid ? "ok" : "warn"
            }`}
          >
            {form.validation.is_valid
              ? `Saved${form.saved_id ? ` (#${form.saved_id})` : ""}`
              : `Missing: ${form.validation.missing_fields.join(", ")}`}
          </div>
        )}
      </div>

      <div className="right-panel">
        <div className="chat-header">
          <div className="chat-title">
            <span role="img" aria-label="bot">🤖</span> AI Assistant
          </div>
          <div className="chat-subtitle">Log Interaction details here via chat</div>
        </div>

        <div className="chat-history">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={msg.sender === "user" ? "chat-user" : "chat-ai"}
            >
              {msg.text}
            </div>
          ))}
          {status === "loading" && (
            <div className="chat-ai typing">Thinking…</div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-row">
          <input
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe Interaction..."
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={status === "loading"}
          />
          <button
            className="send-button"
            onClick={handleSend}
            disabled={status === "loading"}
            aria-label="Send"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
