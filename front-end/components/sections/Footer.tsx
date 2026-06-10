"use client";

import { FileSpreadsheet } from "lucide-react";
import { useTranslations } from "next-intl";

export default function Footer() {
  const t = useTranslations("landing.footer");

  const columns: { heading: string; links: string[] }[] = [
    { heading: t("product"), links: ["linkFeatures", "linkPricing", "linkApiDocs", "linkChangelog", "linkStatus"] },
    { heading: t("company"), links: ["linkAbout", "linkCareers", "linkBlog", "linkContact"] },
    { heading: t("legal"), links: ["linkPrivacy", "linkTerms", "linkSecurity", "linkSoc2"] },
  ];

  return (
    <footer className="lp-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="brand">
            <span className="glyph">
              <FileSpreadsheet size={16} strokeWidth={2.4} />
            </span>
            <span className="wordmark">TABULA</span>
          </div>
          <p>
            {t.rich("tagline", {
              strong: (chunks) => <span className="serif">{chunks}</span>,
            })}
          </p>
        </div>
        {columns.map((col) => (
          <div key={col.heading} className="footer-col">
            <h4>{col.heading}</h4>
            {col.links.map((key) => (
              <a key={key} href="#">
                {t(key)}
              </a>
            ))}
          </div>
        ))}
      </div>
      <div className="footer-bottom">
        <span>{t("copyright")}</span>
        <span>{t("madeFor")}</span>
      </div>
    </footer>
  );
}
