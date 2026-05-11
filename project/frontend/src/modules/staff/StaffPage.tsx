import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  Clock3,
  LoaderCircle,
  LogIn,
  LogOut,
  MonitorCog,
  ShieldCheck,
  Store,
  UserRound,
} from "lucide-react";
import {
  checkInReservation,
  getStoreReservations,
  type StaffReservation,
} from "../../api";
import { useAuth } from "../../auth/AuthContext";
import { OperationsPlaceholder } from "../ops/OperationsPlaceholder";
import { PageShell } from "../../shell/PageShell";

export function StaffPage() {
  const { authNotice, clearNotice, loginAs, logout, session, sessionStatus, token } = useAuth();
  const [date, setDate] = useState("2026-05-20");
  const [statusFilter, setStatusFilter] = useState("");
  const [reservations, setReservations] = useState<StaffReservation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("店员后台仅服务门店值班人员。");
  const [error, setError] = useState("");

  const isStaff = session?.role === "staff";
  const storeId = session?.storeId ?? "store-shanghai-001";

  useEffect(() => {
    if (!token || !isStaff) {
      setReservations([]);
      return;
    }
    const currentToken = token;

    async function loadReservations() {
      try {
        setIsLoading(true);
        setError("");
        const nextReservations = await getStoreReservations(
          currentToken,
          storeId,
          date,
          statusFilter || undefined,
        );
        setReservations(nextReservations);
        setMessage("已进入店员后台，可以查看今日预约。");
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "店员后台加载失败");
      } finally {
        setIsLoading(false);
      }
    }

    void loadReservations();
  }, [date, isStaff, statusFilter, storeId, token]);

  async function handleEnterStaff() {
    try {
      clearNotice();
      setError("");
      await loginAs("staff");
      setMessage("店员会话已建立。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "进入店员后台失败");
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

  async function handleCheckIn(reservationId: string) {
    if (!token) {
      return;
    }
    try {
      setError("");
      await checkInReservation(token, reservationId);
      const nextReservations = await getStoreReservations(token, storeId, date, statusFilter || undefined);
      setReservations(nextReservations);
      setMessage("店员后台已确认顾客到店。");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "确认到店失败");
    }
  }

  const statusMessage = error || authNotice || message;
  const statusTone = error ? "error" : authNotice ? "neutral" : "ok";

  return (
    <PageShell
      eyebrow="Store Console"
      title="把今天的预约、到店节奏和门店现场处理留在一个干净的后台里。"
      subtitle="店员后台单独进入，不和顾客预约首页混用同一套身份和状态。"
      statusMessage={statusMessage}
      statusTone={statusTone}
      actions={
        isStaff ? (
          <button className="secondary-button" onClick={() => void handleLogout()} type="button">
            <LogOut size={16} />
            <span>退出后台</span>
          </button>
        ) : null
      }
      sidebar={
        <>
          <section className="sidebar-card">
            <div className="section-heading">
              <Store size={18} />
              <span>后台入口</span>
            </div>
            <strong>店员工作台</strong>
            <p>只允许店员会话访问门店预约与到店确认。</p>
            <Link className="text-link" to="/">
              <ArrowLeft size={15} />
              返回顾客首页
            </Link>
          </section>

          <section className="sidebar-card">
            <div className="section-heading">
              <ShieldCheck size={18} />
              <span>当前会话</span>
            </div>
            <strong>{isStaff ? session.displayName : "未进入店员后台"}</strong>
            <p>
              {isStaff
                ? `当前门店：${session.storeId ?? "store-shanghai-001"}`
                : "进入后台后，才能处理今日预约和到店操作。"}
            </p>
            {!isStaff ? (
              <button className="primary-button" onClick={() => void handleEnterStaff()} type="button">
                {sessionStatus === "authenticating" ? <LoaderCircle className="spin" size={18} /> : <LogIn size={18} />}
                <span>进入店员后台</span>
              </button>
            ) : null}
          </section>

          <section className="sidebar-card">
            <div className="section-heading">
              <MonitorCog size={18} />
              <span>后续后台能力</span>
            </div>
            <div className="roadmap-grid">
              <OperationsPlaceholder />
            </div>
          </section>
        </>
      }
    >
      {!isStaff ? (
        <section className="hero-card">
          <div className="section-heading">
            <Store size={20} />
            <h2>店员后台独立进入</h2>
          </div>
          <p>真实门店后台和顾客预约站不是一个壳。这里保留单独入口，进入后再加载门店预约和到店处理。</p>
          <div className="action-row">
            <button className="primary-button" onClick={() => void handleEnterStaff()} type="button">
              <LogIn size={18} />
              <span>以店员身份进入</span>
            </button>
            <Link className="secondary-button nav-button" to="/">
              <UserRound size={18} />
              <span>回到顾客首页</span>
            </Link>
          </div>
        </section>
      ) : (
        <section className="workspace-grid">
          <article className="panel span-two">
            <div className="section-heading">
              <Clock3 size={20} />
              <h2>今日预约</h2>
            </div>
            <div className="form-grid">
              <label>
                营业日期
                <input
                  min="2026-05-20"
                  onChange={(event) => setDate(event.target.value)}
                  type="date"
                  value={date}
                />
              </label>
              <label>
                状态
                <select onChange={(event) => setStatusFilter(event.target.value)} value={statusFilter}>
                  <option value="">全部</option>
                  <option value="BOOKED">已预约</option>
                  <option value="CHECKED_IN">已到店</option>
                  <option value="CANCELLED">已取消</option>
                </select>
              </label>
            </div>
            <div className="staff-list">
              {isLoading ? (
                <div className="empty-state">
                  <LoaderCircle className="spin" size={22} />
                  <span>正在读取今日预约</span>
                </div>
              ) : reservations.length === 0 ? (
                <div className="empty-state">
                  <Clock3 size={22} />
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
                    <div className="card-actions">
                      <span className="status-pill" data-status={reservation.status}>
                        {formatStatus(reservation.status)}
                      </span>
                      {reservation.status === "BOOKED" ? (
                        <button
                          className="secondary-button compact"
                          onClick={() => void handleCheckIn(reservation.reservationId)}
                          type="button"
                        >
                          <LogIn size={16} />
                          <span>确认到店</span>
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

function formatDateTime(value: string) {
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
