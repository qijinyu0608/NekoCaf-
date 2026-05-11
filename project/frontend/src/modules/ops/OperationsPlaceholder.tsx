import { MonitorCog } from "lucide-react";

export function OperationsPlaceholder() {
  return (
    <article className="roadmap-card">
      <MonitorCog size={18} />
      <strong>运营看板</strong>
      <span>后续接营业日历、桌位配置、预约漏斗和审计台账。</span>
    </article>
  );
}
