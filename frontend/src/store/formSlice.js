import { createSlice } from "@reduxjs/toolkit";

const emptyForm = {
  hcp_name: "",
  date: "",
  interaction_type: "",
  attendees: "",
  topics: "",
  sentiment: "",
  materials_shared: false,
  summary: "",
  validation: null,
  saved_id: null,
};

const formSlice = createSlice({
  name: "form",
  initialState: emptyForm,
  reducers: {
    applyAiUpdate(state, action) {
      const data = action.payload || {};
      // Merge only non-null fields so the "edit" flow keeps existing values.
      for (const key of Object.keys(emptyForm)) {
        if (data[key] !== undefined && data[key] !== null) {
          state[key] = data[key];
        }
      }
    },
    setField(state, action) {
      const { field, value } = action.payload;
      state[field] = value;
    },
    resetForm() {
      return { ...emptyForm };
    },
  },
});

export const { applyAiUpdate, setField, resetForm } = formSlice.actions;
export default formSlice.reducer;
