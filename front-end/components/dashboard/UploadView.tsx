"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Download, FilePlus2, FileText, RefreshCw, Sparkles, UploadCloud, X } from "lucide-react";
import { useTranslations } from "next-intl";

type FileStatus = "queued" | "parsing" | "done";

interface QueuedFile {
  uid: number;
  name: string;
  size: string;
  isImg: boolean;
  url: string | null;
  progress: number;
  status: FileStatus;
}

let uidSeq = 0;

export default function UploadView() {
  const t = useTranslations("upload");
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState<QueuedFile[]>([]);
  const [parsing, setParsing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const filesRef = useRef<QueuedFile[]>(files);
  filesRef.current = files;

  const addFiles = useCallback((fileList: FileList) => {
    const arr = Array.from(fileList).filter(
      (f) => /pdf|image\/(png|jpeg|jpg|tiff)/i.test(f.type) || /\.(pdf|png|jpe?g|tiff?)$/i.test(f.name),
    );
    const mapped: QueuedFile[] = arr.map((f) => {
      const isImg = /image/i.test(f.type) || /\.(png|jpe?g|tiff?)$/i.test(f.name);
      return {
        uid: ++uidSeq,
        name: f.name,
        size: (f.size / 1024 / 1024).toFixed(2) + " MB",
        isImg,
        url: isImg ? URL.createObjectURL(f) : null,
        progress: 0,
        status: "queued",
      };
    });
    setFiles((p) => [...p, ...mapped]);
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
  };
  const removeFile = (uid: number) => setFiles((p) => p.filter((f) => f.uid !== uid));
  const clearAll = () => {
    setFiles([]);
    setParsing(false);
  };

  const parseAll = () => {
    if (!files.length || parsing) return;
    setParsing(true);
    setFiles((p) => p.map((f) => ({ ...f, status: "parsing", progress: 0 })));
    const id = setInterval(() => {
      let allDone = true;
      setFiles((p) =>
        p.map((f) => {
          if (f.progress >= 100) return { ...f, status: "done" };
          allDone = false;
          const next = Math.min(100, f.progress + Math.random() * 16 + 6);
          return { ...f, progress: next, status: next >= 100 ? "done" : "parsing" };
        }),
      );
      if (allDone) {
        clearInterval(id);
        setParsing(false);
      }
    }, 280);
  };

  useEffect(
    () => () => {
      filesRef.current.forEach((f) => f.url && URL.revokeObjectURL(f.url));
    },
    [],
  );

  const queued = files.length;
  const done = files.filter((f) => f.status === "done").length;

  return (
    <div className="upload-layout">
      <div
        className={`dropzone ${dragging ? "drag" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setDragging(false);
        }}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg,.tiff,image/*,application/pdf"
          style={{ display: "none" }}
          onChange={(e) => {
            if (e.target.files) addFiles(e.target.files);
            e.target.value = "";
          }}
        />
        <div className="dz-ico">
          <UploadCloud size={30} />
        </div>
        <h3>{dragging ? t("dropActive") : t("dropTitle")}</h3>
        <p>
          {t("dropHintPre")}
          <span style={{ color: "var(--cyan)" }}>{t("dropHintLink")}</span>
          {t("dropHintPost")}
        </p>
        <div className="dz-formats">
          <span>PDF</span>
          <span>JPG</span>
          <span>PNG</span>
          <span>TIFF</span>
          <span>{t("maxSize")}</span>
        </div>
      </div>

      <div className="file-queue">
        <div className="fq-head">
          <h3>
            {t("queue")}{" "}
            {queued ? (
              <span
                style={{
                  color: "var(--fg-dim)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 12,
                  fontWeight: 400,
                }}
              >
                {t("queueProgress", { done, total: queued })}
              </span>
            ) : null}
          </h3>
          {queued > 0 && (
            <button
              className="fq-x"
              title={t("clear")}
              onClick={clearAll}
              style={{ width: "auto", padding: "0 9px", fontFamily: "var(--font-mono)", fontSize: 11 }}
            >
              {t("clear")}
            </button>
          )}
        </div>
        <div className="fq-list">
          {queued === 0 && (
            <div className="fq-empty">
              {t("emptyLine1")}
              <br />
              {t("emptyLine2")}
            </div>
          )}
          {files.map((f) => (
            <div className="fq-item" key={f.uid}>
              <div className={`fq-thumb ${f.isImg ? "" : "pdf"}`}>
                {f.isImg && f.url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={f.url} alt="" />
                ) : (
                  <FileText size={18} />
                )}
              </div>
              <div className="fq-meta">
                <div className="n">{f.name}</div>
                <div className="s">
                  {f.status === "done" ? (
                    <span style={{ color: "var(--ok)" }}>{t("ready")}</span>
                  ) : f.status === "parsing" ? (
                    t("parsingPct", { pct: Math.round(f.progress) })
                  ) : (
                    f.size
                  )}
                </div>
                {(f.status === "parsing" || f.status === "done") && (
                  <div className="fq-bar">
                    <i
                      style={{
                        width: `${f.progress}%`,
                        background: f.status === "done" ? "var(--ok)" : "var(--cyan)",
                      }}
                    />
                  </div>
                )}
              </div>
              {f.status === "done" ? (
                <button className="fq-x" title={t("download")} style={{ color: "var(--cyan)" }}>
                  <Download size={15} />
                </button>
              ) : (
                <button className="fq-x" title={t("remove")} onClick={() => removeFile(f.uid)}>
                  <X size={15} />
                </button>
              )}
            </div>
          ))}
        </div>
        <div className="fq-foot">
          <button className="btn btn-ghost" onClick={() => inputRef.current?.click()}>
            <FilePlus2 size={15} /> {t("add")}
          </button>
          <button className="btn btn-primary" onClick={parseAll} disabled={!queued || parsing}>
            {parsing ? (
              <>
                <RefreshCw size={15} className="spin" /> {t("parsing")}
              </>
            ) : (
              <>
                <Sparkles size={15} /> {t("parse", { count: queued || "" })}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
