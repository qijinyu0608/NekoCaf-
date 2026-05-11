import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  CalendarCheck,
  Clock3,
  Coffee,
  Leaf,
  LoaderCircle,
  LogOut,
  ShieldCheck,
  Sparkles,
  Store,
  TicketPercent,
  UserRound,
  X,
} from "lucide-react";
import {
  cancelReservation,
  createMyReservation,
  getCurrentMember,
  getCurrentPoints,
  getMyReservations,
  getSlots,
  type CustomerReservation,
  type Member,
  type PointAccount,
  type Slot,
} from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { CatHealthPlaceholder } from "../cat/CatHealthPlaceholder";
import { OperationsPlaceholder } from "../ops/OperationsPlaceholder";
import { PageShell } from "../../shell/PageShell";

const storeId = "store-shanghai-001";

export function CustomerPage() {
  const { authNotice, clearNotice, loginAs, logout, session, sessionStatus, token } = useAuth();
  const [member, setMember] = useState<Member | null>(null);
  const [points, setPoints] = useState<PointAccount | null>(null);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [reservations, setReservations] = useState<CustomerReservation[]>([]);
  const [date, setDate] = useState("2026-05-20");
  const [partySize, setPartySize] = useState(2);
  const [selectedSlotId, setSelectedSlotId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("以顾客身份进入后，可以继续完成预约。");
  const [error, setError] = useState("");

  const isCustomer = session?.role === "customer";
  const selectedSlot = useMemo(
    () => slots.find((slot) => slot.slotId === selectedSlotId),
    [selectedSlotId, slots],
  );

  useEffect(() => {
    if (!token || !isCustomer) {
      setMember(null);
      setPoints(null);
      setSlots([]);
      setReservations([]);
      return;
    }
    const currentToken = token;

    async function loadWorkspace() {
      try {
        setIsLoading(true);
        setError("");
        const [nextMember, nextPoints, nextSlots, nextReservations] = await Promise.all([
          getCurrentMember(currentToken),
          getCurrentPoints(currentToken),
          getSlots(storeId, date, partySize, currentToken),
          getMyReservations(currentToken),
        ]);
        setMember(nextMember);
        setPoints(nextPoints);
        setSlots(nextSlots);
        setReservations(nextReservations);
        setSelectedSlotId(nextSlots[0]?.slotId ?? "");
        setMessage("已进入顾客预约工作区，可以继续选择时段。");
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "顾客工作区加载失败");
      } finally {
        setIsLoading(false);
      }
    }

    void loadWorkspace();
  }, [date, isCustomer, partySize, token]);

  async function handleEnterCustomer() {
    try {
      setError("");
      clearNotice();
      await loginAs("customer");
      setMessage("顾客会话已建立。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "进入顾客预约失败");
    }
  }

  async function handleLogout() {
    try {
      setError("");
      await logout();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "退出会话失败");
    }
  }

  async function handleCreateReservation() {
    if (!token || !selectedSlot) {
      setError("请先进入顾客会话并选择预约时段。");
      return;
    }

    try {
      setIsSubmitting(true);
      setError("");
      await createMyReservation(token, {
        storeId,
        slotId: selectedSlot.slotId,
        partySize,
        preferredTheme: selectedSlot.theme,
        catInteractionMode: "gentle",
      });
      const nextReservations = await getMyReservations(token);
      setReservations(nextReservations);
      setMessage("预约已创建，已同步到我的预约。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "创建预约失败");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCancelReservation(reservationId: string) {
    if (!token) {
      return;
    }
    try {
      setError("");
      await cancelReservation(token, reservationId);
      const nextReservations = await getMyReservations(token);
      setReservations(nextReservations);
      setMessage("预约已取消。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "取消预约失败");
    }
  }

  const statusMessage = error || authNotice || message;
  const statusTone = error ? "error" : authNotice ? "neutral" : "ok";

  return (
    <PageShell
      eyebrow="Guest Reservation"
      title="用一张安静的预约首页，把咖啡、猫咪和到店节奏安排好。"
      subtitle="首页只服务顾客预约，店员后台单独进入，像真实餐饮系统那样把身份和工作区分开。"
      statusMessage={statusMessage}
      statusTone={statusTone}
      actions={
        isCustomer ? (
          <button className="secondary-button" onClick={() => void handleLogout()} type="button">
            <LogOut size={16} />
            <span>退出会话</span>
          </button>
        ) : null
      }
      sidebar={
        <>
          <section className="sidebar-card">
            <div className="section-heading">
              <UserRound size={18} />
              <span>当前入口</span>
            </div>
            <strong>顾客预约首页</strong>
            <p>面向顾客，只处理我的资料、我的预约和继续预约。</p>
            <Link className="text-link" to="/staff">
              店员后台入口
              <ArrowRight size={15} />
            </Link>
          </section>

          <section className="sidebar-card">
            <div className="section-heading">
              <ShieldCheck size={18} />
              <span>会话状态</span>
            </div>
            <strong>{sessionStatus === "authenticated" && isCustomer ? session.displayName : "未进入顾客会话"}</strong>
            <p>
              {sessionStatus === "expired"
                ? "上次会话已过期。"
                : isCustomer
                  ? "当前身份仅可访问自己的资料与预约。"
                  : "点击继续预约后，以顾客身份进入工作区。"}
            </p>
            {!isCustomer ? (
              <button className="primary-button" onClick={() => void handleEnterCustomer()} type="button">
                {sessionStatus === "authenticating" ? <LoaderCircle className="spin" size={18} /> : <CalendarCheck size={18} />}
                <span>继续预约</span>
              </button>
            ) : null}
          </section>

          <section className="sidebar-card">
            <div className="section-heading">
              <Sparkles size={18} />
              <span>后续模块</span>
            </div>
            <div className="roadmap-grid">
              <CatHealthPlaceholder />
              <OperationsPlaceholder />
            </div>
          </section>
        </>
      }
    >
      {!isCustomer ? (
        <section className="hero-card">
          <div className="section-heading">
            <Coffee size={20} />
            <h2>先确认顾客身份，再继续预约</h2>
          </div>
          <p>
            真实门店预约站不会把顾客预约和店员操作揉在一起。这里先进入顾客会话，再读取会员资料、积分和我的预约。
          </p>
          <div className="action-row">
            <button className="primary-button" onClick={() => void handleEnterCustomer()} type="button">
              <CalendarCheck size={18} />
              <span>以顾客身份进入</span>
            </button>
            <Link className="secondary-button nav-button" to="/staff">
              <Store size={18} />
              <span>前往店员后台</span>
            </Link>
          </div>
        </section>
      ) : (
        <section className="workspace-grid">
          <article className="panel">
            <div className="section-heading">
              <UserRound size={20} />
              <h2>会员摘要</h2>
            </div>
            <div className="summary-grid">
              <div className="summary-item">
                <span>昵称</span>
                <strong>{member?.nickname ?? "..."}</strong>
              </div>
              <div className="summary-item">
                <span>手机</span>
                <strong>{member?.mobileMasked ?? "..."}</strong>
              </div>
              <div className="summary-item">
                <span>等级</span>
                <strong>{member?.loyaltyLevel ?? "..."}</strong>
              </div>
              <div className="summary-item">
                <span>积分</span>
                <strong>{points?.currentPoints ?? 0}</strong>
              </div>
            </div>
          </article>

          <article className="panel">
            <div className="section-heading">
              <CalendarCheck size={20} />
              <h2>选择预约时段</h2>
            </div>
            <div className="form-grid">
              <label>
                日期
                <input
                  min="2026-05-20"
                  onChange={(event) => setDate(event.target.value)}
                  type="date"
                  value={date}
                />
              </label>
              <label>
                人数
                <input
                  max={6}
                  min={1}
                  onChange={(event) => setPartySize(Number(event.target.value))}
                  type="number"
                  value={partySize}
                />
              </label>
            </div>
            <div className="slot-grid">
              {isLoading ? (
                <div className="empty-state">
                  <LoaderCircle className="spin" size={22} />
                  <span>正在读取可预约时段</span>
                </div>
              ) : slots.length === 0 ? (
                <div className="empty-state">
                  <Leaf size={22} />
                  <span>当前日期暂无合适时段</span>
                </div>
              ) : (
                slots.map((slot) => (
                  <button
                    className="slot-card"
                    data-selected={slot.slotId === selectedSlotId}
                    key={slot.slotId}
                    onClick={() => setSelectedSlotId(slot.slotId)}
                    type="button"
                  >
                    <strong>{formatTime(slot.startAt)}</strong>
                    <span>{formatTheme(slot.theme)}</span>
                    <small>适合 {slot.capacity} 人</small>
                  </button>
                ))
              )}
            </div>
            <button
              className="primary-button"
              disabled={!selectedSlot || isSubmitting}
              onClick={() => void handleCreateReservation()}
              type="button"
            >
              {isSubmitting ? <LoaderCircle className="spin" size={18} /> : <CalendarCheck size={18} />}
              <span>{isSubmitting ? "正在创建预约" : "确认预约"}</span>
            </button>
          </article>

          <article className="panel span-two">
            <div className="section-heading">
              <Clock3 size={20} />
              <h2>我的预约</h2>
            </div>
            <div className="reservation-list">
              {reservations.length === 0 ? (
                <div className="empty-state">
                  <TicketPercent size={22} />
                  <span>你还没有预约记录</span>
                </div>
              ) : (
                reservations.map((reservation) => (
                  <article className="reservation-card" key={reservation.reservationId}>
                    <div>
                      <strong>{formatDateTime(reservation.slotStartAt)}</strong>
                      <span>{formatTheme(reservation.theme)}</span>
                      <small>
                        {reservation.partySize} 人 · {formatStatus(reservation.status)}
                      </small>
                    </div>
                    <div className="card-actions">
                      <span className="status-pill" data-status={reservation.status}>
                        {formatStatus(reservation.status)}
                      </span>
                      {reservation.status === "BOOKED" ? (
                        <button
                          aria-label={`取消预约 ${reservation.reservationId}`}
                          className="icon-button"
                          onClick={() => void handleCancelReservation(reservation.reservationId)}
                          type="button"
                        >
                          <X size={16} />
                        </button>
                      ) : null}
                    </div>
                  </article>
                ))
              )}
            </div>
          </article>
        </section>
      )}
    </PageShell>
  );
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

function formatTheme(theme: string) {
  return theme
    .split("-")
    .map((part) => part[0]?.toUpperCase() + part.slice(1))
    .join(" ");
}

function formatStatus(status: string) {
  const labels: Record<string, string> = {
    BOOKED: "已预约",
    CHECKED_IN: "已到店",
    CANCELLED: "已取消",
  };
  return labels[status] ?? status;
}
