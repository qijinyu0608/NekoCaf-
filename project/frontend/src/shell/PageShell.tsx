import type { PropsWithChildren, ReactNode } from "react";
import logoUrl from "../assets/nekocafe-logo.png";

type PageShellProps = PropsWithChildren<{
  eyebrow: string;
  title: string;
  subtitle: string;
  sidebar: ReactNode;
  statusTone: "ok" | "error" | "neutral";
  statusMessage: string;
  actions?: ReactNode;
}>;

export function PageShell({
  eyebrow,
  title,
  subtitle,
  sidebar,
  statusTone,
  statusMessage,
  actions,
  children,
}: PageShellProps) {
  return (
    <main className="page-shell">
      <aside className="sidebar-shell">
        <div className="brand-lockup">
          <img className="brand-logo" src={logoUrl} alt="NekoCafe Eat Sip Unwind" />
          <div className="brand-copy">
            <p className="eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
            <p className="brand-subtitle">{subtitle}</p>
          </div>
        </div>
        <div className="sidebar-stack">{sidebar}</div>
      </aside>

      <section className="workspace-shell">
        <header className="workspace-topbar">
          <div className={`status-banner ${statusTone}`}>
            <span>{statusMessage}</span>
          </div>
          {actions ? <div className="top-actions">{actions}</div> : null}
        </header>
        {children}
      </section>
    </main>
  );
}
