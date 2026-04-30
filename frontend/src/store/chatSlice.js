import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { applyAiUpdate } from "./formSlice";

export const sendMessage = createAsyncThunk(
  "chat/sendMessage",
  async (text, { dispatch, getState }) => {
    const current = getState().form;
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, current }),
    });
    if (!res.ok) {
      throw new Error(`Backend error ${res.status}`);
    }
    const data = await res.json();
    dispatch(applyAiUpdate(data));
    return data;
  }
);

const initialState = {
  messages: [
    {
      sender: "ai",
      text:
        'Hi! Describe your interaction (e.g., "Met Dr. Smith today, discussed Product X efficacy. Sentiment was positive and I shared brochures.").',
    },
  ],
  status: "idle",
  error: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ sender: "user", text: action.payload });
    },
    addAiMessage(state, action) {
      state.messages.push({ sender: "ai", text: action.payload });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = "idle";
        const data = action.payload || {};
        const missing = data?.validation?.missing_fields || [];
        let aiText;
        if (data.summary && missing.length === 0) {
          aiText = `Logged. ${data.summary}${data.saved_id ? ` (saved as #${data.saved_id})` : ""}`;
        } else if (missing.length > 0) {
          aiText = `Updated the form. Still missing: ${missing.join(", ")}.`;
        } else {
          aiText = "Updated the form.";
        }
        state.messages.push({ sender: "ai", text: aiText });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message;
        state.messages.push({
          sender: "ai",
          text: `Sorry, something went wrong: ${action.error.message}`,
        });
      });
  },
});

export const { addUserMessage, addAiMessage } = chatSlice.actions;
export default chatSlice.reducer;
