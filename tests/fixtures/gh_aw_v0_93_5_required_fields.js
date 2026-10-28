// Unmodified shared validator extracted from gh-aw v0.93.5, byte offset 26489947.
// windows-amd64.exe SHA-256: e1661fa10956ed969c33b9208790b2857148699dd5f9ab97a149c605bdfb2eb6
// Tests required-field validation only, not the safe-output server or recording.
function validateRequiredFields(args, inputSchema) {
  const requiredFields = inputSchema && Array.isArray(inputSchema.required) ? inputSchema.required : [];

  if (!requiredFields.length) {
    return [];
  }

  const missing = requiredFields.filter(f => {
    const value = args[f];
    return value === undefined || value === null || (typeof value === "string" && value.trim() === "");
  });

  return missing;
}
