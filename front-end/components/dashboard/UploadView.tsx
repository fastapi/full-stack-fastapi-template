"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Download, FilePlus2, FileText, RefreshCw, Sparkles, UploadCloud, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { apiMessage } from "@/lib/api";
import { FilesService } from "@/lib/client";
import { downloadExport, jobProgress, jobStatus } from "@/lib/files";

type FileStatus = "queued" | "uploading" | "parsing" | "done" | "error";

interface QueuedFile {
  uid: number;
  file: File;
  name: string;
  size: string;
  isImg: boolean;
  url: string | null;
  progress: number;
  status: FileStatus;
  fileId?: string;
  error?: string;
}

const POLL_INTERVAL_MS = 2500;

let uidSeq = 0;

export default function UploadView() {
  const t = useTranslations("upload");
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState<QueuedFile[]>([]);
  const [parsing, setParsing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const filesRef = useRef<QueuedFile[]>(files);
  filesRef.current = files;
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      filesRef.current.forEach((f) => f.url && URL.revokeObjectURL(f.url));
    };
  }, []);

  const addFiles = useCallback((fileList: FileList) => {
    const arr = Array.from(fileList).filter(
      (f) => /pdf|image\/(png|jpeg|jpg|tiff)/i.test(f.type) || /\.(pdf|png|jpe?g|tiff?)$/i.test(f.name),
    );
    const mapped: QueuedFile[] = arr.map((f) => {
      const isImg = /image/i.test(f.type) || /\.(png|jpe?g|tiff?)$/i.test(f.name);
      return {
        uid: ++uidSeq,
        file: f,
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

  const patch = (uid: number, updates: Partial<QueuedFile>) =>
    setFiles((p) => p.map((f) => (f.uid === uid ? { ...f, ...updates } : f)));

  /** Polls the batch status endpoint until every uploaded file finishes or fails. */
  const pollJobs = useCallback(async () => {
    for (;;) {
      await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
      if (!mountedRef.current) return;

      const pending = filesRef.current.filter((f) => f.status === "parsing" && f.fileId);
      if (pending.length === 0) return;

      try {
        const jobs = await FilesService.getFilesBatchStatus({
          requestBody: { file_ids: pending.map((f) => f.fileId!) },
        });
        if (!mountedRef.current) return;
        setFiles((p) =>
          p.map((f) => {
            const job = jobs.find((j) => j.file_id === f.fileId);
            if (!job || f.status !== "parsing") return f;
            const status = jobStatus(job);
            if (status === "done") return { ...f, status: "done", progress: 100 };
            if (status === "fail") return { ...f, status: "error", error: job.err_msg ?? undefined };
            return { ...f, progress: jobProgress(job) ?? Math.min(95, f.progress + 5) };
          }),
        );
      } catch {
        // transient polling error — keep trying on the next tick
      }
    }
  }, []);

  const parseAll = async () => {
    const queued = filesRef.current.filter((f) => f.status === "queued");
    if (!queued.length || parsing) return;
    setParsing(true);

    await Promise.all(
      queued.map(async (f) => {
        patch(f.uid, { status: "uploading", progress: 0 });
        try {
          const uploaded = await FilesService.uploadFileEndpoint({ formData: { file: f.file } });
          patch(f.uid, { status: "parsing", fileId: uploaded.id, progress: 5 });
        } catch (err) {
          patch(f.uid, { status: "error", error: apiMessage(err) });
        }
      }),
    );

    await pollJobs();
    if (mountedRef.current) setParsing(false);
  };

  const queued = files.length;
  const done = files.filter((f) => f.status === "done").length;
  const parsable = files.filter((f) => f.status === "queued").length;

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
                  ) : f.status === "error" ? (
                    <span style={{ color: "var(--bad)" }}>
                      {f.error ?? t("failed")}
                    </span>
                  ) : f.status === "uploading" ? (
                    t("uploading")
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
              {f.status === "done" && f.fileId ? (
                <button
                  className="fq-x"
                  title={t("download")}
                  style={{ color: "var(--cyan)" }}
                  onClick={() => void downloadExport(f.fileId!, f.name, "xlsx").catch(() => {})}
                >
                  <Download size={15} />
                </button>
              ) : f.status === "queued" || f.status === "error" ? (
                <button className="fq-x" title={t("remove")} onClick={() => removeFile(f.uid)}>
                  <X size={15} />
                </button>
              ) : null}
            </div>
          ))}
        </div>
        <div className="fq-foot">
          <button className="btn btn-ghost" onClick={() => inputRef.current?.click()}>
            <FilePlus2 size={15} /> {t("add")}
          </button>
          <button className="btn btn-primary" onClick={() => void parseAll()} disabled={!parsable || parsing}>
            {parsing ? (
              <>
                <RefreshCw size={15} className="spin" /> {t("parsing")}
              </>
            ) : (
              <>
                <Sparkles size={15} /> {t("parse", { count: parsable || "" })}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
