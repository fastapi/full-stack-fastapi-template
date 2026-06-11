"use client";

import { useEffect, useState } from "react";
import { Check, FileCheck2, FileSpreadsheet, FileText, Plus, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import Toggle from "@/components/ui/Toggle";
import { apiMessage } from "@/lib/api";
import { ApiKeysService, type ApiKeyPublic } from "@/lib/client";
import { formatDate } from "@/lib/files";

type OptKey = "autoTables" | "mergePages" | "headers" | "ocr" | "notify";

export default function SettingsView() {
  const t = useTranslations("settings");
  const tc = useTranslations("common");
  const [opts, setOpts] = useState<Record<OptKey, boolean>>({
    autoTables: true,
    mergePages: true,
    headers: true,
    ocr: false,
    notify: true,
  });
  const [fmt, setFmt] = useState<"xlsx" | "csv">("xlsx");
  const flip = (k: OptKey) => setOpts((p) => ({ ...p, [k]: !p[k] }));

  const [keys, setKeys] = useState<ApiKeyPublic[]>([]);
  const [keysLoading, setKeysLoading] = useState(true);
  const [keyName, setKeyName] = useState("");
  const [keyValue, setKeyValue] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [keyError, setKeyError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    ApiKeysService.listApiKeys()
      .then((res) => active && setKeys(res.data))
      .catch((err) => active && setKeyError(apiMessage(err)))
      .finally(() => active && setKeysLoading(false));
    return () => {
      active = false;
    };
  }, []);

  const addKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyValue.trim()) return;
    setSavingKey(true);
    setKeyError(null);
    try {
      const created = await ApiKeysService.createApiKey({
        requestBody: { name: keyName.trim() || null, key: keyValue.trim() },
      });
      setKeys((p) => [...p, created]);
      setKeyName("");
      setKeyValue("");
    } catch (err) {
      setKeyError(apiMessage(err));
    } finally {
      setSavingKey(false);
    }
  };

  const deleteKey = async (id: string) => {
    setKeyError(null);
    try {
      await ApiKeysService.deleteApiKey({ apiKeyId: id });
      setKeys((p) => p.filter((k) => k.id !== id));
    } catch (err) {
      setKeyError(apiMessage(err));
    }
  };

  const toggles: { key: OptKey; t: string; d: string }[] = [
    { key: "autoTables", t: t("autoTablesT"), d: t("autoTablesD") },
    { key: "mergePages", t: t("mergePagesT"), d: t("mergePagesD") },
    { key: "headers", t: t("headersT"), d: t("headersD") },
    { key: "ocr", t: t("ocrT"), d: t("ocrD") },
    { key: "notify", t: t("notifyT"), d: t("notifyD") },
  ];

  return (
    <div className="settings-wrap">
      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("parsingTitle")}</h3>
          <p>{t("parsingSub")}</p>
        </div>
        {toggles.map((row) => (
          <div className="set-row" key={row.key}>
            <div className="label">
              <div className="t">{row.t}</div>
              <div className="d">{row.d}</div>
            </div>
            <Toggle on={opts[row.key]} onToggle={() => flip(row.key)} label={row.t} />
          </div>
        ))}
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("formatTitle")}</h3>
          <p>{t("formatSub")}</p>
        </div>
        <div style={{ padding: "18px 22px" }}>
          <div className="fmt-select">
            <div className={`fmt-opt ${fmt === "xlsx" ? "on" : ""}`} onClick={() => setFmt("xlsx")}>
              <span className="fo-ico">
                <FileSpreadsheet size={18} />
              </span>
              <span>
                <div className="fo-t">{t("xlsxT")}</div>
                <div className="fo-d">{t("xlsxD")}</div>
              </span>
              <span className="fo-check">
                <Check size={18} />
              </span>
            </div>
            <div className={`fmt-opt ${fmt === "csv" ? "on" : ""}`} onClick={() => setFmt("csv")}>
              <span className="fo-ico">
                <FileText size={18} />
              </span>
              <span>
                <div className="fo-t">{t("csvT")}</div>
                <div className="fo-d">{t("csvD")}</div>
              </span>
              <span className="fo-check">
                <Check size={18} />
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="set-panel">
        <div className="sp-head">
          <h3>{t("apiTitle")}</h3>
          <p>{t("apiSub")}</p>
        </div>

        {keyError && (
          <div className="set-row">
            <div className="field-error" style={{ width: "100%" }}>
              {keyError}
            </div>
          </div>
        )}

        {keysLoading && (
          <div className="set-row">
            <div className="label">
              <div className="d">{tc("loading")}</div>
            </div>
          </div>
        )}
        {!keysLoading && keys.length === 0 && (
          <div className="set-row">
            <div className="label">
              <div className="d">{t("noKeys")}</div>
            </div>
          </div>
        )}
        {keys.map((k) => (
          <div className="set-row" key={k.id}>
            <div className="label">
              <div className="t" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <FileCheck2 size={15} style={{ color: "var(--cyan)" }} />
                {k.name || t("unnamedKey")}
              </div>
              <div className="d">{formatDate(k.created_at)}</div>
            </div>
            <button
              className="btn btn-ghost"
              title={t("deleteKey")}
              aria-label={t("deleteKey")}
              onClick={() => void deleteKey(k.id)}
            >
              <Trash2 size={15} />
            </button>
          </div>
        ))}

        <form className="set-row" onSubmit={addKey} style={{ gap: 10, flexWrap: "wrap" }}>
          <input
            className="auth-input"
            placeholder={t("keyNamePlaceholder")}
            value={keyName}
            onChange={(e) => setKeyName(e.target.value)}
            aria-label={t("keyNamePlaceholder")}
            style={{ minWidth: 160, flex: "0 1 180px" }}
          />
          <input
            className="auth-input"
            placeholder={t("keyValuePlaceholder")}
            value={keyValue}
            onChange={(e) => setKeyValue(e.target.value)}
            required
            aria-label={t("keyValuePlaceholder")}
            style={{ flex: "1 1 240px" }}
          />
          <button className="btn btn-primary" type="submit" disabled={savingKey}>
            <Plus size={15} /> {t("addKey")}
          </button>
        </form>
      </div>
    </div>
  );
}
