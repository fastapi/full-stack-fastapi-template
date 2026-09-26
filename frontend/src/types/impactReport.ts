export type Severity = "high" | "medium" | "low";
export type VerifyStatus = "pass" | "fail";
export type ChangeType =
  | "field_renamed"
  | "field_type_changed"
  | "field_added_required"
  | "field_removed"
  | "endpoint_removed";

export interface ImpactReport {
  change_id: string;
  change_type: ChangeType;
  endpoint: string;
  method: string;
  summary_plain_english: string;
  severity: Severity;
  affected_files: string[];
  patch_applied: boolean;
  patch_description: string;
  verify_status: VerifyStatus;
  verify_log: string;
  old_schema_fragment: Record<string, unknown> | null;
  new_schema_fragment: Record<string, unknown> | null;
  detected_at: string;
}