import { HeartPulse } from "lucide-react";

export function CatHealthPlaceholder() {
  return (
    <article className="roadmap-card">
      <HeartPulse size={18} />
      <strong>猫咪健康台账</strong>
      <span>下一轮接入猫咪档案、健康打卡与互动限制。</span>
    </article>
  );
}
