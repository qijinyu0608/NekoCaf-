import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  CalendarCheck,
  CircleAlert,
  Clock3,
  Coffee,
  HeartPulse,
  Leaf,
  LoaderCircle,
  LogIn,
  MonitorCog,
  Sparkles,
  Store,
  TicketPercent,
  UserRound,
  X,
} from "lucide-react";
import logoUrl from "./assets/nekocafe-logo.png";
import {
  cancelReservation,
  checkInReservation,
  createReservation,
  getMember,
  getMemberReservations,
  getPoints,
  getSlots,
  getStoreReservations,
  type Member,
  type PointAccount,
  type Reservation,
  type Slot,
  type StaffReservation,
} from "./api";
import "./styles.css";

const memberId = "member-1001";
const storeId = "store-shanghai-001";
type ModuleKey = "customer" | "staff" | "cat" | "ops";
const platformModules = [
  {
    key: "customer",
    label: "顾客预约台",
    status: "已接入",
    description: "会员资料、时段查询、预约创建、取消预约",
  },
  {
    key: "staff",
    label: "店员后台",
    status: "已接入",
    description: "当日预约、到店核销、排台与异常处理",
  },
  {
    key: "cat",
    label: "猫咪健康",
    status: "预留",
    description: "健康打卡、互动限制、异常分流",
  },
  {
    key: "ops",
    label: "运营看板",
    status: "预留",
    description: "门店配置、活动效果、审计日志",
  },
] satisfies Array<{ key: ModuleKey; label: string; status: string; description: string }>;

function App() {
  const [member, setMember] = useState<Member | null>(null);
  const [points, setPoints] = useState<PointAccount | null>(null);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [staffReservations, setStaffReservations] = useState<StaffReservation[]>([]);
  const [activeModule, setActiveModule] = useState<ModuleKey>("customer");
  const [staffStatusFilter, setStaffStatusFilter] = useState("");
  const [selectedSlotId, setSelectedSlotId] = useState("");
  const [date, setDate] = useState("2026-05-20");
  const [partySize, setPartySize] = useState(2);
  const [statusMessage, setStatusMessage] = useState("正在连接 NekoCafé 服务...");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function loadReservations() {
    const nextReservations = await getMemberReservations(memberId);
    setReservations(nextReservations);
  }

  async function loadStaffReservations(nextStatus = staffStatusFilter) {
    const nextReservations = await getStoreReservations(storeId, date, nextStatus || undefined);
    setStaffReservations(nextReservations);
  }

  useEffect(() => {
    async function loadInitialData() {
      try {
        setIsLoading(true);
        setError("");
        const [nextMember, nextPoints, nextSlots, nextReservations, nextStaffReservations] =
          await Promise.all([
          getMember(memberId),
          getPoints(memberId),
          getSlots(storeId, date, partySize),
          getMemberReservations(memberId),
          getStoreReservations(storeId, date),
        ]);
        setMember(nextMember);
        setPoints(nextPoints);
        setSlots(nextSlots);
        setReservations(nextReservations);
        setStaffReservations(nextStaffReservations);
        setSelectedSlotId(nextSlots[0]?.slotId ?? "");
        setStatusMessage("服务已就绪，可以选择时段预约。");
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "服务连接失败");
        setStatusMessage("请确认 member-service 和 reservation-service 已启动。");
      } finally {
        setIsLoading(false);
      }
    }

    void loadInitialData();
  }, []);

  useEffect(() => {
    async function refreshWorkspaceData() {
      try {
        setError("");
        const [nextSlots, nextStaffReservations] = await Promise.all([
          getSlots(storeId, date, partySize),
          getStoreReservations(storeId, date, staffStatusFilter || undefined),
        ]);
        setSlots(nextSlots);
        setStaffReservations(nextStaffReservations);
        setSelectedSlotId(nextSlots[0]?.slotId ?? "");
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "工作台刷新失败");
      }
    }

    void refreshWorkspaceData();
  }, [date, partySize]);

  const selectedSlot = useMemo(
    () => slots.find((slot) => slot.slotId === selectedSlotId),
    [slots, selectedSlotId],
  );

  async function handleCreateReservation() {
    if (!selectedSlot) {
      setError("请先选择一个可预约时段");
      return;
    }

    try {
      setIsSubmitting(true);
      setError("");
      await createReservation({
        memberId,
        storeId,
        slotId: selectedSlot.slotId,
        partySize,
        preferredTheme: selectedSlot.theme,
        catInteractionMode: "gentle",
      });
      await loadReservations();
      await loadStaffReservations();
      setStatusMessage("预约已创建，已同步到我的预约。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "预约创建失败");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCancelReservation(reservationId: string) {
    try {
      setError("");
      await cancelReservation(reservationId);
      await loadReservations();
      await loadStaffReservations();
      setStatusMessage("预约已取消，桌位已释放。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "预约取消失败");
    }
  }

  async function handleCheckIn(reservationId: string) {
    try {
      setError("");
      await checkInReservation(reservationId);
      await loadReservations();
      await loadStaffReservations();
      setStatusMessage("店员后台已确认顾客到店。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "到店确认失败");
    }
  }

  async function handleStaffStatusChange(status: string) {
    try {
      setStaffStatusFilter(status);
      setError("");
      await loadStaffReservations(status);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "店员后台刷新失败");
    }
  }

  return (
    <main className="app-shell">
      <aside className="brand-panel">
        <img className="brand-logo" src={logoUrl} alt="NekoCafé Eat Sip Unwind" />
        <div className="brand-copy">
          <p className="eyebrow">Smart Reservation Platform</p>
          <h1>安静、清楚地订到喜欢的猫咖时段。</h1>
        </div>
        <div className="member-card">
          <div className="card-title">
            <UserRound size={18} />
            <span>会员状态</span>
          </div>
          {member ? (
            <>
              <strong>{member.nickname}</strong>
              <span>{member.mobileMasked}</span>
              <div className="badge-row">
                <span className="badge">{member.loyaltyLevel}</span>
                <span className="badge">{points?.currentPoints ?? 0} 积分</span>
              </div>
            </>
          ) : (
            <span>等待会员服务返回...</span>
          )}
        </div>
        <nav className="module-nav" aria-label="NekoCafé 平台模块">
          <div className="card-title">
            <MonitorCog size={18} />
            <span>平台模块</span>
          </div>
          {platformModules.map((module) => (
            <button
              className="module-item"
              data-active={module.key === activeModule}
              key={module.label}
              onClick={() => setActiveModule(module.key)}
              type="button"
            >
              <span>
                <strong>{module.label}</strong>
                <small>{module.description}</small>
              </span>
              <em>{module.status}</em>
            </button>
          ))}
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Store Shanghai 001</p>
            <h2>{platformModules.find((module) => module.key === activeModule)?.label}</h2>
          </div>
          <div className="service-state" data-state={error ? "error" : "ok"}>
            {error ? <CircleAlert size={18} /> : <Leaf size={18} />}
            <span>{error || statusMessage}</span>
          </div>
        </header>

        {activeModule === "customer" && (
          <CustomerWorkspace
            date={date}
            isLoading={isLoading}
            isSubmitting={isSubmitting}
            onCancelReservation={handleCancelReservation}
            onCreateReservation={handleCreateReservation}
            onDateChange={setDate}
            onPartySizeChange={setPartySize}
            onSelectSlot={setSelectedSlotId}
            partySize={partySize}
            reservations={reservations}
            selectedSlot={selectedSlot}
            selectedSlotId={selectedSlotId}
            slots={slots}
          />
        )}

        {activeModule === "staff" && (
          <StaffWorkspace
            date={date}
            onCheckIn={handleCheckIn}
            onDateChange={setDate}
            onStatusChange={handleStaffStatusChange}
            reservations={staffReservations}
            statusFilter={staffStatusFilter}
          />
        )}

        {(activeModule === "cat" || activeModule === "ops") && (
          <ReservedModule moduleKey={activeModule} />
        )}
      </section>
    </main>
  );
}

type CustomerWorkspaceProps = {
  date: string;
  isLoading: boolean;
  isSubmitting: boolean;
  onCancelReservation: (reservationId: string) => void;
  onCreateReservation: () => void;
  onDateChange: (date: string) => void;
  onPartySizeChange: (partySize: number) => void;
  onSelectSlot: (slotId: string) => void;
  partySize: number;
  reservations: Reservation[];
  selectedSlot: Slot | undefined;
  selectedSlotId: string;
  slots: Slot[];
};

function CustomerWorkspace({
  date,
  isLoading,
  isSubmitting,
  onCancelReservation,
  onCreateReservation,
  onDateChange,
  onPartySizeChange,
  onSelectSlot,
  partySize,
  reservations,
  selectedSlot,
  selectedSlotId,
  slots,
}: CustomerWorkspaceProps) {
  return (
    <section className="booking-grid">
          <div className="booking-panel">
            <div className="section-heading">
              <CalendarCheck size={20} />
              <h3>选择到店信息</h3>
            </div>
            <div className="form-grid">
              <label>
                日期
                <input
                  type="date"
                  value={date}
                  min="2026-05-20"
                  onChange={(event) => onDateChange(event.target.value)}
                />
              </label>
              <label>
                人数
                <input
                  type="number"
                  value={partySize}
                  min={1}
                  max={6}
                  onChange={(event) => onPartySizeChange(Number(event.target.value))}
                />
              </label>
            </div>

            <div className="slot-list" aria-label="可预约时段">
              {isLoading ? (
                <div className="empty-state">
                  <LoaderCircle className="spin" size={24} />
                  <span>正在读取可预约时段</span>
                </div>
              ) : slots.length === 0 ? (
                <div className="empty-state">
                  <Coffee size={24} />
                  <span>当前日期暂无合适时段</span>
                </div>
              ) : (
                slots.map((slot) => (
                  <button
                    key={slot.slotId}
                    className="slot-card"
                    data-selected={slot.slotId === selectedSlotId}
                    onClick={() => onSelectSlot(slot.slotId)}
                    type="button"
                  >
                    <span className="slot-time">{formatTime(slot.startAt)}</span>
                    <span>{formatTheme(slot.theme)}</span>
                    <small>可容纳 {slot.capacity} 人</small>
                  </button>
                ))
              )}
            </div>

            <button
              className="primary-action"
              disabled={!selectedSlot || isSubmitting}
              onClick={onCreateReservation}
              type="button"
            >
              {isSubmitting ? <LoaderCircle className="spin" size={18} /> : <CalendarCheck size={18} />}
              <span>{isSubmitting ? "正在预约" : "确认预约"}</span>
            </button>
          </div>

          <div className="reservation-panel">
            <div className="section-heading">
              <Clock3 size={20} />
              <h3>我的预约</h3>
            </div>
            <div className="reservation-list">
              {reservations.length === 0 ? (
                <div className="empty-state">
                  <TicketPercent size={24} />
                  <span>还没有预约记录</span>
                </div>
              ) : (
                reservations.map((reservation) => (
                  <article className="reservation-card" key={reservation.reservationId}>
                    <div>
                      <strong>{formatDateTime(reservation.slotStartAt)}</strong>
                      <span>{reservation.storeId}</span>
                      <small>
                        {reservation.partySize} 人 · {reservation.tableCode ?? "待分配桌位"}
                      </small>
                    </div>
                    <div className="reservation-actions">
                      <span className="status-pill" data-status={reservation.status}>
                        {reservation.status === "BOOKED" ? "已预约" : "已取消"}
                      </span>
                      {reservation.status === "BOOKED" && (
                        <button
                          className="icon-action"
                          aria-label={`取消预约 ${reservation.reservationId}`}
                          onClick={() => onCancelReservation(reservation.reservationId)}
                          type="button"
                        >
                          <X size={16} />
                        </button>
                      )}
                    </div>
                  </article>
                ))
              )}
            </div>
          </div>

          <div className="system-panel">
            <div className="section-heading">
              <Store size={20} />
              <h3>后续后台能力</h3>
            </div>
            <div className="capability-grid">
              <article>
                <Store size={18} />
                <strong>店员工作台</strong>
                <span>查看今日预约、到店确认、排台、迟到/爽约处理。</span>
              </article>
              <article>
                <HeartPulse size={18} />
                <strong>猫咪健康台账</strong>
                <span>健康打卡、互动限制、异常指标和人工复核流。</span>
              </article>
              <article>
                <Sparkles size={18} />
                <strong>推荐与权益</strong>
                <span>AI 推荐、优惠券领取、积分消耗和支付评价链路。</span>
              </article>
            </div>
          </div>
        </section>
  );
}

type StaffWorkspaceProps = {
  date: string;
  onCheckIn: (reservationId: string) => void;
  onDateChange: (date: string) => void;
  onStatusChange: (status: string) => void;
  reservations: StaffReservation[];
  statusFilter: string;
};

function StaffWorkspace({
  date,
  onCheckIn,
  onDateChange,
  onStatusChange,
  reservations,
  statusFilter,
}: StaffWorkspaceProps) {
  return (
    <section className="staff-grid">
      <div className="booking-panel">
        <div className="section-heading">
          <Store size={20} />
          <h3>今日预约</h3>
        </div>
        <div className="form-grid">
          <label>
            营业日期
            <input
              type="date"
              value={date}
              min="2026-05-20"
              onChange={(event) => onDateChange(event.target.value)}
            />
          </label>
          <label>
            状态
            <select value={statusFilter} onChange={(event) => onStatusChange(event.target.value)}>
              <option value="">全部</option>
              <option value="BOOKED">已预约</option>
              <option value="CHECKED_IN">已到店</option>
              <option value="CANCELLED">已取消</option>
            </select>
          </label>
        </div>
        <div className="staff-list">
          {reservations.length === 0 ? (
            <div className="empty-state">
              <Clock3 size={24} />
              <span>当前筛选下暂无预约</span>
            </div>
          ) : (
            reservations.map((reservation) => (
              <article className="staff-card" key={reservation.reservationId}>
                <div>
                  <strong>{formatDateTime(reservation.slotStartAt)}</strong>
                  <span>{reservation.memberNickname}</span>
                  <small>
                    {reservation.partySize} 人 · {reservation.tableCode}
                  </small>
                </div>
                <div className="reservation-actions">
                  <span className="status-pill" data-status={reservation.status}>
                    {formatStatus(reservation.status)}
                  </span>
                  {reservation.status === "BOOKED" && (
                    <button
                      className="secondary-action"
                      onClick={() => onCheckIn(reservation.reservationId)}
                      type="button"
                    >
                      <LogIn size={16} />
                      <span>确认到店</span>
                    </button>
                  )}
                </div>
              </article>
            ))
          )}
        </div>
      </div>
      <div className="system-panel">
        <div className="section-heading">
          <MonitorCog size={20} />
          <h3>后台后续动作</h3>
        </div>
        <div className="capability-grid">
          <article>
            <Store size={18} />
            <strong>排台与改台</strong>
            <span>下一步接入桌位资源状态，支持临时换台和冲突提示。</span>
          </article>
          <article>
            <CircleAlert size={18} />
            <strong>迟到/爽约处理</strong>
            <span>补充异常状态和颜色规则，支撑店员快速识别。</span>
          </article>
          <article>
            <Clock3 size={18} />
            <strong>离店与完单</strong>
            <span>后续衔接订单核销、积分累计和运营统计。</span>
          </article>
        </div>
      </div>
    </section>
  );
}

function ReservedModule({ moduleKey }: { moduleKey: "cat" | "ops" }) {
  const isCat = moduleKey === "cat";
  return (
    <section className="system-panel">
      <div className="section-heading">
        {isCat ? <HeartPulse size={20} /> : <MonitorCog size={20} />}
        <h3>{isCat ? "猫咪健康" : "运营看板"}</h3>
      </div>
      <div className="empty-state">
        <span>{isCat ? "健康打卡、互动限制和异常分流将在 V3 接入。" : "门店配置、活动效果和审计日志将在 V3 接入。"}</span>
      </div>
    </section>
  );
}

function formatTheme(theme: string) {
  return theme
    .split("-")
    .map((part) => part[0]?.toUpperCase() + part.slice(1))
    .join(" ");
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function formatDateTime(value?: string) {
  if (!value) {
    return "待确认时段";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function formatStatus(status: string) {
  const labels: Record<string, string> = {
    BOOKED: "已预约",
    CHECKED_IN: "已到店",
    CANCELLED: "已取消",
  };
  return labels[status] ?? status;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
